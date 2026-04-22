# FB Daily Auto-Publisher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** GitHub Actions publishes one random Polish content page to Facebook daily, using GPT-5.4 for the post copy, with deduplication via a tracked JSON file in the repo.

**Architecture:** Single Python script (`scripts/fb_publish.py`) scans `content/pl/`, excludes technical pages, filters out already-published (from `.fb-published.json`), picks one at random, generates copy via OpenAI, posts to Facebook Graph API, then commits the updated tracking file. Triggered by GitHub Actions cron (`0 18 * * *` UTC) or manual `workflow_dispatch` with optional `dry_run`. Exhausted pool → creates a GitHub Issue and fails (email alert).

**Tech Stack:** Python 3.12, `requests`, `python-frontmatter`, `openai` (SDK), `pytest`. GitHub Actions. Facebook Graph API v21.0. OpenAI `gpt-5.4`.

**Spec:** `docs/superpowers/specs/2026-04-22-fb-daily-auto-publisher-design.md`

**File Structure:**
- `scripts/fb_publish.py` — main script (filter, tracking, OpenAI, FB, git push, main flow)
- `scripts/test_fb_publish.py` — pytest unit tests for pure-logic functions
- `scripts/requirements.txt` — pinned deps
- `.github/workflows/fb-daily-post.yml` — cron + manual trigger workflow
- `.fb-published.json` — tracking state, initially `{"posts": []}`
- `docs/FB_SETUP.md` — Meta App + long-lived Page Access Token instructions

---

## Task 1: Scaffolding — scripts directory, requirements, skeleton

**Files:**
- Create: `scripts/fb_publish.py`
- Create: `scripts/requirements.txt`
- Create: `scripts/test_fb_publish.py`

- [ ] **Step 1: Create `scripts/requirements.txt`**

```
requests==2.32.3
python-frontmatter==1.1.0
openai==1.54.3
pytest==8.3.3
```

- [ ] **Step 2: Create `scripts/fb_publish.py` skeleton**

```python
"""FB Daily Auto-Publisher — publishes one random PL content page to Facebook."""
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import frontmatter
import requests
from openai import OpenAI

BASE_URL = "https://bestofcalabria.com"
CONTENT_DIR = Path("content/pl")
TRACKING_FILE = Path(".fb-published.json")
UTILITY_DIRS = {"kontakt", "o-nas", "wspolpraca"}
MIN_BODY_CHARS = 1500
OPENAI_MODEL = "gpt-5.4"
FB_API_VERSION = "v21.0"


def main() -> int:
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Create `scripts/test_fb_publish.py` skeleton**

```python
"""Unit tests for fb_publish pure-logic functions."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import fb_publish
```

- [ ] **Step 4: Verify pytest can discover and run (no tests yet = pass trivially)**

Run: `cd scripts && python -m pip install -r requirements.txt && python -m pytest test_fb_publish.py -v`
Expected: `no tests ran` or exit 5 (no tests collected) — both acceptable.

- [ ] **Step 5: Commit**

```bash
git add scripts/
git commit -m "feat(fb): scaffold auto-publisher script and test harness"
```

---

## Task 2: `scan_candidates` — filter logic with TDD

**Files:**
- Modify: `scripts/fb_publish.py`
- Modify: `scripts/test_fb_publish.py`

- [ ] **Step 1: Write failing tests for `scan_candidates`**

Append to `scripts/test_fb_publish.py`:

```python
# Tests run from repo root so content/pl/ is resolvable.

@pytest.fixture(autouse=True)
def _cd_repo_root(monkeypatch, tmp_path):
    repo_root = Path(__file__).resolve().parent.parent
    monkeypatch.chdir(repo_root)


def test_scan_candidates_excludes_homepage():
    paths = [c["path"] for c in fb_publish.scan_candidates()]
    assert "_index.html" not in paths


def test_scan_candidates_excludes_utility_dirs():
    paths = [c["path"] for c in fb_publish.scan_candidates()]
    for p in paths:
        assert not p.startswith("kontakt/")
        assert not p.startswith("o-nas/")
        assert not p.startswith("wspolpraca/")


def test_scan_candidates_excludes_section_listings():
    paths = [c["path"] for c in fb_publish.scan_candidates()]
    # Section-level _index.html (depth 2) should be excluded
    for p in paths:
        parts = Path(p).parts
        if len(parts) == 2 and parts[-1] == "_index.html":
            pytest.fail(f"section listing leaked: {p}")


def test_scan_candidates_includes_city_index():
    # content/pl/kierunki/tropea/_index.html is a real city page with content
    paths = [c["path"] for c in fb_publish.scan_candidates()]
    assert "kierunki/tropea/_index.html" in paths


def test_scan_candidates_includes_blog_post():
    paths = [c["path"] for c in fb_publish.scan_candidates()]
    assert "blog/weekend-w-reggio-calabria.html" in paths


def test_scan_candidates_has_title_and_description():
    for c in fb_publish.scan_candidates():
        assert c["title"]
        assert c["description"]
        assert len(c["body"].strip()) >= fb_publish.MIN_BODY_CHARS


def test_scan_candidates_yields_at_least_50():
    # Sanity: we expect ~80 candidates; fail loudly if filter breaks
    candidates = list(fb_publish.scan_candidates())
    assert len(candidates) >= 50, f"got only {len(candidates)} candidates"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_fb_publish.py -v`
Expected: FAIL — `AttributeError: module 'fb_publish' has no attribute 'scan_candidates'`

- [ ] **Step 3: Implement `scan_candidates`**

Add to `scripts/fb_publish.py` (before `main()`):

```python
def scan_candidates() -> Iterable[dict]:
    """Yield content pages eligible for FB posting.

    Excludes: homepage, utility dirs (kontakt/o-nas/wspolpraca),
    section-listing _index.html at depth 2, and pages with missing
    title/description or body < MIN_BODY_CHARS.
    """
    for path in CONTENT_DIR.rglob("*.html"):
        rel = path.relative_to(CONTENT_DIR)
        # Homepage
        if str(rel) == "_index.html":
            continue
        # Utility pages
        if rel.parts[0] in UTILITY_DIRS:
            continue
        # Section listings (content/pl/<section>/_index.html)
        if len(rel.parts) == 2 and rel.name == "_index.html":
            continue
        post = frontmatter.load(path)
        title = post.metadata.get("title")
        description = post.metadata.get("description")
        if not title or not description:
            continue
        body = post.content
        if len(body.strip()) < MIN_BODY_CHARS:
            continue
        yield {
            "path": str(rel).replace(os.sep, "/"),
            "title": title,
            "description": description,
            "body": body,
        }
```

- [ ] **Step 4: Run tests — should pass**

Run: `cd scripts && python -m pytest test_fb_publish.py -v`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/fb_publish.py scripts/test_fb_publish.py
git commit -m "feat(fb): scan_candidates filter with unit tests"
```

---

## Task 3: `url_for` — content path → public URL

**Files:**
- Modify: `scripts/fb_publish.py`
- Modify: `scripts/test_fb_publish.py`

- [ ] **Step 1: Write failing tests**

Append to `scripts/test_fb_publish.py`:

```python
def test_url_for_city_index():
    assert fb_publish.url_for("kierunki/tropea/_index.html") == \
        "https://bestofcalabria.com/pl/kierunki/tropea/"


def test_url_for_attraction_index():
    assert fb_publish.url_for("kuchnia/nduja/index.html") == \
        "https://bestofcalabria.com/pl/kuchnia/nduja/"


def test_url_for_blog_post():
    assert fb_publish.url_for("blog/weekend-w-reggio-calabria.html") == \
        "https://bestofcalabria.com/pl/blog/weekend-w-reggio-calabria/"


def test_url_for_nested_attraction():
    assert fb_publish.url_for("kierunki/reggio-calabria/lungomare/_index.html") == \
        "https://bestofcalabria.com/pl/kierunki/reggio-calabria/lungomare/"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_fb_publish.py::test_url_for_city_index -v`
Expected: FAIL — `AttributeError: module 'fb_publish' has no attribute 'url_for'`

- [ ] **Step 3: Implement `url_for`**

Add to `scripts/fb_publish.py`:

```python
def url_for(rel_path: str) -> str:
    """Convert relative content path to public URL."""
    p = rel_path.replace("_index.html", "").replace("index.html", "")
    # Blog posts end in .html (no trailing dir); strip extension, add slash
    if p.endswith(".html"):
        p = p[: -len(".html")] + "/"
    return f"{BASE_URL}/pl/{p.rstrip('/')}/"
```

- [ ] **Step 4: Run tests — should pass**

Run: `cd scripts && python -m pytest test_fb_publish.py -v -k url_for`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/fb_publish.py scripts/test_fb_publish.py
git commit -m "feat(fb): url_for content path mapping"
```

---

## Task 4: Tracking file — load / is_published / record

**Files:**
- Modify: `scripts/fb_publish.py`
- Modify: `scripts/test_fb_publish.py`

- [ ] **Step 1: Write failing tests**

Append to `scripts/test_fb_publish.py`:

```python
def test_load_tracking_missing_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(fb_publish, "TRACKING_FILE", Path(".fb-published.json"))
    assert fb_publish.load_tracking() == {"posts": []}


def test_load_tracking_existing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(fb_publish, "TRACKING_FILE", Path(".fb-published.json"))
    data = {"posts": [{"path": "blog/foo.html", "url": "https://x/", "published_at": "2026-04-22T00:00:00+00:00", "fb_post_id": "1_2"}]}
    Path(".fb-published.json").write_text(json.dumps(data))
    assert fb_publish.load_tracking() == data


def test_is_published_true(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(fb_publish, "TRACKING_FILE", Path(".fb-published.json"))
    tracking = {"posts": [{"path": "blog/foo.html", "url": "x", "published_at": "x", "fb_post_id": "1_2"}]}
    assert fb_publish.is_published(tracking, "blog/foo.html") is True


def test_is_published_false(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(fb_publish, "TRACKING_FILE", Path(".fb-published.json"))
    tracking = {"posts": []}
    assert fb_publish.is_published(tracking, "blog/foo.html") is False


def test_record_appends_and_writes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tracking_path = tmp_path / ".fb-published.json"
    monkeypatch.setattr(fb_publish, "TRACKING_FILE", tracking_path)
    tracking = {"posts": []}
    fb_publish.record(tracking, "blog/foo.html", "https://x/", "1_2")
    assert len(tracking["posts"]) == 1
    assert tracking["posts"][0]["path"] == "blog/foo.html"
    saved = json.loads(tracking_path.read_text())
    assert saved["posts"][0]["fb_post_id"] == "1_2"
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `cd scripts && python -m pytest test_fb_publish.py -v -k "tracking or published or record"`
Expected: FAIL — `AttributeError: ... load_tracking`

- [ ] **Step 3: Implement tracking functions**

Add to `scripts/fb_publish.py`:

```python
def load_tracking() -> dict:
    """Load tracking JSON or return empty state."""
    if not TRACKING_FILE.exists():
        return {"posts": []}
    return json.loads(TRACKING_FILE.read_text(encoding="utf-8"))


def is_published(tracking: dict, path: str) -> bool:
    """Check if `path` is already in the tracking list."""
    return any(p["path"] == path for p in tracking["posts"])


def record(tracking: dict, path: str, url: str, fb_post_id: str) -> None:
    """Append a published entry and persist to disk."""
    tracking["posts"].append({
        "path": path,
        "url": url,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "fb_post_id": fb_post_id,
    })
    TRACKING_FILE.write_text(
        json.dumps(tracking, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
```

- [ ] **Step 4: Run tests — should pass**

Run: `cd scripts && python -m pytest test_fb_publish.py -v`
Expected: all previous tests + 5 new = 16 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/fb_publish.py scripts/test_fb_publish.py
git commit -m "feat(fb): tracking file load/is_published/record"
```

---

## Task 5: OpenAI integration — `generate_fb_text`

**Files:**
- Modify: `scripts/fb_publish.py`

No unit tests for the API call itself (would require mocking entire SDK — low value vs. dry-run integration test). The prompt text is the contract — gets eyeballed during dry-run.

- [ ] **Step 1: Implement `generate_fb_text` with retry**

Add to `scripts/fb_publish.py`:

```python
FB_PROMPT_SYSTEM = (
    "Jesteś redaktorem social media dla bestofcalabria.com — portalu o podróżach "
    "po Kalabrii. Piszesz krótkie, zachęcające posty na Facebook po polsku. "
    "Styl: ciepły, konkretny, bez clickbaitu."
)

FB_PROMPT_USER_TEMPLATE = """Napisz post na FB (2-3 zdania, max 280 znaków) do linku:
Tytuł: {title}
Meta opis: {description}
Fragment treści:
{body_excerpt}

Zasady:
- Po polsku, naturalnie, nie przesadzaj z emocjami
- Max 1 emoji (opcjonalnie, pasujące tematycznie)
- Na końcu 2-3 krótkie hashtagi: #Kalabria + 1-2 tematyczne
- BEZ "Sprawdź", "Kliknij", "Odkryj teraz" — to spam
- Zakończ naturalnie, zachęć zdaniem, nie imperatywem

Zwróć TYLKO tekst posta, bez cudzysłowów ani dodatkowych komentarzy."""


def generate_fb_text(title: str, description: str, body: str) -> str:
    """Generate FB post copy via OpenAI GPT-5.4 with retry on transient errors."""
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    user_msg = FB_PROMPT_USER_TEMPLATE.format(
        title=title,
        description=description,
        body_excerpt=body.strip()[:1000],
    )

    last_error: Exception | None = None
    for attempt, backoff in enumerate([2, 4, 10], start=1):
        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": FB_PROMPT_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=200,
                temperature=0.7,
                timeout=60,
            )
            text = resp.choices[0].message.content.strip()
            # Strip potential leading/trailing quotes the model occasionally adds
            return text.strip('"').strip("'").strip()
        except Exception as e:
            last_error = e
            print(f"[openai] attempt {attempt} failed: {e}", file=sys.stderr)
            if attempt < 3:
                time.sleep(backoff)
    raise RuntimeError(f"OpenAI failed after 3 attempts: {last_error}")
```

- [ ] **Step 2: Smoke test locally (manual, optional — skip if no OPENAI_API_KEY handy)**

```bash
cd scripts && OPENAI_API_KEY="$(cat ../fact-checker/api-key.txt)" python -c "
import fb_publish
print(fb_publish.generate_fb_text(
    'Tropea',
    'Tropea to urokliwe miasteczko na klifie nad Morzem Tyrreńskim.',
    'Tropea jest często nazywana perłą Kalabrii. Słynie z piaskowcowego klifu, krystalicznej wody i czerwonej cebuli.'
))
"
```
Expected: a 2-3 sentence Polish FB post ending with `#Kalabria` + 1-2 hashtags.

- [ ] **Step 3: Commit**

```bash
git add scripts/fb_publish.py
git commit -m "feat(fb): OpenAI GPT-5.4 post copy generator with retry"
```

---

## Task 6: Facebook Graph API — `publish_to_fb`

**Files:**
- Modify: `scripts/fb_publish.py`

- [ ] **Step 1: Implement `publish_to_fb` with retry**

Add to `scripts/fb_publish.py`:

```python
def publish_to_fb(message: str, link: str) -> str:
    """POST to Facebook Page feed. Returns the created post ID."""
    page_id = os.environ["FB_PAGE_ID"]
    token = os.environ["FB_PAGE_ACCESS_TOKEN"]
    url = f"https://graph.facebook.com/{FB_API_VERSION}/{page_id}/feed"

    last_error: Exception | None = None
    for attempt, backoff in enumerate([2, 4, 10], start=1):
        try:
            resp = requests.post(
                url,
                data={"message": message, "link": link, "access_token": token},
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()["id"]
            # 4xx → don't retry (bad token, bad URL, etc.)
            if 400 <= resp.status_code < 500:
                raise RuntimeError(
                    f"Facebook API {resp.status_code}: {resp.text}"
                )
            # 5xx → retry
            last_error = RuntimeError(f"{resp.status_code}: {resp.text}")
            print(f"[fb] attempt {attempt} 5xx: {resp.status_code}", file=sys.stderr)
        except requests.RequestException as e:
            last_error = e
            print(f"[fb] attempt {attempt} network error: {e}", file=sys.stderr)
        if attempt < 3:
            time.sleep(backoff)
    raise RuntimeError(f"Facebook publish failed after 3 attempts: {last_error}")
```

- [ ] **Step 2: Commit**

```bash
git add scripts/fb_publish.py
git commit -m "feat(fb): Facebook Graph API publish with retry and 4xx/5xx distinction"
```

---

## Task 7: GitHub Issue on exhaustion — `notify_exhausted`

**Files:**
- Modify: `scripts/fb_publish.py`

- [ ] **Step 1: Implement `notify_exhausted`**

Add to `scripts/fb_publish.py`:

```python
def notify_exhausted() -> None:
    """Create a GitHub Issue announcing the FB queue is empty.

    Best-effort: logs failure but does not raise — the workflow already
    fails via sys.exit(1) in main().
    """
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print("[notify] GITHUB_TOKEN or GITHUB_REPOSITORY missing; skipping issue", file=sys.stderr)
        return
    try:
        r = requests.post(
            f"https://api.github.com/repos/{repo}/issues",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
            json={
                "title": "FB queue exhausted — wszystkie strony opublikowane",
                "body": (
                    "Workflow `fb-daily-post` wyczerpał pulę treści.\n\n"
                    "**Opcje:**\n"
                    "- Dodaj nowe strony do `content/pl/` (filtr znajdzie je automatycznie)\n"
                    "- Lub zresetuj `.fb-published.json` do `{\"posts\": []}` aby puścić cykl od nowa"
                ),
                "labels": ["fb-publisher", "automation"],
            },
            timeout=10,
        )
        r.raise_for_status()
        print(f"[notify] issue created: {r.json().get('html_url')}")
    except Exception as e:
        print(f"[notify] failed to create issue: {e}", file=sys.stderr)
```

- [ ] **Step 2: Commit**

```bash
git add scripts/fb_publish.py
git commit -m "feat(fb): GitHub Issue notification on exhausted queue"
```

---

## Task 8: Git commit + push helper — `git_commit_and_push`

**Files:**
- Modify: `scripts/fb_publish.py`

- [ ] **Step 1: Implement `git_commit_and_push`**

Add to `scripts/fb_publish.py`:

```python
def git_commit_and_push(msg: str) -> None:
    """Configure bot identity, commit tracking file, and push with rebase retry."""
    subprocess.run(
        ["git", "config", "user.name", "github-actions[bot]"],
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email",
         "41898282+github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(["git", "add", str(TRACKING_FILE)], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)

    for attempt in range(3):
        r = subprocess.run(["git", "push"])
        if r.returncode == 0:
            return
        print(f"[git] push attempt {attempt + 1} failed, rebasing", file=sys.stderr)
        subprocess.run(["git", "pull", "--rebase"], check=True)
    raise RuntimeError("git push failed after 3 attempts")
```

- [ ] **Step 2: Commit**

```bash
git add scripts/fb_publish.py
git commit -m "feat(fb): git commit+push helper with rebase retry"
```

---

## Task 9: Main flow with dry-run support

**Files:**
- Modify: `scripts/fb_publish.py`

- [ ] **Step 1: Implement `main`**

Replace the `raise NotImplementedError` in `main()`:

```python
def main() -> int:
    candidates = list(scan_candidates())
    tracking = load_tracking()
    remaining = [c for c in candidates if not is_published(tracking, c["path"])]

    total = len(candidates)
    done = total - len(remaining)
    print(f"Candidates: {total} total, {done} published, {len(remaining)} remaining")

    if not remaining:
        print("Pool exhausted — creating GitHub Issue and exiting.")
        notify_exhausted()
        return 1

    pick = random.choice(remaining)
    url = url_for(pick["path"])

    print(f"Picked: {pick['path']}")
    print(f"URL:    {url}")

    message = generate_fb_text(pick["title"], pick["description"], pick["body"])
    print("Generated message:")
    print("---")
    print(message)
    print("---")

    if os.environ.get("DRY_RUN", "").lower() in {"true", "1", "yes"}:
        print("[DRY RUN] Skipping FB publish and git commit.")
        return 0

    fb_post_id = publish_to_fb(message, url)
    print(f"Published to FB: {fb_post_id}")

    record(tracking, pick["path"], url, fb_post_id)
    git_commit_and_push(f"fb: publish {pick['path']} -> {fb_post_id}")

    return 0
```

- [ ] **Step 2: Verify full test suite still passes**

Run: `cd scripts && python -m pytest test_fb_publish.py -v`
Expected: 16 passed.

- [ ] **Step 3: Verify script imports cleanly**

Run: `cd /mnt/c/projekty/calabria && python -c "import scripts.fb_publish as m; print('ok:', m.main)"`
Expected: `ok: <function main at 0x...>` (no import errors).

- [ ] **Step 4: Commit**

```bash
git add scripts/fb_publish.py
git commit -m "feat(fb): main flow with dry-run branching"
```

---

## Task 10: Initial `.fb-published.json`

**Files:**
- Create: `.fb-published.json`

- [ ] **Step 1: Create tracking file with empty state**

Content:

```json
{
  "posts": []
}
```

- [ ] **Step 2: Commit**

```bash
git add .fb-published.json
git commit -m "feat(fb): initial empty tracking state"
```

---

## Task 11: GitHub Actions workflow

**Files:**
- Create: `.github/workflows/fb-daily-post.yml`

- [ ] **Step 1: Create workflow file**

```yaml
name: FB Daily Post

on:
  schedule:
    # 18:00 UTC = 19:00 CET (winter) / 20:00 CEST (summer). 1h DST drift accepted.
    - cron: '0 18 * * *'
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Dry run (no FB post, no commit)'
        type: boolean
        default: false

permissions:
  contents: write   # commit .fb-published.json
  issues: write     # open issue on pool exhaustion

jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
          cache-dependency-path: scripts/requirements.txt

      - name: Install dependencies
        run: pip install -r scripts/requirements.txt

      - name: Run FB publisher
        env:
          FB_PAGE_ACCESS_TOKEN: ${{ secrets.FB_PAGE_ACCESS_TOKEN }}
          FB_PAGE_ID: ${{ secrets.FB_PAGE_ID }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          DRY_RUN: ${{ inputs.dry_run }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
        run: python scripts/fb_publish.py
```

- [ ] **Step 2: Validate YAML locally**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/fb-daily-post.yml'))" && echo ok`
Expected: `ok`.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/fb-daily-post.yml
git commit -m "ci(fb): GitHub Actions workflow with cron + manual dry-run"
```

---

## Task 12: Setup documentation — `docs/FB_SETUP.md`

**Files:**
- Create: `docs/FB_SETUP.md`

- [ ] **Step 1: Write the setup guide**

```markdown
# FB Daily Auto-Publisher — Setup

Procedura jednorazowa. Wynik: 3 secrets w GitHub + działający workflow `fb-daily-post`.

## 1. Meta Developer App

1. Wejdź na <https://developers.facebook.com/apps> → **Create App**
2. Use case: **Other** → Type: **Business** → nazwa dowolna (np. `BestOfCalabria FB Publisher`)
3. W app dashboard zapamiętaj **App ID** i **App Secret** (Settings → Basic)
4. **Nie dodawaj** produktu Login ani Pages — tylko Graph API (domyślnie dostępne)

## 2. Short-lived User Access Token

1. Wejdź na <https://developers.facebook.com/tools/explorer/>
2. Wybierz swoją app z dropdownu
3. Kliknij **Generate Access Token** → akceptuj permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
4. Skopiuj token — to jest short-lived (wygasa za ~1h)

## 3. Long-lived User Access Token

```bash
curl "https://graph.facebook.com/v21.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=APP_ID&\
client_secret=APP_SECRET&\
fb_exchange_token=SHORT_LIVED_TOKEN"
```

Zwróci `access_token` ważny 60 dni.

## 4. Long-lived Page Access Token

```bash
curl "https://graph.facebook.com/v21.0/me/accounts?access_token=LONG_USER_TOKEN"
```

W odpowiedzi znajdź obiekt swojej strony. Skopiuj:
- `id` → to **FB_PAGE_ID**
- `access_token` → to **FB_PAGE_ACCESS_TOKEN**

Ten page token **nie wygasa** dopóki admin strony ma aktywne konto Facebook.

## 5. Weryfikacja tokenu

<https://developers.facebook.com/tools/debug/accesstoken/> → wklej FB_PAGE_ACCESS_TOKEN. Powinno pokazać:
- **Expires:** Never
- **Scopes:** pages_show_list, pages_read_engagement, pages_manage_posts
- **Profile ID:** = twój FB_PAGE_ID

## 6. GitHub Secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**. Dodaj:

| Name | Value |
|---|---|
| `FB_PAGE_ACCESS_TOKEN` | Page token z kroku 4 |
| `FB_PAGE_ID` | Page ID z kroku 4 |
| `OPENAI_API_KEY` | Zawartość `fact-checker/api-key.txt` |

## 7. Pierwszy test — dry run

1. Repo → **Actions → FB Daily Post → Run workflow**
2. Zaznacz **Dry run** = true
3. Kliknij Run
4. Sprawdź logi: powinno wypisać wylosowaną stronę, URL, i wygenerowany tekst posta. **Nic nie pójdzie na FB**, żaden commit się nie zrobi.

## 8. Pierwszy real run

Powtórz punkt 7 z Dry run = false. Sprawdź:
- Post pojawił się na FB
- W repo pojawił się commit `fb: publish ... -> ...` aktualizujący `.fb-published.json`

Od tego momentu cron wystartuje codziennie o 18:00 UTC.

## Troubleshooting

**4xx z Facebook API** — token wygasł lub stracił permissions. Powtórz kroki 2-5.

**Rate limit z OpenAI** — skrypt retry'uje 3x; jeśli fail, sprawdź billing na <https://platform.openai.com/>.

**Git push conflict** — jeśli ręcznie commitujesz w czasie runa, rebase zadziała. W razie czego przejrzyj historię `git log .fb-published.json`.

**"Pool exhausted" Issue** — workflow zatrzymał się, bo wszystkie ~80 stron zostały opublikowane. Dodaj nowe strony lub zresetuj `.fb-published.json` do `{"posts": []}`.
```

- [ ] **Step 2: Commit**

```bash
git add docs/FB_SETUP.md
git commit -m "docs(fb): Meta App + long-lived Page Access Token setup guide"
```

---

## Task 13: Manual validation — local dry-run

**Files:** (no changes)

- [ ] **Step 1: Local dry-run with real OpenAI key, without FB/git side effects**

Run from repo root:

```bash
OPENAI_API_KEY="$(cat fact-checker/api-key.txt)" \
DRY_RUN=true \
python scripts/fb_publish.py
```

Expected output:
- `Candidates: 80+ total, 0 published, 80+ remaining`
- `Picked: <some/path>`
- `URL: https://bestofcalabria.com/pl/...`
- `Generated message: <Polish 2-3 sentence FB post with hashtags>`
- `[DRY RUN] Skipping FB publish and git commit.`
- Exit code 0.

- [ ] **Step 2: Eyeball the generated copy**

Run the dry-run 3-5 times. Each should pick a different page. Verify:
- Copy is coherent, in Polish, 2-3 sentences
- Has `#Kalabria` + 1-2 thematic hashtags
- No "Sprawdź", "Kliknij", "Odkryj teraz"
- No wrapping quotes

If the copy is poor, iterate on `FB_PROMPT_SYSTEM` / `FB_PROMPT_USER_TEMPLATE` in `scripts/fb_publish.py` and commit.

- [ ] **Step 3: No changes expected**

`git status` should be clean (no `.fb-published.json` changes from dry-run).

---

---

## ⚠️ User action required between Task 13 and Task 14

Before running Task 14, the user must complete **steps 1-6 of `docs/FB_SETUP.md`** (Meta App creation, long-lived Page Access Token, and adding 3 secrets to GitHub). This is a one-time manual setup that the engineer cannot automate.

Checklist for the user:
- [ ] Meta Developer App created
- [ ] Long-lived Page Access Token obtained and verified in Access Token Debugger (shows "Expires: Never")
- [ ] GitHub secrets added: `FB_PAGE_ACCESS_TOKEN`, `FB_PAGE_ID`, `OPENAI_API_KEY`

Once done, proceed to Task 14.

---

## Task 14: Manual validation — GitHub Actions dry-run

**Files:** (no changes — assumes user setup above is complete)

- [ ] **Step 1: Push to remote**

```bash
git push
```

- [ ] **Step 2: Trigger workflow_dispatch with dry_run=true**

Via UI: Repo → Actions → FB Daily Post → Run workflow → `dry_run: true` → Run.

Or via CLI:

```bash
gh workflow run fb-daily-post.yml -f dry_run=true
gh run watch
```

Expected: green run, logs showing candidate scan + generated message. No new commit on `main`, no post on FB.

- [ ] **Step 3: If fail — debug from logs**

Common issues:
- `KeyError: 'OPENAI_API_KEY'` — secret not set; check GitHub Settings → Secrets
- `content/pl does not exist` — `fetch-depth: 0` missing or working dir wrong
- Import error — `requirements.txt` missing a dep

---

## Task 15: Manual validation — first real FB post

**Files:** (no changes)

- [ ] **Step 1: Trigger workflow_dispatch with dry_run=false**

```bash
gh workflow run fb-daily-post.yml -f dry_run=false
gh run watch
```

- [ ] **Step 2: Verify on Facebook**

Open your FB page. The most recent post should be:
- Published within the last minute
- Contains the generated copy + OG link preview from the target page
- Link preview shows title/description/image from your Hugo OG tags

- [ ] **Step 3: Verify tracking commit landed**

```bash
git pull
cat .fb-published.json
```

Expected: one entry with `path`, `url`, `published_at`, `fb_post_id`.

- [ ] **Step 4: Verify cron schedule**

Repo → Actions → FB Daily Post → Upcoming runs should show "Scheduled: in XX hours" for the next 18:00 UTC.

---

## Summary of commits (14 total)

1. scaffold auto-publisher script and test harness
2. scan_candidates filter with unit tests
3. url_for content path mapping
4. tracking file load/is_published/record
5. OpenAI GPT-5.4 post copy generator with retry
6. Facebook Graph API publish with retry and 4xx/5xx distinction
7. GitHub Issue notification on exhausted queue
8. git commit+push helper with rebase retry
9. main flow with dry-run branching
10. initial empty tracking state
11. ci(fb): GitHub Actions workflow with cron + manual dry-run
12. docs(fb): Meta App + long-lived Page Access Token setup guide
13. (no commit — manual local validation)
14. (no commit — manual CI validation)
15. (no commit — first real post, which generates its own commit from within the workflow)

## Deferred / out of scope

- EN post publishing (second workflow)
- Uploading images via Graph API (currently uses OG link preview)
- CTR / analytics
- Instagram / X cross-posting
- Editorial calendar / per-page scheduling
- Hashtag pool from a static list (current: GPT chooses)
