# CLAUDE.md — projekt bestofcalabria.com
# Pełna wiedza operacyjna. Aktualizuj po każdej sesji.

---

## Uprawnienia operacyjne

- Wszystkie komendy bash (curl, python, node) — **wykonuj bez pytania o potwierdzenie**
- Wyjątki wymagające akceptu użytkownika:
  - Usuwanie plików lub treści (rm, DELETE do API)
  - Generowanie dodatkowych obrazów (generate-image.js) — kosztuje kredyty

---

## WordPress API
- URL: https://bestofcalabria.com/wp-json/wp/v2/
- Login: `admin`
- Hasło aplikacji: `JwGw oBQ1 yaHo hXeg oadm Kx86`
- Przykład: `curl --user "admin:JwGw oBQ1 yaHo hXeg oadm Kx86" "https://bestofcalabria.com/wp-json/wp/v2/pages/ID?context=edit"`

---

## Struktura URL — mapowanie PL ↔ EN

| Polski URL                        | Angielski URL                    |
|-----------------------------------|----------------------------------|
| `/pl/kierunki/[miasto]/`          | `/destinations/[city]/`          |
| `/pl/kierunki/[miasto]/[atr]/`    | `/destinations/[city]/[attr]/`   |
| `/pl/natura/`                     | `/nature/`                       |
| `/pl/kuchnia/`                    | `/cuisine/`                      |
| `/pl/kultura/`                    | `/culture/`                      |
| `/pl/praktyczne/`                 | `/practical/`                    |

Przykład: `/pl/kierunki/scilla/chianalea/` → `/destinations/scilla/chianalea/`

---

## Workflow publikacji (dla każdej strony)

1. Użytkownik podaje: treść PL + docelowy URL PL
2. Znajdź ID strony PL: `GET /wp-json/wp/v2/pages?slug=SLUG&context=edit`
3. Zaktualizuj treść PL: `PUT /wp-json/wp/v2/pages/ID` z `{"content": "...", "status": "publish"}`
4. Przetłumacz treść na EN (zachowaj strukturę `boc-` CSS i Gutenberg blocks)
5. Znajdź ID strony EN (mapowanie URL PL→EN jak powyżej)
6. Zaktualizuj treść EN tak samo

---

## Szablon strony (format `boc-`)

Wzorcowa strona: https://bestofcalabria.com/pl/kierunki/reggio-calabria/ (ID=2168)

Sekcje obowiązkowe (w kolejności):
```
[intro akapit — bez H1, tytuł jest w WP]
[sekcje merytoryczne z H2 + akapity]
[boc-faq-box — HTML block z <details>]
[boc-attractions-box — karty atrakcji]
[boc-transport-box — siatka transportu]
[boc-nearby-box — pigułki pobliskich miejsc]
```

### CSS klasy `boc-` — JEDYNY dopuszczalny format

**boc-attractions-box** — karty z numerami (NIE `boc-card-icon`, NIE `<strong>` zamiast `<h3>`):
```html
<div class="boc-attractions-box">
<h2 class="boc-section-title">Główne atrakcje</h2>
<div class="boc-cards-grid">
  <a href="/pl/kierunki/MIASTO/" class="boc-attraction-card">
    <div class="boc-attraction-num">1</div>
    <div><h3>Tytuł atrakcji</h3><p>Opis atrakcji.</p></div>
  </a>
  <!-- kolejne karty z num 2, 3... -->
</div>
</div>
```

**boc-transport-box** — prosty tekst w `<strong>`, BEZ emoji w HTML (CSS dodaje ikony):
```html
<div class="boc-transport-box">
<h2 class="boc-section-title">Jak dojechać</h2>
<div class="boc-transport-grid">
  <div class="boc-transport-item">
    <strong>Samolotem</strong>
    <p>Opis dojazdu samolotem.</p>
  </div>
  <!-- kolejne: Samochodem, Autobusem, Pociągiem -->
</div>
</div>
```
- EN odpowiedniki: "How to get there", "By plane", "By car", "By bus", "By train"
- **Nigdy nie używaj**: `boc-card-icon`, `boc-transport-icon`, `boc-transport-name`, `boc-transport-label`, `&#9992;`, `&#128652;` ani innych encji emoji w HTML

**boc-faq-box**, **boc-nearby-box** — bez zmian:
- `.boc-faq-box` + `.boc-section-title` — sekcja FAQ z `<details>`
- `.boc-nearby-box` + `.boc-nearby-grid` + `.boc-nearby-pill` + `.boc-dist` — w pobliżu

### Ważne: bloki Gutenberg
- Sekcje merytoryczne: `<!-- wp:paragraph -->` i `<!-- wp:heading -->`
- Sekcje HTML (boc-boxes): `<!-- wp:html -->`

---

## Mapa stron (kluczowe ID)

### Polskie strony
| URL | ID |
|-----|----|
| /pl/kierunki/reggio-calabria/ | 2168 |
| /pl/kierunki/reggio-calabria/bronzy-z-riace/ | 2169 |
| /pl/kierunki/reggio-calabria/lungomare/ | 2170 |
| /pl/kierunki/reggio-calabria/museo-nazionale/ | 2171 |
| /pl/kierunki/reggio-calabria/arena-dello-stretto/ | 2172 |
| /pl/kierunki/tropea/ | 2173 |
| /pl/kierunki/scilla/ | 2177 |
| /pl/kierunki/pizzo/ | 2181 |
| /pl/kierunki/bova/ | 2185 |
| /pl/kierunki/gerace/ | 2187 |
| /pl/kierunki/stilo/ | 2188 |
| /pl/kierunki/cosenza/ | 2189 |
| /pl/kierunki/catanzaro/ | 2190 |
| /pl/kierunki/locri/ | 2191 |

### Angielskie strony
| URL | ID |
|-----|----|
| /destinations/reggio-calabria/ | 2030 |
| /destinations/reggio-calabria/bronzi-di-riace/ | 2031 |
| /destinations/reggio-calabria/lungomare/ | 2032 |
| /destinations/reggio-calabria/museo-nazionale/ | 2033 |
| /destinations/reggio-calabria/arena-dello-stretto/ | 2034 |
| /destinations/tropea/ | 2035 |
| /destinations/scilla/ | 2039 |
| /destinations/pizzo/ | 2043 |
| /destinations/bova/ | 2047 |
| /destinations/gerace/ | 2049 |
| /destinations/stilo/ | 2050 |
| /destinations/cosenza/ | 2051 |
| /destinations/catanzaro/ | 2052 |
| /destinations/locri/ | 2053 |

---

## Stan treści

### Kierunki (/pl/kierunki/)
| Strona | PL | EN |
|--------|----|----|
| Reggio Calabria | ✅ 2168 | ✅ 2030 |
| Tropea | ✅ 2173 | ✅ 2035 |
| Bova | ✅ 2185 | ✅ 2047 |
| Catanzaro | ✅ 2190 | ✅ 2052 |
| Scilla | ✅ 2177 | ✅ 2039 |
| Pizzo | ✅ 2181 | ✅ 2043 |
| Gerace | ✅ 2187 | ✅ 2049 |
| Stilo | ✅ 2188 | ✅ 2050 |
| Cosenza | ✅ 2189 | ✅ 2051 |
| Locri | ✅ 2191 | ✅ 2053 |

### Natura (/pl/natura/) — zlecenia w Supabase (2026-03-11)
| Strona | Supabase ID | PL | EN |
|--------|-------------|----|----|
| Park Narodowy Aspromonte | 48a939d0-8072-425b-bdbd-e84a97adb1cd | ⏳ | ⏳ |
| Park Narodowy Sila | b5909f0e-aefe-4a70-8f7a-c982ec1a8d1c | ⏳ | ⏳ |
| Park Narodowy Pollino | aa9d6c90-928d-4e44-a4d5-deebbbe36389 | ✅ 2195 | ✅ 2057 |
| Najlepsze plaże Kalabrii | 6eaa07ad-68c9-47c8-8150-f2ec8c291d7e | ✅ 2196 | ✅ 2058 |
| Capo Vaticano | 3013a1c5-3cc0-4033-aa87-547950caf18b | ✅ 2197 | ✅ 2059 |
| Costa Viola | b2708b71-1ec6-415f-a15d-03dfe2220626 | ✅ 2198 | ✅ 2060 |

---

## Generowanie obrazów (generate-image.js)

### Tryb generowania (domyślny)
`node generate-image.js --prompt "..." --slug "slug" --alt "alt" [--caption "..."]`
- Model: `nano-banana-2`, rozdzielczość **1K (1024×576, 16:9)**

### Tryb edycji (na bazie istniejącego zdjęcia)
`node generate-image.js --prompt "..." --slug "slug" --alt "alt" --edit-from "URL_zdjecia" [--caption "..."]`
- Model: `google/nano-banana-edit`, format 16:9
- Użyj gdy masz realne zdjęcie miejsca i chcesz je zmodyfikować (oświetlenie, pora dnia, usunięcie elementów)

Oba tryby: auto-upload do WP, wypisują gotowy blok Gutenberg. Obraz inline w treści (NIE featured image).

### Styl promptu dla Kalabrii
```
Photorealistic travel photography, [OPIS MIEJSCA/OBIEKTU], Calabria, southern Italy.
Golden hour lighting, vivid Mediterranean colors, high detail.
No text, no watermarks, no people in foreground.
```

### Szablon bloku Gutenberg (wypisywany przez skrypt automatycznie)
```
<!-- wp:image {"id":MEDIA_ID,"sizeSlug":"large","linkDestination":"none","align":"center"} -->
<figure class="wp-block-image aligncenter size-large"><img src="URL" alt="ALT" class="wp-image-MEDIA_ID"/>
<figcaption class="wp-element-caption"><em>Podpis.</em></figcaption></figure>
<!-- /wp:image -->
```

### Kiedy wstawiać obraz w treści
- Wstaw po 2. lub 3. sekcji H2 (środek artykułu)
- NIE na początku, NIE bezpośrednio przed boc-boxes

---

## Monetyzacja (planowana)
- Booking.com affiliate — do wdrożenia po dopracowaniu treści
- Google AdSense — do wdrożenia
- Loty (Skyscanner/Kiwi) — opcjonalnie

---

## Styl typograficzny\n- Używaj **półpauzy** (–) nie pauzy (—) — w tytułach, nagłówkach i treści\n- W HTML: `&ndash;` = półpauza (–), `&mdash;` = pauza (—) — używamy ndash\n\n## Notatki techniczne
- Login WP: `admin` (nie `sibilian` jak w bas-3)
- Strony to `pages`, NIE `posts`
- Plugin językowy: **Polylang** — obie wersje to osobne strony WP powiązane przez Polylang
- Flaga językowa pokazuje złą stronę? Sprawdź kosz WP — Polylang może się przyczepiać do usuniętych duplikatów
- `google/nano-banana-edit`: output_format musi być `jpeg` (nie `jpg`) — `jpg` zwraca błąd
- Zdjęcie podane jako URL lokalny → najpierw uploaduj do WP media, żeby dostać publiczny URL dla kie.ai
- Przy edycji zdjęcia ze stocków (Dreamstime itp.) — lepiej użyć czystego źródła (np. calabriastraordinaria.it)
- Badolato (prowincja Catanzaro) — dobre zdjęcie reprezentatywne dla regionu Catanzaro

## Stan 2026-09-12
- Każda strona contentowa (PL+EN, 160 plików) kończy się ramką `boc-sources-box` (Źródła) – generator `fact-checker/gen_sources.py` (katalog fact-checker/ poza repo)
- 15 stron miast/parków ma planer dojazdu `boc-transport-box boc-planner` (select „Skąd jedziesz?”: lotniska SUF/REG, Polska, Rzym/Neapol, sąsiedzi) zamiast statycznej siatki – dane `fact-checker/planner/*.json`, skrypty `planner_gen.py` i `planner_apply.py`; JS w baseof.html
- Ikony transportu wg klas `boc-t-plane|car|train|bus|ferry|walk|taxi`, nie wg pozycji
- Hero strony głównej = własne zdjęcie Scilli; karty na homepage = realne zdjęcia (own/commons)

## Stan 2026-09-12 (2) – widget pogodowy
- Sidebar zaczyna się od ramki `boc-weather` (partial `layouts/partials/weather.html`): teraz + odczuwalna + wiatr + temperatura morza (strony z `sea: true`) + prognoza 6 dni; dane Open-Meteo bez klucza, wołane z przeglądarki, cache 30 min w sessionStorage; JS w baseof.html, CSS v=39
- Współrzędne w frontmatterze: `geo: [lat, lon]`, `sea: true|false`, opcjonalnie `weatherLabel:` (parki górskie – miejscowość i wysokość). 15 stron PL+EN (10 miast, 5 natura); podstrony atrakcji dziedziczą z `.Parent`
- `geo` trafia też do schema TouristDestination jako GeoCoordinates
- Licencja Open-Meteo: darmowa do użytku niekomercyjnego – przy wdrożeniu AdSense/affiliate rozważyć plan płatny albo Cloudflare Worker z cache

## Stan 2026-09-12 (3) – publikator FB + plan bloga
- Strona FB: https://www.facebook.com/poznajkalabrie/ – parametr `facebook` w hugo.toml; użyty w stopce (`.footer-social`), ramce `boc-fb-cta` (partial fb-cta.html: „Skomentuj na Facebooku” + „Udostępnij”, pod treścią nad author-boxem, nie na o-nas/kontakt/wspolpraca) i w schema Organization `sameAs`
- Auto-publikator Facebook: `.github/workflows/fb-daily-post.yml` (cron 18:00 UTC + ręczne `dry_run` / `pick`), skrypt `scripts/fb_publish.py`, testy `scripts/test_fb_publish.py`, stan `.fb-published.json` (commit bota po każdym poście), instrukcja tokenów `docs/FB_SETUP.md`
- Pula: 80 stron z content/pl (bez homepage, listingów sekcji, kontakt/o-nas/wspolpraca); tekst posta z OpenRouter (chat completions, reasoning low), publikacja przez webhook Make.com; FB post = message + link (podgląd z Open Graph)
- Format posta: zdjęcie hero (og:image) + podpis, link w pierwszym komentarzu. Scenariusz Make: Webhook → HTTP Get a file (image) → Facebook Pages Upload a Photo (File name stałe `zdjecie.webp`, Data z HTTP, caption=message) → Create a Comment (Post ID z modułu zdjęcia, text=comment). Po edycji scenariusza sprawdzić przełącznik „Immediately as data arrives” – Make wyłącza go przy zapisie. Odpowiedź webhooka to „Accepted” (bez id posta) – TODO: moduł Webhook response
- Sekrety GitHub: `OPENROUTER_API_KEY` (model openai/gpt-5.6-luna) i `FB_WEBHOOK_URL` (Make.com → Facebook Pages, bez konta dewelopera Meta) ustawione; publikator działa od 2026-09-12, pierwszy post: Tropea
- Open Graph: og:image = obraz hero (partial `hero-image.html`), fallback hero-calabria.webp
- Plan bloga: `docs/blog-content-plan-2026-2027.md` – 24 wpisy PL+EN, kalendarz 2/mies. paź 2026–wrz 2027, luki w Kierunkach (Scalea, Parghelia, Soverato, Lamezia)

## Stan 2026-09-13 – pływające skróty
- `.boc-float` w baseof.html (poza homepage): przycisk `.boc-float-top` („Do góry”, po 700 px scrolla) + `.boc-float-weather` (tylko ≤960 px i tylko gdy jest `.boc-weather`) – pigułka z ikoną i temperaturą z renderu widgetu, przewija do widgetu, chowa się gdy widget widoczny (IntersectionObserver); CSS v=42

## Stan 2026-09-13 (2) – blog: pierwsze wpisy z planu
- OPUBLIKOWANE 2026-09-14 (commit 988c363): #1 „Kalabria – co zobaczyć? 25 miejsc” (`content/pl/blog/kalabria-co-zobaczyc.md` / `content/en/blog/things-to-do-in-calabria.md`) i #2 „Pogoda w Kalabrii miesiąc po miesiącu” (`pogoda-w-kalabrii.md` / `calabria-weather-by-month.md`), date 2026-09-14 zamiast kalendarzowych 1 i 15 października; oba po redakcji użytkownika
- Format wpisu .md: frontmatter (title, slug, date, translationKey, image, description) + Markdown z surowym HTML (boc-toc, boc-faq-box, boc-sources-box, figure boc-photo); nagłówki `## Tytuł {#id}` pod kotwice spisu treści
- Przyszła data = wpis niewidoczny do tego dnia (Hugo bez buildFuture)
- TODO: linki zwrotne z 2–3 stron encyklopedycznych (Tropea, Jak dojechać, Plan na 7 dni); kolejne wpisy z planu: #3 Mapa Kalabrii, #9 Czy Kalabria jest bezpieczna + E1 Where is Calabria

## Stan 2026-09-14 – powiązane wpisy na blogu
- Partial `layouts/partials/related-posts.html` w `layouts/blog/single.html` pod author-boxem: sekcja „Przeczytaj też” / „Read next” – do 3 najnowszych innych wpisów z bloga w tym samym języku (bez tagów, sortowanie po dacie), karty `.blog-card` z `image:` z frontmattera
- CSS `.boc-related` (v=43): 3 kolumny na desktopie, poziome karty z miniaturą 110×80 na ≤600 px; nadpisuje `.page-content h3` (kreska, niebieski)
- Hugo server na /mnt/c w WSL nie wykrywa zmian w plikach – po edycji CSS/szablonów restartować serwer
