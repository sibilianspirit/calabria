"""FB Daily Auto-Publisher – publikuje jedną losową polską stronę bestofcalabria.com na Facebooku.

Przebieg:
  1. skanuje content/pl/**/*.html i odrzuca strony techniczne,
  2. odfiltrowuje strony już opublikowane (.fb-published.json),
  3. losuje jedną, generuje tekst posta przez OpenAI (Responses API),
  4. publikuje przez Graph API (message + link – podgląd bierze się z Open Graph),
  5. dopisuje wpis do .fb-published.json i commituje.

Zmienne środowiskowe:
  FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID, OPENAI_API_KEY – wymagane do realnej publikacji
  OPENAI_MODEL       – domyślnie gpt-5.4
  DRY_RUN=true       – bez publikacji i bez commitu (wypisuje wybraną stronę i tekst)
  PICK=<ścieżka>     – wymuś konkretną stronę (np. kierunki/tropea/_index.html) zamiast losowania
  GITHUB_TOKEN, GITHUB_REPOSITORY – do założenia Issue po wyczerpaniu puli
"""
from __future__ import annotations

import html
import json
import os
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import frontmatter
import requests

BASE_URL = "https://bestofcalabria.com"
CONTENT_DIR = Path("content/pl")
TRACKING_FILE = Path(".fb-published.json")
UTILITY_DIRS = {"kontakt", "o-nas", "wspolpraca"}
MIN_BODY_CHARS = 1500
FB_API_VERSION = "v21.0"
OPENAI_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5.4"

SYSTEM_PROMPT = (
    "Jesteś redaktorem social media portalu bestofcalabria.com o podróżach po Kalabrii. "
    "Piszesz krótkie, konkretne posty na Facebook po polsku. Styl: ciepły, rzeczowy, bez clickbaitu "
    "i bez przesadnych emocji. Używasz półpauzy (–), nie pauzy (—)."
)

USER_PROMPT = """Napisz post na Facebook (2–3 zdania, maks. 300 znaków bez hashtagów) do linku:
Tytuł: {title}
Meta opis: {description}
Fragment treści:
{excerpt}

Zasady:
- po polsku, naturalnie; zacznij od konkretu (fakt, liczba, obraz), nie od pytania retorycznego
- maks. 1 emoji, opcjonalnie, pasujące tematycznie
- na końcu, w nowej linii, 2–3 hashtagi: #Kalabria + 1–2 tematyczne (np. #Tropea, #Włochy, #plaże)
- BEZ zwrotów "Sprawdź", "Kliknij", "Odkryj teraz", "Zobacz więcej" – to spam
- nie wklejaj linku, nie dodawaj cudzysłowów ani komentarza od siebie

Zwróć wyłącznie tekst posta."""


# ---------------------------------------------------------------------------
# Kandydaci
# ---------------------------------------------------------------------------
def strip_html(text: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_page(path: Path) -> tuple[dict, str]:
    post = frontmatter.load(str(path))
    return dict(post.metadata), post.content


def is_technical(rel: Path) -> bool:
    if str(rel) == "_index.html":
        return True
    if rel.parts[0] in UTILITY_DIRS:
        return True
    if len(rel.parts) == 2 and rel.name == "_index.html":
        return True
    return False


def scan_candidates(content_dir: Path = CONTENT_DIR) -> Iterable[dict]:
    for path in sorted(content_dir.rglob("*.html")):
        rel = path.relative_to(content_dir)
        if is_technical(rel):
            continue
        try:
            fm, body = parse_page(path)
        except Exception as exc:  # uszkodzony frontmatter – pomijamy, nie wywalamy runa
            print(f"[warn] {rel}: {exc}", file=sys.stderr)
            continue
        if not fm.get("title") or not fm.get("description"):
            continue
        text = strip_html(body)
        if len(text) < MIN_BODY_CHARS:
            continue
        yield {
            "path": rel.as_posix(),
            "title": str(fm["title"]),
            "description": html.unescape(str(fm["description"])),
            "body": text,
        }


def url_for(rel_path: str) -> str:
    p = rel_path.replace("_index.html", "").replace("index.html", "")
    p = p.strip("/")
    return f"{BASE_URL}/pl/{p}/" if p else f"{BASE_URL}/pl/"


# ---------------------------------------------------------------------------
# Tracking
# ---------------------------------------------------------------------------
def load_tracking(path: Path = TRACKING_FILE) -> dict:
    if not path.exists():
        return {"posts": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("posts", [])
    return data


def save_tracking(tracking: dict, path: Path = TRACKING_FILE) -> None:
    path.write_text(json.dumps(tracking, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def is_published(tracking: dict, rel_path: str) -> bool:
    return any(p.get("path") == rel_path for p in tracking["posts"])


def record(tracking: dict, rel_path: str, url: str, fb_post_id: str, message: str) -> None:
    tracking["posts"].append(
        {
            "path": rel_path,
            "url": url,
            "published_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "fb_post_id": fb_post_id,
            "message": message,
        }
    )


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------
def _with_retry(fn, attempts: int = 3, delays=(2, 4, 10)):
    last: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else 0
            if 400 <= status < 500 and status != 429:
                raise
            last = exc
        except (requests.ConnectionError, requests.Timeout) as exc:
            last = exc
        if i < attempts - 1:
            time.sleep(delays[min(i, len(delays) - 1)])
    assert last is not None
    raise last


def generate_fb_text(title: str, description: str, body: str, *, model: str | None = None) -> str:
    api_key = os.environ["OPENAI_API_KEY"]
    model = model or os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    payload = {
        "model": model,
        "reasoning": {"effort": "low"},
        "max_output_tokens": 400,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT.format(title=title, description=description, excerpt=body[:1200]),
            },
        ],
    }

    def call():
        r = requests.post(
            OPENAI_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("error"):
            raise RuntimeError(data["error"])
        text = "".join(
            c.get("text", "")
            for o in data.get("output", [])
            if o.get("type") == "message"
            for c in o.get("content", [])
        )
        return clean_message(text)

    return _with_retry(call)


def clean_message(text: str) -> str:
    text = text.strip().strip('"').strip("„”").strip()
    text = text.replace("—", "–")
    text = re.sub(r"https?://\S+", "", text)  # link dokładamy osobno
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if not text:
        raise RuntimeError("OpenAI zwróciło pusty tekst")
    return text.strip()


# ---------------------------------------------------------------------------
# Facebook
# ---------------------------------------------------------------------------
def publish_to_fb(message: str, link: str) -> str:
    page_id = os.environ["FB_PAGE_ID"]
    token = os.environ["FB_PAGE_ACCESS_TOKEN"]

    def call():
        r = requests.post(
            f"https://graph.facebook.com/{FB_API_VERSION}/{page_id}/feed",
            data={"message": message, "link": link, "access_token": token},
            timeout=30,
        )
        if r.status_code >= 400:
            try:
                err = r.json().get("error", {})
            except ValueError:
                err = {}
            print(f"[fb] HTTP {r.status_code}: {err.get('type')} {err.get('code')} – {err.get('message')}", file=sys.stderr)
            if err.get("code") == 190:  # invalid/expired token
                raise SystemExit("Facebook token nieważny (code 190) – wygeneruj nowy wg docs/FB_SETUP.md")
        r.raise_for_status()
        return r.json()["id"]

    return _with_retry(call)


# ---------------------------------------------------------------------------
# GitHub Issue po wyczerpaniu puli
# ---------------------------------------------------------------------------
def notify_exhausted() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print("[warn] brak GITHUB_TOKEN/GITHUB_REPOSITORY – pomijam Issue", file=sys.stderr)
        return
    requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        json={
            "title": "FB publisher: pula treści wyczerpana",
            "body": (
                "Workflow `fb-daily-post` opublikował już wszystkie kwalifikujące się strony z `content/pl/`.\n\n"
                "Co zrobić: dodać nowe treści albo wyczyścić `.fb-published.json` (`{\"posts\": []}`), "
                "żeby zacząć cykl od nowa."
            ),
            "labels": ["fb-publisher", "automation"],
        },
        timeout=15,
    )


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------
def git_commit_and_push(msg: str) -> None:
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", str(TRACKING_FILE)], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)
    for _ in range(3):
        if subprocess.run(["git", "push"]).returncode == 0:
            return
        subprocess.run(["git", "pull", "--rebase"], check=True)
    raise RuntimeError("git push nie powiódł się po 3 próbach")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def choose(remaining: list[dict]) -> dict:
    forced = os.environ.get("PICK")
    if forced:
        for c in remaining:
            if c["path"] == forced:
                return c
        raise SystemExit(f"PICK={forced} nie ma wśród dostępnych kandydatów")
    return random.choice(remaining)


def main() -> int:
    dry_run = os.environ.get("DRY_RUN", "").lower() == "true"
    candidates = list(scan_candidates())
    tracking = load_tracking()
    remaining = [c for c in candidates if not is_published(tracking, c["path"])]
    print(f"Kandydatów: {len(candidates)}, opublikowanych: {len(candidates) - len(remaining)}, zostało: {len(remaining)}")

    if not remaining:
        notify_exhausted()
        print("Pula wyczerpana.", file=sys.stderr)
        return 1

    pick = choose(remaining)
    url = url_for(pick["path"])
    message = generate_fb_text(pick["title"], pick["description"], pick["body"])

    print(f"Wybrano: {pick['path']}\nURL: {url}\n--- treść ---\n{message}\n-------------")

    if dry_run:
        print("[DRY RUN] bez publikacji i bez commitu.")
        return 0

    fb_post_id = publish_to_fb(message, url)
    print(f"Opublikowano: {fb_post_id}")
    record(tracking, pick["path"], url, fb_post_id, message)
    save_tracking(tracking)
    git_commit_and_push(f"fb: {pick['path']} -> {fb_post_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
