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

## Stan 2026-09-16 (2) – fact-check redaktorski: Magna Graecia
- Magna Graecia PL+EN (68858ca): fleksja (Kroton rodz. męski – słynął/zniszczył/pokonał, dzisiejsze Rosarno, po Tropeę, Bruttowie, wojna z Pyrrusem), „Calabria” → Kalabria, „Język greko kalabryjskie” → „Język greko (greka kalabryjska)”, Cattolica di Stilo = zabytek bizantyjski „a nie starożytny” (nie „nie grecki” – Bizancjum było greckojęzyczne)
- Kotwice: id nagłówków przepisane na ASCII (były polskie znaki + zepsute `wsp-oacute-łczesnej`, `grek-oacute-w` po konwersji encji) – ten sam problem co w dziedzictwie bizantyjskim
- Odległości wg OSRM: Reggio → Locri **110 km / ~1,5 godz.** (w tekście było 75, redaktor proponował 95 – oba za mało), Locri → Monasterace 45 km (było 35), Monasterace → Crotone 115 km, Capo Colonna 11 km od Crotone
- Brązy z Riace: dodany odkrywca – płetwonurek-amator Stefano Mariottini, 16.08.1972, ok. 220 m od brzegu (redaktor podawał 300 m i „rzymski chemik” – it.wikipedia potwierdza tylko nurkowanie amatorskie)
- Przelot po kotwicach w całym `content/` (eac3643): 64 id z wtopionymi encjami (`-ndash-`, `-oacute-`, `-eacute-`, `-deg-`, `rsquo`, `8217`) w 17 plikach przepisane na czyste slugi generowane z treści nagłówka; id i href zmieniane razem
- **Decyzja: id z polskimi znakami zostają** (207 sztuk w 71 plikach, np. `id="wpływ-wodospadów-marmarico"`). Działają poprawnie, w URL-u kodują się na `%C5%82`; przepisanie unieważniłoby zaindeksowane fragmenty „przejdź do sekcji”, a zysk byłby czysto kosmetyczny. Nie wracać do tematu
- Weryfikacja kotwic: budować i skanować `public/`, nie `content/` – w plikach .md (blog) id nagłówków generuje Hugo, więc skan źródeł pokazuje fałszywe „wiszące href”. Stan po przelocie: 164 strony z TOC, 0 martwych kotwic

## Stan 2026-09-16 (3) – fact-check redaktorski: Najlepsze plaże
- Plaże PL+EN (b33ed11): usunięte banały (raj dla miłośników plaż, ukryte piękno, dzikie piękno, Perła Morza Tyrreńskiego/Jońskiego, Mała Wenecja południa, odskocznia od plaż); „lidos” → `lidi`; dodane włoskie nazwy pomocne w terenie: `torri costiere`, `Bandiera Verde`, `Paradiso del Sub`, `cipolla rossa di Tropea Calabria IGP`, Cirò DOC
- **Błędy merytoryczne**: Tropea i Capo Vaticano leżą na tym samym (zachodnim) wybrzeżu – porównanie zmienione na Tropea ↔ Soverato; Scilla jest na Costa Viola, nie na Costa degli Dei – w akapicie o bazie wypadowej z Tropei zastąpiona Pizzem
- **Liczby**: wybrzeże Kalabrii **blisko 790 km** (it.wikipedia 788,92 km; w treści było 740, w description „ponad 800” – ujednolicone); Area Marina Protetta Capo Rizzuto **blisko 15 tys. ha** (14 721, największy rezerwat morski Włoch; było 8 tys.); Fossa del Tirreno 3785 m; Głębia Kalipso nazwana z ostrożnym „przekracza 5000 m”
- **Ordinanza n.12 z 30.04.2026 (Arcomagno) jest prawdziwa** – potwierdzona na stronie comune.sannicolaarcella.cs.it (HTTP 200). Redaktor uznał ją za halucynację AI; szczegół usunięty ze stylistycznego powodu (dla czytelnika bezużyteczny), ale źródło zostaje i potwierdza, że wstęp bywa biletowany
- „Czubek włoskiego buta” zostaje – decyzja użytkownika wbrew propozycji redaktora („nos”)
- **Znalezione przy okazji: dwie martwe kotwice w intro** (`#tropea-klejnot-kalabrii`, `#ukryte-uroki-wybrzeza-jonskiego` i ich odpowiedniki EN) – linki w treści, poza `boc-toc`. Naprawione. Wniosek: skan kotwic musi obejmować **każdy** `href="#"` na stronie, nie tylko te wewnątrz ramki TOC. Po naprawie: 189 stron, 0 martwych kotwic w całym serwisie

## Stan 2026-09-16 (4) – fact-check redaktorski: Plaże Costa degli Dei
- Costa degli Dei PL+EN (27a5598), `content/pl/kierunki/pizzo/plaze-costa-degli-dei/` i `content/en/destinations/pizzo/costa-degli-dei-beaches/`
- **Błąd merytoryczny**: kitesurfing i windsurfing nie są domeną Tropei ani Capo Vaticano – ośrodkiem jest **Gizzeria Lido** (Hang Loose Beach, termiczny NW 12–25 węzłów); osłonięte zatoki Costa degli Dei służą do snorkelingu i nurkowania
- **Pociągi**: Intercity i Frecce omijają nadmorski odcinek – zatrzymują się na stacji Vibo Valentia-Pizzo w głębi lądu i jadą do Rosarno; na wybrzeżu (Pizzo, Zambrone, Parghelia, Tropea, Ricadi, Nicotera) tylko Regionale. Vibo Valentia-Pizzo usunięta z listy stacji nadmorskich
- Nazewnictwo: Santa Maria dell'Isola to **sanktuarium**, nie bazylika; „wieże saraceńskie” → wieże strażnicze (`torri costiere` – budowano je przeciw Saracenom, nie Saraceni); kalki usunięte: *pisciny*, *nielegalna pesca*, *fondale*, *nursery*, *trasa tirreńska*
- Liczby: Michelino – główne schody **210 stopni**, z rampami dojścia **ok. 240** (redaktor podawał „dokładnie 210”); SUF → Tropea **55 km / 61 min** wg OSRM (w tekście było 1 h 10–1 h 30, redaktor proponował 1 h–1 h 15; przyjęte 1 h–1 h 20 + uwaga o Ferragosto)
- **Nie przyjęte z redakcji** (oryginał był ostrożniejszy lub precyzyjniejszy): numer ustawy regionalnej 13/2008 parku morskiego i kod Natura 2000 IT9340093 zostają; widoczność 30 m zostaje z atrybucją do centrów nurkowych (redaktor zrobił z tego twierdzenie); historia IGP Tartufo di Pizzo (projekt 2007, ochrona krajowa 2008) zostaje zamiast ogólnego „status PAT”; Bandiera Blu z konkretną edycją 2026 zostaje
- Konfitura z cebuli: w handlu funkcjonują obie nazwy – `marmellata` (potocznie, częściej na etykietach) i `confettura` (technicznie poprawna); oryginalne `confettura` nie było błędem, spolszczone na „słodka konfitura” z nazwą z etykiety

## Stan 2026-09-16 (5) – fact-check redaktorski: Muzeum Diecezjalne w Gerace
- PL+EN (234eedd): arazzo → gobelin, corali → księgi chórowe, pala d'altare → obraz ołtarzowy (nie „nastawa” – to obraz), spolia jako kolumny z odzysku, ikoniczny → rozpoznawalny; nagłówek „Tkaniny i flamandzki gobelin” (nowe id), description przepisany (był ucięty „…”)
- Imiona: Roger de Hauteville (wł. Ruggero d’Altavilla), Atanazy Chalkeopulos (gr. Χαλκεόπουλος; redaktor pisał „Chalkiopoulos” i odmieniał włoskie „Ruggera”), Hagia Kyriake (św. Cyriaki)
- Gobelin: sygnowany przez Jana Leyniersa, ok. 1673–1680, projekt Le Bruna; temat – epizod z mitu o Meleagrze, identyfikacja sceny niepewna (źródła: spotkanie z Ojneusem / pożegnanie z Kastorem). Informacji o zamówieniu przez Fouqueta NIE dodawać – Fouquet upadł w 1661
- Nie przyjęte: „Jerozolima Południa” (niezweryfikowany przydomek; zostało „miasto stu kościołów”), „1059–1062” zamiast 1062, frazesy „prawdziwa gratka” / „miejsce, którego nie można pominąć”, encje `&ndash;` z tekstu redaktora

## Stan 2026-09-17 – fact-check redaktorski: Muzeum MARCA (Catanzaro)
- PL+EN: nagłówek „dialog modernizmu z tradycją” → „nowe życie zabytkowego pałacu”; FAQ bez włoskich wtrąceń (scivoli/rampe, ascensore, parcheggio riservato); Mimmo Rotella/Paladino odmienione (Mimma Rotelli), w Tavernie, w Polistenie
- **Błąd redaktora**: Palazzo Marincola di San Floro to pałac **XVI-wieczny**, nie XIX-wieczny; związek z przemysłem jedwabniczym niepotwierdzony – nie dodany. Instytut dla głuchoniemych i drukarnia – potwierdzone w karcie usług
- Diamante ← Catanzaro wg OSRM **136 km / ok. 2 godz. 15 min** (w tekście było 175–190, redaktor 130)
- Bilety wg FAI: całe muzeum 8 € / ulgowy 6 €, dwie sale 6/4 €, wystawa czasowa 4/3 €; Mendini (wejście, księgarnia, czytelnia, od 2009) i Fabre „L'uomo che misura le nuvole” (1998) w parku – potwierdzone

## Stan 2026-09-17 (2) – fact-check redaktorski: San Giovannello (Gerace)
- PL+EN: „perła” → „bizantyjski zabytek”, nagłówek „Morfologia… intencjonalnej niedoskonałości” → „Architektura i forma budowli” (nowe id), sanacja → konserwacja, dach dwuspadowy (wł. *a capanna*), usunięty powtórzony katolikon, Kasa Południa, Soprintendenza z objaśnieniem, miasto metropolitalne małą literą
- **Nie przyjęte z redakcji**: „griko” (to dialekt Salento – zostaje greko / greka kalabryjska); wysokość „470 m” – it.wikipedia podaje 500 m, wpisane „blisko 500 m”; daty skanu 2023 i fotogrametrii 2024 zostają
- Droga Locri → Gerace to **SP1 (dawna SS111)** – redaktor miał rację; najpierw błędnie wpisane SS111, poprawione przy planie 7 dni (OSM/OSRM, strona Gerace _index)
- Barlaam nauczycielem Petrarki **i Boccaccia** – zostaje (it.wikipedia, epigraf w Gerace); OSRM Locri → Gerace 9,3 km / 14 min

## Stan 2026-09-17 (3) – fact-check redaktorski: Kalabria w 7 dni
- PL+EN: kalki „Tirrenian”, „miradory”, „klejnot”, „czubek buta”; ’nduja z apostrofem; opis tartufo di Pizzo; Mesyna (nie Messyna); fata morgana małą literą; Santa Maria dell'Isola = sanktuarium
- Trasy wg OSRM: **SUF → Tropea 55 km / 62 min przez SS18 i dawną SS522 (SP95), bez A2**; Scilla → Reggio 23 km / 22 min; Bova → Gerace 74 km / 85 min; **Gerace → Stilo 58 km / 61 min** (było 70); **Stilo → SUF 100 km / 1 godz. 45 min** (było 130 km, 1,5–2 h). Reggio → Bova zostaje „około godziny” (53 km / 64 min) – redaktor proponował 1 h 15
- **„Najpiękniejszy kilometr Włoch” to fałszywy cytat D'Annunzia** (it.wikipedia wg historyka Agazio Trombetty: poeta nie był w Reggio; frazę rozpowszechnił Nando Martellini w radiu 27.03.1955) – opisane jako legenda
- Rada „tankuj diesel” zastąpiona self/fai da te vs servito; FAQ: bez auta centra Bovy, Gerace i Stilo praktycznie niedostępne; SS110 Stilo–Serra kręta

## Stan 2026-09-21 – fact-check redaktorski: Zamek Gerace, Kaulon, Locri park, Kuchnia (blog), Marina Grande
- PL+EN wgrane: zamek w Gerace (35d0aa2), Kaulon (4c5934b), park archeologiczny Locri (4971744), blog Kuchnia kalabryjska (198af52), plaża Marina Grande w Scilli (5a903c9)
- **Błędy redaktora**: „cysterna” w zamku Gerace – źródła gminne i exploregerace mówią *pozzo* (studnia); cena biletu Kaulon 5 € – wg Itinerari Archeo Calabria 4 € / 2 €; powierzchnia parku Locri 300 ha – italia.it podaje „oltre 230 ettari”; „odlewano pinakes” (terakotę się formuje, nie odlewa); „restauracje na palach” w Chianalei
- **Błąd w tekście, redaktor miał rację**: IGP Peperoncino di Calabria wpisane do rejestru UE **11.06.2026** (rozporządzenie wykonawcze 2026/1273), nie „GU n. 142 z 22.06”. Chianalea faktycznie jest w I Borghi più belli d'Italia (borghipiubelliditalia.it/en/borgo/chianalea)
- Zamek Gerace: SP1 (dawna SS111), Locri→Gerace ok. 15 min; wieża narożna zniszczona 1943; CIS poz. A2_120, 2,5 mln €, priorytet średni. Kaulon: park–Stilo ok. 15 km (OSRM ~14,6 km); mozaik ze smokiem są co najmniej dwie („Casa del Drago” III w. p.n.e. i term Casamatta) – nie pisać, że „smok to symbol Monasterace”
- Zasada: pliki z Downloads bywają starsze lub nowsze od repo w różnych akapitach – zawsze diff i wybór zdanie po zdaniu; encje HTML z pliku redaktora konwertować na UTF-8 (zostawić tylko `&nbsp;` itp.)
- Skrypty jednorazowe pisać do pliku (Write), nie w heredocach Bash z zagnieżdżonym `EOF`; po edycji: hugo → skan `href="#"` w `public/` → commit tylko `content/` → pull --rebase z tokiem sibilianspirit → push
- Niepewne: święto San Rocco w Scilli (piątek–niedziela po 16.08 wg tekstu vs „pierwszy weekend po 16.08” wg redaktora; źródło potwierdza tylko 16.08); cena panino ze Scilli 10–20 € niezweryfikowana; ceny biletu Locri 5 € niezweryfikowane

## Stan 2026-09-21 (2) – fact-check redaktorski: Sentiero dell'Inglese, zamek Cosenza, blog Plaże, Noclegi, dziedzictwo grekanickie, muzeum i plaże Locri
- PL+EN wgrane: Sentiero dell'Inglese (8023cea, 377a125), zamek w Cosenzie (6cc932b), blog Najlepsze plaże (611e1d8), Noclegi (dfa237d), dziedzictwo grekanickie w Bovie (92bb6b2), Muzeum Narodowe w Locri (c19f309), Plaże Marina di Locri (3739d7c)
- **Systemowo**: miejscownik „w Cosenzie” (było „w Cosenzy” w 25 miejscach, 6 plików PL) — **⚠ błędna poprawka, cofnięta 2026-09-22, zob. „Stan 2026-09-22”**; „Dziedzictwo grekanické” → „grekańskie” w ramkach „W pobliżu” Bovy; „griko di Calabria” → „greco di Calabria” (griko = Salento; id nagłówka zostaje)
- **Błędy w tekście, redaktor miał rację**: Ferragosto to 15.08 (nie „pierwsze dwa tygodnie sierpnia”); Scilla i Pizzo to nie „wybrzeże Scilla–Pizzo” (Costa Viola / Costa degli Dei); lestopitta jest smażona, nie pieczona
- **Błędy redaktora**: Lamezia (lotnisko) → Tropea nie trwa 40–60 min – wg Trenitalia lefrecce API pociąg z Lamezia Terme Centrale 50–57 min, z lotniska + autobus do dworca łącznie ok. 1 h 10 min–1 h 20 min (tekst miał 1,5–2 h); Catanzaro Lido → muzeum w Locri wg OSRM 93 km / 98 min (redaktor: 75 km, 1 h 15); „Amendolea żeglowna w starożytności” niezweryfikowane, nie dodane; stacja Locri „200–300 m od plaży” niepotwierdzona
- Liczby wg OSRM: zamek Cosenza → katedra ok. 11 min, Teatro Rendano ok. 11 min, Museo Brettii ok. 17 min pieszo (MAB Bilotti ok. 25 min pieszo, 1,9 km – OSM foot, zweryfikowane); muzeum Locri ok. 4 km od centrum (było 5). Wybrzeże Kalabrii „blisko 790 km” także w blogu Najlepsze plaże (było 780)
- Skan kotwic po każdej edycji: 0 martwych `href="#"` na zmienionych stronach. Zasada bez zmian: id z polskimi znakami zostają, nowe id tylko przy zmianie nagłówka
- Pliki od redaktora bywają starszą wersją niż repo (blog Plaże miał jeszcze 780 km) – zawsze diff zdanie po zdaniu
- TODO: „W pobliżu” na innych stronach Cosenzy – czasy pieszo z zamku sprawdzić; EN plaże Locri bez miecznika/sardeli i pinakes z Reggio (do decyzji)

## Stan 2026-09-21 (3) – fact-check redaktorski: 'nduja + weryfikacja MAB
- PL+EN wgrane: 'nduja (b9165c3); zamek Cosenza – MAB Bilotti ok. 25 min pieszo (f89cb7d, 1,9 km wg OSM `routed-foot`; publiczny OSRM `router.project-osrm.org` z profilem foot zwraca czasy samochodowe – nie używać do pieszych)
- Współrzędne it.wikipedia: zamek 39,2866 N / 16,2576 E, MAB 39,2969 N / 16,2543 E (Nominatim błędnie geokoduje „Castello Normanno-Svevo, Cosenza” i „Corso Mazzini” – brać z it.wikipedia API `prop=coordinates`)
- 'nduja: odmiana Spilinga → Spilindze, biernik „'nduję”, dopełniacz „'ndui”; guanciale = policzek (nie podgardle – błąd redaktora); pizza z caciocavallo/provolą silaną zamiast gorgonzoli; fileja z linkiem do /pl/kuchnia/makaron-fileja/. Daty Sagra della 'Nduja (49. ed. 8.08.2025, 50. ed. 8.08.2026) wg komunikatu gminy – zostają
- TODO nadal: „W pobliżu” innych stron Cosenzy (czasy pieszo), EN plaże Locri bez miecznika/sardeli i pinakes z Reggio

## Stan 2026-09-22 – fact-check redaktorski: katedry Tropea, Stilo, Cosenza; korekta odmiany „Cosenzy”
- PL+EN wgrane: katedra normańska w Tropei (d5db95c), Duomo w Stilo (5cbb3a8), katedra Santa Maria Assunta w Cosenzy (fc8d473)
- **Halucynacja AI usunięta**: katedra w Tropei nie ma relikwii św. Błażeja (są w Maratei) – sekcja przepisana na św. Dominikę (relikwie pod głównym ołtarzem, współpatronka, ur. w dzisiejszej Santa Domenica di Ricadi) i bł. Francesca Mottolę; Pizzo od Tropei to 30 km (nie 25, wg SS522); bomby z 1943 spadły do ogrodu pełnego bawiących się dzieci, rozbroił je biskup Cribellati (ilvibonese.it)
- **Odrzucona sugestia redaktora** (Stilo): portal Duomo jako „gotyk andegaweński, XIV w.” – zweryfikowane w turismo.reggiocal.it i themaprogetto.it, które potwierdzają styl romańsko-gotycki i budowę XII–XIV w., zgodnie z dotychczasową treścią. Odległość Stilo–Monasterace Marina poprawiona z 11 na 13 km (OSRM), dodany numer drogi SP9. Naprawione zdezaktualizowane kotwice z błędną nazwą „katedra św. Wawrzyńca” (widoczny tekst był już poprawiony wcześniej, id nie)
- **⚠ Korekta odmiany „Cosenza”**: Wikisłownik potwierdza miejscownik/dopełniacz = „Cosenzy”, nie „Cosenzie” – sesja z 21.09 (zob. wyżej) wprowadziła błędną poprawkę w 25 miejscach/6 plikach. Cofnięte sitewide (11 plików PL: katedra, zamek, teatro-rendano, mab-bilotti, museo-brettii, galleria-nazionale, cosenza/_index, nduja, street-food, noclegi, blog kuchnia-kalabryjska) + poprawione kotwice TOC/nagłówków. **Zasada na przyszłość: sprawdzać trudne odmiany w Wikisłowniku (pl.wiktionary.org), nie polegać na wyczuciu**
- Katedra w Cosenzy: barok z ok. 1750 usunięty purystyczną renowacją XIX/XX w. (progettostoriadellarte.it) – nie „współistnieje” ze średniowiecznym stylem; dodane zweryfikowane fakty: Madonna del Pilerio uratowała miasto od dżumy w 1576 (it.wikipedia), mos teutonicus przy pochówku Izabeli Aragońskiej (ciało w Cosenzy, kości w Saint-Denis); sekcja o „wymogach UNESCO” (generyczny wypełniacz) skondensowana do faktów o Cosenzy
- Wniosek ogólny: pliki od redaktora bywają starszą wersją repo (np. Stilo – nazwa „katedra św. Wawrzyńca” już poprawiona w repo, redaktor pracował na starym szkicu) – zawsze diff z bieżącym stanem, nie nadpisywać w ciemno; ale redaktor bywa też słuszny w kwestiach, które warto zweryfikować niezależnie (Cosenzy, bomby 1943, mos teutonicus) – żadnej strony nie traktować z góry jako autorytatywnej

## Stan 2026-09-22 (2) – fact-check redaktorski: katedra w Bovie, Most Bisantis, Bergamotka, Street food
- PL+EN wgrane i wypchnięte: katedra Santa Maria dell'Isodia w Bovie (4808244), Most Bisantis w Catanzaro (882d77e), Bergamotka (3ccdefa), Street food w Kalabrii (eb20512)
- **Zasada robocza tej sesji**: każdą propozycję redaktora (nawet „pewne fakty” z jego własnej sekcji weryfikacji) sprawdzać niezależnie przez WebSearch/WebFetch przed wklejeniem – w tej turze trafiły się dwa jawne błędy redaktora, które przeszłyby bez weryfikacji
- **Błąd redaktora (Bova)**: literówka cyrylicka „над” w oryginalnym pliku (niezależna od redakcji) poprawiona na „nad”; atrybucja rzeźby Madonny z 1584 dłuta Bonanno jest dziś pewna (inskrypcja na cokole, catalogo.beniculturali.it) – usunięte zbędne „przypisywana”; dodane zweryfikowane: droga SP24 Bova Marina–Bova (~14 km), tradycja rozdawania gałązek Pupazze jako błogosławieństwa, figura św. Leona w kościele San Leo także dłuta Bonanno (1582)
- **Błąd redaktora (Most Bisantis)**: twierdził, że dedykacja mostu Bisantisowi nastąpiła w 2001 r. – to błąd, 2001 to data inauguracji iluminacji łuku, sam most poświęcono pamięci Fausta Bisantisa w 2002 r. (it.wikipedia), tekst już wcześniej poprawnie rozróżniał te dwa wydarzenia i nie został zmieniony. Poprawiona wysokość pomostu 110→112 m; dodane: stacja Catanzaro Città (Ferrovie della Calabria, dzielnica San Leonardo) + funicolare jako dojazd do centrum, Viadotto Italia (259 m, A2) jako najwyższy wiadukt Włoch, ANAS jako zarządca prowadzący monitoring
- **Bergamotka**: poprawki merytoryczne w większości trafne – MASEF→MASAF, Melito Porto Salvo→Melito di Porto Salvo, Bruzzano→Bruzzano Zeffirio (pełne nazwy gmin), 198 000 q→19 800 ton. Nazwa wody kolońskiej poprawiona z błędnego „Calabrisella” (jak podał redaktor) na prawidłowe „Calabresella” (Reggio Calabria, od 1910 r.) – zweryfikowane w źródle
- **Street food**: poprawka geograficzna potwierdzona – Soverato i Corigliano-Rossano leżą nad Morzem Jońskim, nie Tyrreńskim (cuoppo rozdzielone wg wybrzeży). Sagra del pescespada w Bagnara Calabra: błędna „druga niedziela lipca” zastąpiona ostrożniejszym „tradycyjnie pierwsza niedziela sierpnia, data zmienna” (edycja 2026 wypadła 24–26 lipca). Dodane: dosłowne znaczenie „a ruota di carro”, opis feluki (passerella, maszt antenna), status IGP Tartufo di Pizzo od 2024 (pierwszy lód w Europie), sycylijskie pochodzenie Don Pippo jako źródło techniki formowania lodów jak arancini
- **Nie przyjęto z redakcji (street food)**: sugestia zmiany „w Cosenzy” na „w Cosenzie” – to ta sama błędna poprawka co w sesji 21.09, cofnięta 22.09 (zob. wyżej); poprawna forma to „Cosenzy” (Wikisłownik). Redaktor najwyraźniej pracował na starszej/innej wersji tekstu
- Workflow bez zmian: diff zdanie po zdaniu, WebSearch/WebFetch do weryfikacji każdego twierdzenia redaktora (także tych z sekcji „pewne fakty”), hugo build → skan `href="#"` w `public/` po każdej edycji → commit tylko zmienionych plików `content/` → push tokenem sibilianspirit (patrz `reference_github_push_auth.md`)

## Stan 2026-09-23 – fact-check redaktorski: Piazza San Rocco (Scilla)
- PL+EN (10bcf51): banały usunięte, Messyna → Mesyna, „św. Roch” w polskim tekście (Piazza San Rocco zostaje), feluki (wł. *feluche*, nie *felucche*) z masztem i kładką *passerella*; nagłówki kościoła i sekcji Wyspy Liparyjskie i Costa Viola z nowymi id
- **Etna z placu niewidoczna** – redaktor miał rację co do wniosku, ale nie co do przyczyny: profil SRTM pokazuje, że Peloritani NIE zasłaniają (kąt ok. 0,017 rad wobec 0,033 rad do szczytu Etny), zasłania zbocze nad Scillą (~500 m n.p.m., 1,7 km na SW). Tripadvisor twierdzi odwrotnie – niewiarygodne
- Winda (*ascensore*) Piazza San Rocco ↔ Marina Grande: otwarta 14.07.2021, wejście przez tunel od promenady (przy barze Zanzibar), sezonowa, we wrześniu 2025 zamknięta – ceny nie podajemy (1 € z 2021 niezweryfikowane na 2026)
- Rzeźba Scylli: Francesco Triglia, odsłonięta 26.07.2013, po budowie windy przeniesiona na zwieńczenie szybu
- **Nie przyjęte**: „szkoła wenecka” zamiast Mazzola (discoverscilla przypisuje figurę Giovanniemu Battiście Mazzolowi); „bilet kilka euro” – zostaje konkretna cena 3 € i godziny zamku, przeredagowane bez stylu raportu

## Stan 2026-09-23 (2) – fact-check redaktorski: katedra w Catanzaro
- PL+EN (ff7d635): tytuł bez „w sercu Kalabrii”; kalki „Catanzaro Cathedral”, centro storico, rione → dzielnica; archidiecezja/diecezja małą literą; description przepisany (był ucięty „…”)
- Sekcja o katedrach w Sienie i Pizie (zapychacz) usunięta wraz ze źródłami Siena i UNESCO (link „Just a moment...”); w jej miejsce konkatedra w Squillace: XI w., fundacja Rogera I, zniszczona 1783, ponowna konsekracja 6.05.1798, bazylika mniejsza 2015 (it.wikipedia); Catanzaro → Squillace 25 km / ok. 30 min (OSRM)
- **Przesada redaktora**: obraz Wniebowzięcia (ok. 5 × 2,5 m, szkoła neapolitańska, 1750) przeniesiony do MARCA 11.06.2025 – potwierdzone (SABAP), ale wg catanzaroinforma.it z 13.09.2026 konserwacja czeka jeszcze na przetarg, więc nie „ogląda się jej na żywo”; w FAQ opisane ostrożnie. Dzień otwarty pracowni 26.09.2026

## Stan 2026-09-23 (3) – fact-check redaktorski: Brązy z Riace
- PL+EN (6cea095): przyjęta stylistyka redaktora (monumentalne rzeźby, gruntowna konserwacja, w kontrapoście, Mesyna, karabinierzy, „Posąg A/B” zamiast „Bronzo”, „przetrwało kilkanaście”, osoby ustawowo zwolnione z opłat, pinakes z objaśnieniem, autobusy ATAM m.in. 27 i 28)
- **Błąd w tekście i u redaktora**: oczy NIE z kości słoniowej – białka z kalcytu, tęczówki z pasty szklanej; zachowane oko Posągu B z pięciu kamiennych elementów; z miedzi także rzęsy (it.wikipedia). Tabela materiałów poprawiona
- **Liczby „w 100% poprawne” wg redaktora – nie są**: ok. 220 m od brzegu (nie 200), głębokość w relacjach 6–10 m (Mariottini 2009: ~6 m, zgłoszenie z 17.08.1972: ~10 m), nie „8 m”; nurkowanie na wstrzymanym oddechu (*in apnea*). Poprawione też w blogu Najlepsze plaże PL+EN (było 200–300 m / 8 m)
- Hełmy: redaktor przypisał pewny hełm koryncki tylko B – wg it.wikipedia na hełm u A wskazują włosy wymodelowane pod nakryciem i ślady mocowania; potylica B pasuje do podniesionego hełmu albo obszernego nakrycia głowy. Opisane ostrożnie dla obu
- Cokoły antysejsmiczne z marmuru kararyjskiego zaprojektowane przez ENEA (2013, pierwsze takie zastosowanie) – potwierdzone, zastąpiły „antysejsmiczną podłogę”
- Nie przyjęte: nazwa muzeum w alt (zostaje polska, decyzja z 15.09), frazesy „absolutny fundament”, „absolutnie najwyższy poziom”, „na sam koniec włoskiego buta”; usunięcie Centro di Restauro we Florencji i ostrożnych sformułowań o atrybucjach; pewnik o komorze mikroklimatycznej (it.wikipedia potwierdza ją tylko dla 2013). Strona muzeum `come-arrivare` odrzucała połączenia (ECONNREFUSED)

## Stan 2026-09-23 (4) – fact-check redaktorski: Cattolica di Stilo
- PL+EN (dfe7249): odmiana Cattoliki/Cattolicę/Cattolice (id nagłówków bez zmian), „w Kalabrii” zamiast „w regionie Kalabria”, oczka na kostce, katholikon w intro zamiast powtórzonego akapitu o nazwie, św. Jan Theristis (Żniwiarz), apsydy bema/prothesis/diakonikon, arabskie inskrypcje (odkryte 1997) także w tekście głównym, description przepisany (był ucięty „…”)
- **Błędy redaktora**: wzór cegieł to fryz ząbkowy *a dente di sega*, NIE jodełka *spina di pesce* (błąd był też w oryginale); zamknięcie przed otwarciem 29.07.2026 trwało niemal 10 miesięcy, nie „niemal rok”; Orsi przeprowadził pierwszą nowoczesną restaurację 1912–1927 (it.wikipedia), nie „ponowne odkrycie”; autobus lokalny ze stacji niepotwierdzony – zostało „samochód lub taksówka”
- Potwierdzone: prace z PNRR (burze, bariery architektoniczne, park Clarisse – finestresullarte.info); „jedna kolumna do góry nogami” → w podstawach kolumn odwrócone kapitele
- Droga Monasterace Marina → Stilo: w OSM nazwa „Strada Provinciale 9”, ref SS110 – na stronie „SS110 (oznaczana też jako SP9)”, ok. 13 km
- Heredoki w Bash z długim tekstem nadal się sypią – skrypty i pliki pisać narzędziem Write

## Stan 2026-09-23 (5) – fact-check redaktorski: Makaron fileja
- PL+EN (a98b3d5): „tego dania spróbować” (dopełniacz), wymowa bez odniesienia do angielskiego „yes” w PL (w EN zostaje), tyrreńskim, semolina zamiast „mąki semolowej”, świderek zamiast „śruby”, ragù z koziny, „Wersje smakowe”, „doskonale łączy się z gęstymi sosami”, lody tartufo di Pizzo; description przepisany (był ucięty „…”)
- **Sagra doprecyzowana**: redaktor pisał o „słynnej Sagra della Fileja” – nie ma jednej; wpisana Sagra di Fileja e Ceci w Pannaconi (gmina Cessaniti, 36. edycja 6.08.2026, źródło sagreautentiche.it) oraz sagry w Filandari i Briatico
- Potwierdzone: Pecorino del Monte Poro DOP – rozporządzenie wykonawcze 2020/974 z 6.07.2020 (Dz.U. UE L 215 z 7.07.2020)
- Nie przyjęte: wino Cirò Rosso do filei (Cirò to prowincja Crotone, nie Vibo – bez lokalnego związku)

## Stan 2026-09-23 (6) – fact-check redaktorski: Galleria Nazionale di Cosenza (Palazzo Arnone)
- PL+EN (77b5708): lesene → lizeny, łuk pełny → półkolisty, „figury zwycięstw” → postacie Wiktorii w narożach (wg luoghidelcontemporaneo.cultura.gov.it), altura di Triglio → wzgórze Triglio, Quattrocento/Novecento → XV–XX w., Fisco Regio / Regia Udienza / Calabria Citeriore po polsku z oryginałem w nawiasie, pałac rodzaju męskiego, osoby z niepełnosprawnościami; nagłówek „Majestat renesansu” → „Renesansowy pałac – architektura Palazzo Arnone” (nowe id; „perła” od redaktora odrzucona); description przepisany (był ucięty „…”); linki do Castello Svevo prowadzą teraz do strony zamku
- **Błędy redaktora**: XVIII-wieczne *corpi di fabbrica a monte* to części położone wyżej na zboczu, nie „nadbudowa wyższych kondygnacji”; kolekcja Boccioniego to „disegni e incisioni” – ryciny, nie „szkice”; AMACO nie jest „przejmowane przez Consorzio Autolinee” – umowa z marca 2026 upadła, spółka w upadłości kursuje tymczasowo do 30.09.2026, zainteresowanie zgłosiło konsorcjum Cometra (Gazzetta del Sud 31.08.2026) – na stronie ogólna uwaga o reorganizacji i taksówka ze stacji; znacznik „[DO WERYFIKACJI] wstęp bezpłatny” odrzucony – bilet nadal 5 € / 2 €, bezpłatnie tylko w pierwszą niedzielę miesiąca (Domenica al Museo, artsupp/cosenzaok)
- Dodane: trzęsienie ziemi 1854 zawaliło trzecie piętro, nieodbudowane (it.wikipedia); grafiki Boccioniego ze zbioru Lydii Winston Malbin, w galerii od 1996; Preti (Il Cavalier Calabrese, ur. w Tavernie), Boccioni ur. w Reggio Calabria
- SUF → Palazzo Arnone wg OSRM 67 km / 58 min – „około godziny” zamiast 50 min. Strony cultura.gov.it i musei.calabria.beniculturali.it odrzucały połączenia (ECONNREFUSED)
- TODO: po 1.10.2026 sprawdzić, kto obsługuje autobusy miejskie w Cosenzy (Cometra?) i zaktualizować strony Cosenzy

## Stan 2026-09-23 (7) – Galleria Nazionale di Cosenza, druga tura
- PL+EN (adb85a8): redaktor przysłał tę samą redakcję co w (6) – większość była już wgrana; nowe poprawki po diffie
- **Błąd w tekście, redaktor miał rację**: bastiony to nie XVII w. – pierwszy wzniesiono w 1747 r., cztery narożne w 1758 r. z woli gubernatora, po pożarach z 1734 i 1747 (it.wikipedia). Budynek przekazano ministerstwu kultury w latach 80. XX w.
- Potwierdzone i dodane: rysunki przygotowawcze do „Śmiechu” (*La risata*, 1911, MoMA); egzemplarz „Unikalnych form ciągłości w przestrzeni”; wystawy czasowe (Rembrandt 2019, Hokusai/Hiroshige 2022, Manet 2023) zamiast wypełniacza w sekcji „Wydarzenia”
- Nazwa w polskich zdaniach: „Galeria Narodowa w Cosenzy” (odmieniana; tytuł strony zostaje włoski); 3 nagłówki H2 z nowymi id ASCII; usunięte „skarbnica kultury”, „kulturowy pomost”
- Nie przyjęte: „w Cosenzie” (poprawnie: Cosenzy), Paola → Cosenza 25 min (zostaje 22 min), autobusy AMACO jako zalecany dojazd (spółka jest w upadłości)

## Stan 2026-09-23 (8) – fact-check redaktorski: Tradycja połowu miecznika (Scilla)
- PL+EN (b96c2dd): wypływają w morze, maszt/wieża kratownicowa zamiast kalki *traliccio*, pomost dziobowy, Mesyna, w Chianalei, w Bagnarze Calabrze, lokalnych sagr, palangari objaśnione (sznury haczykowe), „filar nadmorskiej kuchni”, „Powrót do Scilli”; description przepisany (był ucięty „…”)
- Dodane i potwierdzone (culturalimentare/ICCD, cibotoday, clicksicilia): harpunuje się najpierw samicę, bo samiec zostaje przy partnerce; *cardata da cruci* = wielokrotny krzyż wydrapywany paznokciami na prawym policzku/skrzelach; św. Marek = patron harpunników
- **Przesada redaktora**: „potwierdzona reguła biologiczna” – źródła opisują to jako tradycję rybacką, nie wynik badań; na stronie „reguła z wielopokoleniowej obserwacji”. Inwokacja: zostaje zapis z karty ICCD „San Marcu è binirittu”, wariant redaktora „San Marcu binirittu!” podany obok. „Scylli i Mesyny” odrzucone (Scylla = potwór) – jest „dzisiejszej Scilli i Mesyny”; „szlachetny przeciwnik” przeniesiony do opisu cardaty (tak podają źródła)
