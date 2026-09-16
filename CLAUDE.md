# CLAUDE.md — projekt bestofcalabria.com
# Pełna wiedza operacyjna. Aktualizuj po każdej sesji.

---

## Uprawnienia operacyjne

- Wszystkie komendy bash (curl, python, node) — **wykonuj bez pytania o potwierdzenie**
- Wyjątki wymagające akceptu użytkownika:
  - Usuwanie plików lub treści (rm, DELETE do API)
  - Generowanie dodatkowych obrazów (generate-image.js) — kosztuje kredyty

---

## Hosting i publikacja
- Od 2026-03-17 strona to **Hugo + Cloudflare Pages** (repo github.com/sibilianspirit/calabria, auto-deploy z `main`); WordPress wyłączony – nie używać wp-json, ID stron ani bloków Gutenberg
- Treść: `content/pl/` i `content/en/` (pliki .md/.html z frontmatterem); publikacja = build Hugo → commit → push
- Środowisko: Windows 11, Claude Code z narzędziem PowerShell (główne) i Bash (Git for Windows); Hugo Extended natywnie na Windows (wcześniej w WSL)

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
2. Edytuj plik w `content/pl/` (ścieżka wg URL)
3. Przetłumacz treść na EN (zachowaj strukturę `boc-` CSS) i zapisz w odpowiedniku w `content/en/` (mapowanie URL PL→EN jak powyżej)
4. Build Hugo → commit → push na `main`

---

## Szablon strony (format `boc-`)

Wzorcowa strona: https://bestofcalabria.com/pl/kierunki/reggio-calabria/

Sekcje obowiązkowe (w kolejności):
```
[intro akapit — bez H1, tytuł jest we frontmatterze]
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

---

## Generowanie obrazów (generate-image.js)

### Tryb generowania (domyślny)
`node generate-image.js --prompt "..." --slug "slug" --alt "alt" [--caption "..."]`
- Model: `nano-banana-2`, rozdzielczość **1K (1024×576, 16:9)**

### Tryb edycji (na bazie istniejącego zdjęcia)
`node generate-image.js --prompt "..." --slug "slug" --alt "alt" --edit-from "URL_zdjecia" [--caption "..."]`
- Model: `google/nano-banana-edit`, format 16:9
- Użyj gdy masz realne zdjęcie miejsca i chcesz je zmodyfikować (oświetlenie, pora dnia, usunięcie elementów)

Skrypt pochodzi z ery WordPressa (upload do WP media) – przed użyciem dostosować do Hugo (zapis do `static/images/`). Obraz inline w treści (NIE featured image).

### Styl promptu dla Kalabrii
```
Photorealistic travel photography, [OPIS MIEJSCA/OBIEKTU], Calabria, southern Italy.
Golden hour lighting, vivid Mediterranean colors, high detail.
No text, no watermarks, no people in foreground.
```

### Obraz w treści
Format jak we wpisach blogowych: `<figure class="boc-photo">` z `<figcaption>` i atrybucją `.boc-photo-credit`.

### Kiedy wstawiać obraz w treści
- Wstaw po 2. lub 3. sekcji H2 (środek artykułu)
- NIE na początku, NIE bezpośrednio przed boc-boxes

---

## Monetyzacja (planowana)
- Booking.com affiliate — do wdrożenia po dopracowaniu treści
- Google AdSense — do wdrożenia
- Loty (Skyscanner/Kiwi) — opcjonalnie

---

## Styl typograficzny
- Używaj **półpauzy** (–) nie pauzy (—) — w tytułach, nagłówkach i treści
- **Od 2026-09-16: w `content/` piszemy czyste znaki UTF-8, nie encje HTML** – półpauza to `–`, nie `&ndash;`; tak samo `ó`, `„ ”`, `à/ò/é`, `€`, `°`. Powód: encje wyciekały jako goły tekst do RSS (`&amp;ndash;`) i do JSON-LD (`&ndash;`) – w kanałach i danych strukturalnych czytelnik/robot widział dosłowne „&ndash;”. Cały katalog przekonwertowany jednym przebiegiem (169 plików, 6174 encje)
- Nadal zostawiamy encje składniowe i niewidoczne: `&amp;` `&lt;` `&gt;` `&quot;` `&nbsp;` `&#39;` `&#x27;` (te ostatnie w atrybutach)

## Notatki techniczne
- Wersje językowe: osobne pliki w `content/pl/` i `content/en/` powiązane przez `translationKey`
- `google/nano-banana-edit`: output_format musi być `jpeg` (nie `jpg`) — `jpg` zwraca błąd
- Zdjęcie podane jako URL lokalny → najpierw udostępnij publicznie (np. `static/images/` po deployu), żeby dostać URL dla kie.ai
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
- Hugo Extended 0.147.4 działa natywnie na Windows (winget, od 2026-09-15) – nie budować przez WSL (tam `hugo server` na /mnt/c nie wykrywał zmian)

## Stan 2026-09-14 (2) – Jak dojechać + Wynajem samochodu (PL+EN)
- „Jak dojechać”: nowa sekcja „Loty z Polski” (tabela lato 2026 / zima 2026/27: KTW–REG Ryanair do 22.10.2026, skasowane na zimę; KTW–SUF Wizz+Ryanair, WAW Wizz, WMI Ryanair – sezonowe; KRK i WRO–SUF Ryanair także zimą; LOT NIE lata do SUF), przesiadki zimą, transfery z REG i SUF (ATAM 1,50 €, Airlink 1,80 €, taxi), koszt paliwa wg MIMIT ~2,10 €/l
- „Wynajem samochodu”: wypożyczalnie wg SACAL (SUF 11 firm, REG tylko Noleggiare/Sicily by Car/Sixt ~250 m, CRV Avis/Violauto), sekcja porównywarek, kaucje/udział własny, kara AGCM za opłaty za mandaty, tabele czasów przejazdu z SUF/REG, parkingi Scilla/Tropea/Pizzo, ZTL Reggio/Cosenza, 3 nowe FAQ
- Ramka linków = `boc-info-box` + `boc-info-table` (linki-przyciski, rel="nofollow noopener"); przy wdrożeniu afiliacji DiscoverCars/Rentalcars dodać `sponsored`. CSS v=44 (margin 0 tabeli w boc-info-box)
- KTW–REG lata w poniedziałki i czwartki (potwierdzone przez użytkownika) – poprawione w 6 planerach PL+EN i na Jak dojechać. TODO: po 22.10.2026 zmienić wpisy Katowice→REG w planerach i na stronie (trasa skasowana na zimę)
- Tytuły plan-7-dni / itinerary-7-days: `&ndash;` w YAML → „–” (encja wyświetlała się dosłownie w sidebarze)
- Rozkłady Ryanaira: publiczny endpoint `https://services-api.ryanair.com/timtbl/3/schedules/{FROM}/{TO}/years/{Y}/months/{M}` (bez klucza, curl działa). Stan 14.09.2026: KTW–REG pn/czw do 22.10; KTW–SUF wt/czw/sob do 24.10; WMI–SUF pn/pt do 23.10; KRK–SUF lato pn/śr/sob/nd, zima zwykle śr/sob/nd; WRO–SUF jesień pn/pt, zima pn/sob; lato 2027 nieopublikowane. Wizz Air – patrz niżej

## Stan 2026-09-14 (3) – rozkład Wizz Air z API
- Wizz timetable działa przez curl: wersja API z HTML strony głównej (`apiUrl:"https://be.wizzair.com/29.16.1/Api"` – zmienia się), `POST {apiUrl}/search/timetable` z `{"flightList":[{"departureStation","arrivalStation","from","to"}],"priceType":"regular","adultCount":1,...}`, okno ≤30 dni; `GET {apiUrl}/asset/map?languageCode=pl-pl` = siatka połączeń. `search/search` blokuje Kasada (429), po ~50 zapytaniach 503 – odczekać
- Stan 14.09.2026: KTW–SUF wt/czw/sob, od 24.09 tylko wt/sob, ostatni lot 17.10 (lotniska w maju podawały 24.10; potwierdzone przez użytkownika w kalendarzu wizzair.com – 20–24.10 wyszarzone, nie „wyprzedane”), powrót 30.03.2027, od czerwca 2027 także nd; WAW–SUF pn/śr/pt do 23.10, powrót 29.03.2027. Zimą 2026/27 brak lotów Wizz z Polski
- Tabela na Jak dojechać PL+EN poprawiona; planery (lato 2026: KTW wt/czw/sob, WAW pn/śr/pt) bez zmian

## Stan 2026-09-15 – fact-check redaktorski + poprawki systemowe
- Użytkownik robi własny fact-check stron PL (zrzut w Downloads/calabria-pl, manifest nazw) i odsyła pliki etapami; katalog błędów w pamięci `feedback_fact_check_errors.md`. Poprawki redaktora weryfikować u źródła – zdarzają się błędne (Parapezza, godziny zamku Ruffo)
- Wgrane: Locri, Scilla, Stilo, Costa Viola (PL; do EN tylko merytoryka). Stilo: odległości wg OSRM, droga SS110 (nie SP9), Duomo = Santa Maria d’Ognissanti (nie św. Wawrzyniec) także na podstronach PL+EN
- Planery „Z Rzymu lub Neapolu” w 16 stronach PL+EN przepisane wg rozkładu e656.net: FR/Italo oddzielnie od Intercity (Rzym–Reggio FR 5,5–6 h, IC 7,5–8,5 h; Rzym–Lamezia FR 4–4,5 h, IC 5,5–6,5 h; Rzym–Villa S.G. FR 5–5,5 h). Z Rzymu brak bezpośrednich pociągów do Scilli, Bagnary, Palmi; Cosenza przez Paolę (Lamezia–Cosenza bez bezpośrednich)
- Spis treści: H2 nie dostają automatycznych id – dodano 107 brakujących id w 17 plikach PL+EN; każdy nowy boc-toc wymaga jawnych id
- Włoskie nazwy muzeów w polskich zdaniach przetłumaczone i odmienione (Narodowe Muzeum Archeologiczne w Reggio Calabria); zostają w tytułach źródeł i filmów
- Do końca dnia wgrane także: Capo Vaticano, Tropea, Pizzo, Jak dojechać, Gerace, Bova, Cosenza, Pollino (ostatni commit 7a9cf18). Redaktor pracuje na starym zrzucie – planery i id nagłówków brać z bieżącego pliku. Konkatedra tylko na stronach głównych Gerace i Bovy (podstrony „katedra” zostają – decyzja użytkownika)
- TODO: planer Pollino „Z Rzymu lub Neapolu” prowadzi przez Lamezię – sprawdzić wariant przez Sibari/Paolę

## Stan 2026-09-16 – fact-check redaktorski: Pollino (2), Catanzaro, Sila
- Wgrane PL+EN: Pollino (druga tura, d83c7e9), Catanzaro (691d04c, e6e116b), Sila (7bc0a27)
- Zjazd A2 oficjalnie **Frascineto – Castrovillari** (nie Castrovillari-Frascineto) – poprawione w planerach i `fact-checker/planner/natura__pollino.json`
- Catanzaro: centrum na trzech wzgórzach (Tre Colli, doliny Fiumarella i Corace), NIE na cyplu; dodany Il Cavatore (Giuseppe Rito 1951–1954, odsłonięta II 1956); usunięta bergamotka i dwa niezwiązane źródła; Reggio → Catanzaro 1 godz. 50 min – 2 godz. (OSRM 157 km/111 min)
- Sila: odmiana „Sili” w całym tekście; wiewiórka kalabryjska *Sciurus meridionalis* = odrębny gatunek (2017); Monte Paleparto 1481 m; odległości od Camigliatello wg OSRM – Catanzaro 130 km (nie 50; 50 dotyczyło Sili Piccola), Pizzo 120, Tropea 145, Pollino 100, Aspromonte 210 (było błędne 95)
- Wnioski: propozycje redaktora przyjmować wybiórczo, każdą liczbę sprawdzać w OSRM/u źródła – bywają zaniżone albo niepewne
- Reggio Calabria (5f1b524): PL+EN – usunięte frazesy (perły/palimpsest/z popiołów), Sztaufowie, fikusy wielkolistne (Ficus magnolioides ≠ magnolia), fata morgana małą literą, „ponad 13,5 mld euro”, 120 000 miejsc pracy zamiast ULA, port bez „TEU”, PRG/PSC zastąpione ogólną formułą; Greko = górskie wioski Bovesii. Zweryfikowane: Bova→Reggio 53 km/64 min (Bova Marina 43 km/48 min), pociąg SUF→Reggio 1 godz. 35 min–1 godz. 45 min (FR i szybkie R), wolne regionalne do 2 godz. 45 min (Trenitalia lefrecce API, nie 2 godz. 40 min ani 1 godz. 20 min z redakcji). Nazwa muzeum zostaje po polsku wbrew redakcji (decyzja z 15.09)
- Dziedzictwo bizantyjskie (5d6bdaa): PL+EN – normański podbój zamiast „normandzkiej konkwisty”, nazwy jednostek administracyjnych małą literą (egzarchat Rawenny, katepanat Italii), Matka Boża Hodegetria, „nieuczyniony ludzką ręką”, baptysterium, Bovie/Bovy (odmiana), Centrum Informacyjne zamiast „Centrum Wizytowe”. Dodane: akapit o Gerace (kolumny z reużycia z Lokroi Epizephyrioi), SS106 Jonica, szlak 4–5 dni zamiast 2–3. Zweryfikowane: Bivongi San Giovanni Theristis – od 2008 mnisi Rumuńskiego Kościoła Prawosławnego (99-letnia koncesja gminy), od 1994 wcześniej mnisi z Athosu (it.wikipedia)
- W pliku PL dziedzictwa bizantyjskiego były encje `&oacute;` i kotwice z polskimi znakami (jedna zepsuta: `wsp-oacute-lnoty`) – encje rozkodowane do znaków, id nagłówków przepisane na ASCII. Encje w całym `content/` rozkodowane osobnym commitem – patrz sekcja „Styl typograficzny”
- TODO nadal otwarte: planer Pollino „Z Rzymu lub Neapolu” przez Lamezię – sprawdzić wariant przez Sibari/Paolę
