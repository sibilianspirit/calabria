# FB Daily Post – konfiguracja

Automat (`.github/workflows/fb-daily-post.yml` + `scripts/fb_publish.py`) codziennie o 18:00 UTC
publikuje na stronie Facebook jedną losową polską stronę serwisu. Publikować może na dwa sposoby:

- **Wariant A – Make.com (zalecany, bez konta dewelopera Meta).** Skrypt wysyła gotowy post na
  webhook, a Make publikuje go na stronie przez własną aplikację Meta. Potrzebny sekret: `FB_WEBHOOK_URL`.
- **Wariant B – Graph API bezpośrednio.** Wymaga konta dewelopera Meta i tokenu strony.
  Sekrety: `FB_PAGE_ACCESS_TOKEN`, `FB_PAGE_ID`. Opis w dalszej części.

W obu wariantach potrzebny jest `OPENAI_API_KEY` (już ustawiony).

## Wariant A – Make.com krok po kroku

1. Załóż konto na https://www.make.com (e-mail, plan Free: 1000 operacji/mies., nam wystarczy ok. 90).
2. **Create a new scenario**.
3. Pierwszy moduł: **Webhooks → Custom webhook → Add**, nazwa np. `bestofcalabria-fb`.
   Skopiuj adres `https://hook.eu2.make.com/...` – to będzie `FB_WEBHOOK_URL`.
4. Kliknij **Run once** w Make, a w terminalu wyślij próbkę, żeby Make poznał strukturę danych:
   ```
   curl -X POST -H "Content-Type: application/json" \
     -d '{"message":"test","link":"https://bestofcalabria.com/pl/"}' \
     https://hook.eu2.make.com/TWOJ_ADRES
   ```
5. Drugi moduł: **Facebook Pages → Create a Post**. Kliknij **Add** przy Connection, zaloguj się
   kontem FB, które administruje stroną *Poznaj Kalabrię*, i zezwól na dostęp do tej strony.
6. W module wybierz Page: *Poznaj Kalabrię*. W pole **Message** przeciągnij `1. message`,
   w pole **Link** przeciągnij `1. link`.
7. Zapisz scenariusz (ikona dyskietki), włącz przełącznik **Scheduling ON** (u dołu, ustawienie
   „Immediately as data arrives”).
8. Sekret w GitHubie:
   ```
   gh secret set FB_WEBHOOK_URL
   ```
   (wklej adres webhooka i Enter).
9. Test z GitHuba – publikuje Tropeę na stronie:
   ```
   gh workflow run fb-daily-post.yml -f pick=kierunki/tropea/_index.html
   gh run watch
   ```
   Jeśli post pojawił się na FB, a w repo jest commit `fb: ...`, cron przejmuje resztę.

Uwaga: przy webhooku skrypt nie zna id posta na FB, w `.fb-published.json` zapisuje `Accepted`.

## Wariant B – Graph API (gdy uda się założyć konto dewelopera)

## 1. Aplikacja Meta

1. Wejdź na https://developers.facebook.com/apps/ i kliknij **Create App**.
2. Use case: **Other** → typ **Business**. Nazwa dowolna, np. `bestofcalabria-publisher`.
3. Po utworzeniu nie dodawaj żadnych produktów. Zapisz **App ID** i **App Secret**
   (Settings → Basic).

## 2. Krótkotrwały token użytkownika

1. Otwórz **Graph API Explorer**: https://developers.facebook.com/tools/explorer/
2. Wybierz swoją aplikację w prawym górnym rogu.
3. W polu *User or Page* zostaw **User Token**, kliknij **Add a Permission** i zaznacz:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
4. Kliknij **Generate Access Token**, zaloguj się i zaakceptuj uprawnienia dla strony
   *Poznaj Kalabrię*. Skopiuj token (ważny ok. 1 godz.).

## 3. Wymiana na długotrwały token użytkownika (60 dni)

W przeglądarce albo curlem:

```
https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=KROTKI_TOKEN
```

Odpowiedź zawiera `access_token` – to długotrwały token użytkownika.

## 4. Token strony (nie wygasa)

```
https://graph.facebook.com/v21.0/me/accounts?access_token=DLUGI_TOKEN_UZYTKOWNIKA
```

W odpowiedzi jest lista stron. Dla *Poznaj Kalabrię* skopiuj:

- `id` → to będzie `FB_PAGE_ID`
- `access_token` → to będzie `FB_PAGE_ACCESS_TOKEN`

Token strony uzyskany z długotrwałego tokenu użytkownika nie ma daty wygaśnięcia, dopóki
konto administratora jest aktywne i nie zmieni hasła. Sprawdź to w
https://developers.facebook.com/tools/debug/accesstoken/ – powinno być **Expires: Never**.

## 5. Tryb aplikacji

Aplikacja może zostać w trybie **Development**. Publikowanie na stronie, której jesteś
administratorem, działa bez App Review. Nie przełączaj na Live, bo wtedy Meta wymaga
przeglądu uprawnień `pages_manage_posts`.

## 6. Sekrety w GitHubie

Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Nazwa | Wartość |
|---|---|
| `FB_PAGE_ACCESS_TOKEN` | token strony z kroku 4 |
| `FB_PAGE_ID` | id strony z kroku 4 |
| `OPENAI_API_KEY` | klucz OpenAI (ten sam, którego używa fact-checker) |

Opcjonalnie w zakładce **Variables**: `OPENAI_MODEL` (domyślnie `gpt-5.4`).

Z terminala to samo:

```
gh secret set FB_PAGE_ACCESS_TOKEN
gh secret set FB_PAGE_ID
gh secret set OPENAI_API_KEY < fact-checker/api-key.txt
```

## 7. Pierwsze uruchomienie

1. Dry run, bez publikacji:
   ```
   gh workflow run fb-daily-post.yml -f dry_run=true
   gh run watch
   ```
   W logu powinna być wybrana strona, URL i wygenerowany tekst.
2. Publikacja konkretnej strony na próbę:
   ```
   gh workflow run fb-daily-post.yml -f pick=kierunki/tropea/_index.html
   ```
3. Jeśli post jest na FB, a w repo pojawił się commit `fb: ...` z `.fb-published.json`,
   cron przejmuje resztę.

## Lokalnie

```
pip install -r scripts/requirements.txt
python -m pytest scripts/ -q
DRY_RUN=true OPENAI_API_KEY=$(cat fact-checker/api-key.txt) python scripts/fb_publish.py
```

## Gdy coś się psuje

- **HTTP 400, code 190** w logu – token stracił ważność. Powtórz kroki 2–4 i podmień sekret.
- **Issue „pula treści wyczerpana”** – wszystkie strony poszły. Wyczyść `.fb-published.json`
  do `{"posts": []}` albo dodaj nowe treści.
- **Zły podgląd linku na FB** – odśwież cache w https://developers.facebook.com/tools/debug/
  (Scrape Again). Podgląd bierze się z tagów Open Graph strony.
