# FB Daily Auto-Publisher — Design Spec

**Data:** 2026-04-22
**Autor:** sibilianspirit (z pomocą Claude)
**Projekt:** bestofcalabria.com (Hugo + Cloudflare Pages)

## Cel

GitHub Actions raz dziennie losuje jedną polską stronę z `content/pl/`, generuje przez GPT-5.4 krótki opis w stylu FB (2–3 zdania), publikuje post (tekst + link) na stronie Facebook, i zapamiętuje co już wypuścił żeby nie duplikował. Po wyczerpaniu puli — zatrzymuje się i powiadamia właściciela przez GitHub Issue + email.

## Zakres

**W zakresie:**
- Workflow GitHub Actions z cron schedule
- Python skrypt publikujący
- Plik tracking `.fb-published.json` w repo
- Generowanie opisów przez OpenAI GPT-5.4
- Publikacja przez Facebook Graph API (tekst + link, bez uploadu zdjęcia)
- Dokument setup po stronie Meta (jak zdobyć long-lived Page Access Token)
- Tryb dry-run do testów manualnych
- Obsługa wyczerpania puli (GitHub Issue + fail workflow)

**Poza zakresem (na teraz):**
- Publikacja wersji EN (tylko PL)
- Uploadowanie zdjęć przez Graph API (wykorzystujemy OG preview z linku)
- Analytics / tracking klikalności postów
- Multi-platform (Instagram, X/Twitter, LinkedIn)
- Planowanie postów na konkretne daty / kalendarz edytorski
- UI do konfiguracji

## Decyzje brainstormingu

| Decyzja | Wybór | Alternatywa odrzucona |
|---|---|---|
| Pula treści | tylko `content/pl/` | EN, obie wersje |
| Generowanie opisu | GPT-5.4 (OpenAI) | meta description, lokalne szablony, Claude |
| Tracking | `.fb-published.json` w repo + commit | Gist, Actions Cache, Cloudflare KV |
| Wyczerpanie puli | stop + GitHub Issue + fail workflow (email) | cykl od nowa, re-publish po N dniach |
| Format posta | tekst + link (FB ciągnie OG preview) | upload zdjęcia, custom thumbnail |
| Godzina | 18:00 UTC = 19:00 CET zimą / 20:00 CEST latem (1h DST drift akceptujemy) | dwa crony sezonowe |
| Setup FB | użytkownik ma stronę, token do wygenerowania | — |

## Architektura

```
┌─────────────────────────────────────────────────────────────┐
│  GitHub Actions (cron: 0 18 * * *, workflow_dispatch)      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  scripts/fb_publish.py                               │   │
│  │                                                      │   │
│  │  1. Scan content/pl/**/*.html → candidates          │   │
│  │  2. Load .fb-published.json → filter out published  │   │
│  │  3. Exhausted? → create Issue, exit 1               │   │
│  │  4. random.choice(remaining)                         │   │
│  │  5. Extract frontmatter (title, description, body)  │   │
│  │  6. OpenAI GPT-5.4 → generate FB post text (PL)     │   │
│  │  7. POST /{page-id}/feed (message + link)           │   │
│  │  8. Append to .fb-published.json                     │   │
│  │  9. git commit + push                                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  Secrets: FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID, OPENAI_API_KEY │
└─────────────────────────────────────────────────────────────┘
```

## Komponenty

### 1. `.github/workflows/fb-daily-post.yml`

```yaml
name: FB Daily Post

on:
  schedule:
    - cron: '0 18 * * *'  # 18:00 UTC = 19:00 CET winter / 20:00 CEST summer
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Dry run (no FB post, no commit)'
        type: boolean
        default: false

permissions:
  contents: write  # for committing .fb-published.json
  issues: write    # for exhaustion issue

jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install requests python-frontmatter openai
      - run: python scripts/fb_publish.py
        env:
          FB_PAGE_ACCESS_TOKEN: ${{ secrets.FB_PAGE_ACCESS_TOKEN }}
          FB_PAGE_ID: ${{ secrets.FB_PAGE_ID }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          DRY_RUN: ${{ inputs.dry_run }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
```

### 2. `scripts/fb_publish.py`

Struktura (pseudokod w sekcjach):

**Konfiguracja:**
- `BASE_URL = "https://bestofcalabria.com"`
- `CONTENT_DIR = "content/pl"`
- `TRACKING_FILE = ".fb-published.json"`
- Kwalifikują się wszystkie strony contentowe (miasta, atrakcje, natura, kuchnia, kultura, blog, praktyczne, plaze).
- Wykluczamy tylko **strony techniczne**:
  - `content/pl/_index.html` (homepage)
  - Section-listing `_index.html` na głębokości 2 (`content/pl/kierunki/_index.html`, `.../blog/_index.html`, `.../kuchnia/_index.html` itd.)
  - Strony utility: `content/pl/{kontakt, o-nas, wspolpraca}/**`
- Safety net: min. długość body 1500 znaków + wymagane `title` i `description` w frontmatterze.

Przy 90 plikach HTML i ~10 wykluczeniach zostaje **~80 kandydatów** (≈2.5 miesiąca przy 1/dzień).

**Kandydaci (scan_candidates):**
```python
UTILITY_DIRS = {"kontakt", "o-nas", "wspolpraca"}

def scan_candidates():
    for path in Path("content/pl").rglob("*.html"):
        rel = path.relative_to("content/pl")
        # Skip homepage
        if str(rel) == "_index.html":
            continue
        # Skip utility pages (kontakt, o-nas, wspolpraca)
        if rel.parts[0] in UTILITY_DIRS:
            continue
        # Skip section-listing pages: content/pl/<section>/_index.html
        if len(rel.parts) == 2 and rel.name == "_index.html":
            continue
        fm, body = parse_frontmatter(path)
        if not fm.get("title") or not fm.get("description"):
            continue
        if len(body.strip()) < 1500:
            continue
        yield {"path": str(rel), "title": fm["title"], "description": fm["description"], "body": body}
```

**URL construction:**
```python
def url_for(rel_path: str) -> str:
    # "kierunki/tropea/_index.html" → "/pl/kierunki/tropea/"
    # "kuchnia/nduja/index.html" → "/pl/kuchnia/nduja/"
    p = rel_path.replace("_index.html", "").replace("index.html", "")
    return f"{BASE_URL}/pl/{p.rstrip('/')}/"
```

**Tracking (load/save/is_published):**
```python
def load_tracking() -> dict:
    if not Path(TRACKING_FILE).exists():
        return {"posts": []}
    return json.loads(Path(TRACKING_FILE).read_text())

def is_published(tracking: dict, path: str) -> bool:
    return any(p["path"] == path for p in tracking["posts"])

def record(tracking: dict, path: str, url: str, fb_post_id: str):
    tracking["posts"].append({
        "path": path,
        "url": url,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "fb_post_id": fb_post_id,
    })
    Path(TRACKING_FILE).write_text(json.dumps(tracking, indent=2, ensure_ascii=False))
```

**OpenAI prompt (generate_fb_text):**
```
System: Jesteś redaktorem social media dla bestofcalabria.com — portalu o podróżach po Kalabrii.
Piszesz krótkie, zachęcające posty na Facebook po polsku. Styl: ciepły, konkretny, bez clickbaitu.

User: Napisz post na FB (2-3 zdania, max 280 znaków) do linku:
Tytuł: {title}
Meta opis: {description}
Fragment treści:
{body_first_1000_chars}

Zasady:
- Po polsku, naturalnie, nie przesadzaj z emocjami
- Max 1 emoji (opcjonalnie, pasujące tematycznie)
- Na końcu 2-3 krótkie hashtagi: #Kalabria + 1-2 tematyczne (#Tropea, #włochy, #plaże itp.)
- BEZ "Sprawdź", "Kliknij", "Odkryj teraz" — to spam
- Zakończ naturalnie, zachęć zdaniem, nie imperatywem

Zwróć TYLKO tekst posta, bez cudzysłowów ani dodatkowych komentarzy.
```

Model: `gpt-5.4` (konsystencja z resztą projektu), `max_tokens=200`, `temperature=0.7`.

**Facebook publish:**
```python
def publish_to_fb(message: str, link: str) -> str:
    resp = requests.post(
        f"https://graph.facebook.com/v21.0/{FB_PAGE_ID}/feed",
        data={"message": message, "link": link, "access_token": FB_PAGE_ACCESS_TOKEN},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]  # format: "pageId_postId"
```

**Exhaustion handling:**
```python
def notify_exhausted():
    # Create GitHub Issue via REST API
    requests.post(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues",
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"},
        json={
            "title": "FB queue exhausted — wszystkie strony opublikowane",
            "body": "Workflow `fb-daily-post` wyczerpał pulę treści. Dodaj nowe strony do `content/pl/` lub zresetuj `.fb-published.json`.",
            "labels": ["fb-publisher", "automation"],
        },
        timeout=10,
    )
```

**Main flow:**
```python
def main():
    candidates = list(scan_candidates())
    tracking = load_tracking()
    remaining = [c for c in candidates if not is_published(tracking, c["path"])]

    print(f"Total candidates: {len(candidates)}, already published: {len(candidates) - len(remaining)}")

    if not remaining:
        notify_exhausted()
        sys.exit(1)

    pick = random.choice(remaining)
    url = url_for(pick["path"])

    message = generate_fb_text(pick["title"], pick["description"], pick["body"])

    print(f"Picked: {pick['path']}")
    print(f"URL: {url}")
    print(f"Message:\n{message}")

    if os.environ.get("DRY_RUN") == "true":
        print("[DRY RUN] Skipping FB publish and commit.")
        return

    fb_post_id = publish_to_fb(message, url)
    record(tracking, pick["path"], url, fb_post_id)
    git_commit_and_push(f"fb: publish {pick['path']} → {fb_post_id}")
```

**Git commit + push (w skrypcie, nie w yaml):**
```python
def git_commit_and_push(msg: str):
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", ".fb-published.json"], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)
    # push with retry on rebase conflict
    for attempt in range(3):
        r = subprocess.run(["git", "push"])
        if r.returncode == 0:
            return
        subprocess.run(["git", "pull", "--rebase"], check=True)
    raise RuntimeError("git push failed after 3 attempts")
```

### 3. `.fb-published.json`

```json
{
  "posts": [
    {
      "path": "kierunki/tropea/_index.html",
      "url": "https://bestofcalabria.com/pl/kierunki/tropea/",
      "published_at": "2026-04-22T18:00:00+00:00",
      "fb_post_id": "1234567890_9876543210"
    }
  ]
}
```

Początkowa zawartość: `{"posts": []}`.

### 4. `docs/FB_SETUP.md`

Krok po kroku instrukcja zdobywania long-lived Page Access Token:

1. **Meta Developer App** — stworzenie app na developers.facebook.com (Type: Business, bez produktu Login, tylko Graph API access)
2. **User short-lived token** — Graph API Explorer, permissions: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`
3. **Extend to long-lived user token** — `GET /oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN` (ważny 60 dni)
4. **Get Page Access Token (long-lived)** — `GET /me/accounts?access_token=LONG_USER_TOKEN` → zwraca tablicę stron z `access_token` dla każdej. Page token pochodzący z long-lived user tokena NIE WYGASA (przy zachowaniu aktywnego użytkownika admin).
5. **Weryfikacja w Access Token Debugger** (developers.facebook.com/tools/debug/accesstoken/) — powinno pokazać "Expires: Never" i permissions
6. **Dodanie do GitHub Secrets** — `Settings → Secrets and variables → Actions → New repository secret`:
   - `FB_PAGE_ACCESS_TOKEN`
   - `FB_PAGE_ID` (widoczne w `/me/accounts` response jako `id`)
   - `OPENAI_API_KEY` (wartość z `fact-checker/api-key.txt`)

## Przepływ danych

1. Cron wyzwala workflow o 18:00 UTC
2. Checkout repo → Python 3.12 → pip install requests/python-frontmatter/openai
3. Skrypt skanuje `content/pl/`, filtruje wykluczenia i min. długość
4. Wczytuje `.fb-published.json`, usuwa już opublikowane
5. Losuje jedną (albo tworzy Issue i exit 1)
6. Czyta frontmatter + body, składa prompt dla GPT-5.4
7. Wywołuje OpenAI API (retry 2x, backoff 2s/4s)
8. Wywołuje Facebook Graph API (retry 2x, backoff 2s/4s)
9. Appenduje wpis do JSON
10. Commituje i pusha (retry z `pull --rebase` przy konflikcie)

## Obsługa błędów

| Sytuacja | Reakcja |
|---|---|
| OpenAI 5xx / timeout | retry 2x z backoff, potem `raise` → workflow fail |
| OpenAI rate limit (429) | retry 2x z dłuższym backoff (10s/30s) |
| Facebook 5xx | retry 2x z backoff → workflow fail |
| Facebook 4xx (invalid token) | natychmiastowy fail z komunikatem w logach, Issue z `label: token-expired` |
| Git push conflict | `pull --rebase` + retry (3 próby łącznie) |
| Pula wyczerpana | GitHub Issue + exit 1 |
| Workflow fail | GitHub domyślnie wysyła email do admina repo |

## Testowanie

1. **Dry-run przed pierwszym crontabem:**
   - `gh workflow run fb-daily-post.yml -f dry_run=true` (lub ręcznie z UI GitHuba)
   - Skrypt scanuje, losuje, generuje opis, printuje — ALE nie publikuje i nie commituje
   - Sprawdzamy output w GitHub Actions logs
2. **Pierwszy real run:** `workflow_dispatch` bez `dry_run` → weryfikujemy że post faktycznie ląduje na FB i JSON się commituje
3. **Test wyczerpania puli:** manualnie wypełniamy `.fb-published.json` wszystkimi path, odpalamy dry-run=false → sprawdzamy Issue
4. **Test retry:** nieaktualny token w secretach → sprawdzamy komunikat w logach

## Decyzje otwarte (do potwierdzenia przy implementacji)

1. **Hashtag pool** — czy GPT-5.4 ma dobierać sam, czy dostarczamy listę (`#Kalabria`, `#Włochy`, `#Italy`, `#Travel`, `#ItalyTravel`, `#SouthernItaly`, plus tematyczne per miejsce)? **Propozycja:** niech GPT dobiera sam, instruowany by użył `#Kalabria` + 1-2 tematyczne.
2. **DST handling długoterminowo** — akceptujemy 1h drift; gdyby przeszkadzało, w v2 dodamy drugi cron + warunek na miesiąc.

## Pliki do stworzenia/zmiany

**Nowe:**
- `.github/workflows/fb-daily-post.yml`
- `scripts/fb_publish.py`
- `.fb-published.json`
- `docs/FB_SETUP.md`

**Bez zmian:**
- Reszta repo

## Szacowany wysiłek

- Setup Meta App + tokeny (po stronie użytkownika): ~30 min
- Implementacja workflow + skrypt: ~1.5h
- Testy (dry-run + real run): ~30 min
- **Total:** ~2.5h roboczych (bez czasu na setup Meta)

## Ryzyka

| Ryzyko | Prawdopodobieństwo | Mitigation |
|---|---|---|
| Long-lived page token jednak wygasa (Meta zmienia polityki) | niskie | monitorujemy 4xx w logach, Issue przy expired |
| FB oznaczy częste linki jako spam | niskie (1x dzień, różne URLe, OG preview prawidłowe) | akceptujemy, w razie czego zmniejszamy częstotliwość |
| GPT-5.4 wygeneruje słaby/nietrafny tekst | średnie | prompt konsekwentny, `temperature=0.7`, można iterować na prompcie po pierwszych postach |
| Commit z bota psuje deploy Cloudflare Pages | niskie (zmiana tylko `.fb-published.json`, nie content/) | `.fb-published.json` w gitignore Hugo? Nie — jest poza content/ więc Hugo go zignoruje |
| Dwa równoległe runy (np. manual + cron) nadpisują JSON | bardzo niskie (cron 1x dzień) | `pull --rebase` retry w git push wystarczy |
