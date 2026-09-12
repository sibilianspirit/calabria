# Plan treści blogowych bestofcalabria.com – październik 2026 → wrzesień 2027

Stan na 2026-09-12. Dane: Senuto (Polska, baza standardowa), Ahrefs (GB) – wolumeny miesięczne.

## 1. Punkt wyjścia

- Serwis ma 146 stron encyklopedycznych (miasta, atrakcje, natura, kuchnia, kultura, praktyczne) i tylko **3 wpisy blogowe**.
- Widoczność w Google PL: **3 frazy** w TOP50 (park narodowy pollino, park narodowy sila, parki narodowe włochy). Strony miast nie rankują jeszcze na nic, bo konkurują z Wikipedią i portalami biur podróży na frazach brandowych typu „tropea”.
- Najłatwiej wejść w SERP-y **frazami pytaniowymi i poradnikowymi** (co zobaczyć, pogoda, jak dojechać, czy warto), gdzie konkurencja to blogi, a nie Wikipedia. To zadanie bloga.
- Duża część polskiego ruchu wokół Kalabrii to **turystyka zorganizowana**: `tui magic life calabria` 1600, `kalabria itaka` 320, `scalea` 1900, `santa caterina scalea` 480, `parghelia` 880. Serwis nie ma o tych miejscach ani słowa.

Frazy główne, których serwis dziś nie obsługuje (Senuto PL):

| Fraza | Wolumen | Uwagi |
|---|---|---|
| kalabria | 27 100 | ogólna, strona główna |
| kalabria włochy | 6 600 | ogólna |
| capo vaticano | 5 400 | strona istnieje |
| scilla | 4 400 | strona istnieje, ale fraza wieloznaczna |
| wyspy liparyjskie | 2 900 | wycieczka z Tropei |
| scalea | 1 900 | **brak strony** |
| tropea włochy | 1 900 | strona istnieje |
| tui magic life calabria | 1 600 | **brak** (GB: 2 100) |
| ndrangheta | 1 600 | brak; intent informacyjny |
| kalabria mapa | 880 | brak |
| parghelia | 880 | brak |
| kalabria co zobaczyć | 590 | brak listy zbiorczej |
| kalabria pogoda | 590 | brak; + wrzesień 70, październik 50, czerwiec 30 |
| kalabria wakacje | 590 | brak |
| kalabria lotnisko | 390 | częściowo (jak dojechać) |
| kalabria itaka | 320 | brak |
| soverato | 260 | brak |
| lamezia terme lotnisko | 210 | częściowo |
| tropea plaże | 170 | strona istnieje |
| tropea noclegi | 140 | brak |

Osobna liga: `nduja` 49 500 i `nduja co to` 3 600 oraz `bergamotka` 22 200. Strony w sekcji Kuchnia istnieją, ale są encyklopedyczne. Blog może dołożyć wersje użytkowe (przepisy, co kupić, gdzie zobaczyć).

## 2. Zasady dla każdego wpisu

- **Dwujęzycznie**: PL jako oryginał, EN jako pełne tłumaczenie z lokalizacją fraz (nie kalka). Pliki `content/pl/blog/<slug>.html` i `content/en/blog/<slug>.html`, wspólny `translationKey`.
- **Długość** 1 500–2 500 słów, spis treści `boc-toc`, H2 co 250–400 słów, ramka FAQ (4–6 pytań z fraz „people also ask”), ramka Źródła.
- **Zdjęcia**: wyłącznie realne (własne lub Wikimedia Commons z atrybucją), min. 3 na wpis, hero 1600×900.
- **Linkowanie**: każdy wpis linkuje do 4–8 istniejących stron serwisu (miasta, atrakcje, praktyczne) i odwrotnie – po publikacji dopisać link z 2–3 stron encyklopedycznych do wpisu.
- **Fact-check** przez pipeline `fact-checker/` przed publikacją; ceny, godziny i rozkłady z datą sprawdzenia w treści.
- **Autor**: Karina (author-box, schema Article). Elementy pierwszej osoby tam, gdzie są własne zdjęcia.
- **Publikacja** równo co 2 tygodnie; po publikacji wpis automatycznie trafia do puli publikatora FB, można też wymusić przez `gh workflow run fb-daily-post.yml -f pick=blog/<slug>.html`.

## 3. Lista wpisów według priorytetu

Priorytet = wolumen × szansa na ranking × dopasowanie do monetyzacji (Booking, wynajem aut).

| # | Tytuł roboczy PL | Fraza główna (PL vol.) | Frazy wspierające | Tytuł EN (GB vol.) | Slug PL / EN |
|---|---|---|---|---|---|
| 1 | Kalabria – co zobaczyć? 25 miejsc od Tropei po Aspromonte | kalabria co zobaczyć (590) | kalabria atrakcje 390, co warto zobaczyć 140, zwiedzanie 90, co zwiedzić 50 | Things to do in Calabria: 25 places worth the trip (150, TP 700) | kalabria-co-zobaczyc / things-to-do-in-calabria |
| 2 | Pogoda w Kalabrii miesiąc po miesiącu – kiedy jechać i jaka jest woda | kalabria pogoda (590) | pogoda wrzesień 70, październik 50, czerwiec 30, maj 20, temperatura 110, tropea pogoda 880 | Calabria weather by month: when to go (200) | pogoda-w-kalabrii / calabria-weather-by-month |
| 3 | Mapa Kalabrii – atrakcje, plaże, lotniska i odległości | kalabria mapa (880) | mapa turystyczna 110, atrakcje mapa 90, tropea mapa 390 | Map of Calabria: regions, beaches and airports | mapa-kalabrii / map-of-calabria |
| 4 | Scalea i Riviera dei Cedri – co zobaczyć, plaże, Santa Caterina Village | scalea (1 900) | santa caterina scalea 480, scalea pogoda 320, opinie 90, co zobaczyć 50, stare miasto 90, diamante 90 | Scalea, Calabria: beaches, old town and Riviera dei Cedri | scalea-co-zobaczyc / scalea-calabria |
| 5 | Lotnisko Lamezia Terme – jak dojechać do Tropei, Pizzo i Scalei, co zobaczyć w Lamezii | kalabria lotnisko (390) | lamezia terme lotnisko 210, lamezia 3 600, lamezia terme co zobaczyć 90, kalabria loty 90 | Lamezia Terme airport: transfers to Tropea, Pizzo and Scalea (calabria airport 250) | lotnisko-lamezia-terme / lamezia-terme-airport |
| 6 | TUI Magic Life Calabria – co zobaczyć w okolicy resortu (Pizzo, Tropea, Capo Vaticano) | tui magic life calabria (1 600) | magic life calabria, kalabria tui 20 | Around TUI Magic Life Calabria: Pizzo, Tropea and Capo Vaticano (2 100) | tui-magic-life-calabria-okolica / tui-magic-life-calabria-area |
| 7 | Kalabria z biurem podróży – gdzie są hotele Itaki, Rainbow i TUI i co zwiedzić z każdego kurortu | kalabria itaka (320) | kalabria rainbow 90, kalabria wakacje 590, kalabria wczasy 90, all inclusive 10 | – (tylko PL) | kalabria-z-biurem-podrozy |
| 8 | Prom z Kalabrii na Sycylię – Villa San Giovanni–Messyna, ceny, czas i Etna w jeden dzień | prom na sycylię z villa san giovanni (90) | prom na sycylie 170, promy sycylia 90, ile kosztuje 50, ile płynie 20 | Ferry from Calabria to Sicily: Villa San Giovanni to Messina | prom-na-sycylie-z-kalabrii / ferry-calabria-sicily |
| 9 | Czy Kalabria jest bezpieczna? 'Ndrangheta, turyści i zdrowy rozsądek | ndrangheta (1 600) | mafia kalabryjska 260, kalabria mafia 70, czy w kalabrii jest bezpiecznie 10 | Is Calabria safe for tourists? | czy-kalabria-jest-bezpieczna / is-calabria-safe |
| 10 | Wyspy Liparyjskie z Kalabrii – Stromboli o zachodzie słońca z Tropei | wyspy liparyjskie (2 900) | stromboli wycieczka 30, wycieczki fakultatywne 40 | Aeolian Islands day trip from Tropea | wyspy-liparyjskie-z-tropei / aeolian-islands-from-tropea |
| 11 | Kalabria czy Sycylia? A może Sardynia lub Apulia – porównanie na wakacje | kalabria czy sycylia (30) | kalabria czy sardynia 10, kalabria opinie 40 | Calabria vs Sicily: which one for your holiday? | kalabria-czy-sycylia / calabria-vs-sicily |
| 12 | Tropea w jeden dzień – trasa spaceru, plaże, gdzie zjeść | tropea co zobaczyć (90) | tropea plaże 170, restauracje 40, atrakcje 70, tropea włochy 1 900 | One day in Tropea: walking route, beaches, where to eat (tropea calabria beach 600) | tropea-w-jeden-dzien / one-day-in-tropea |
| 13 | Gdzie spać w Kalabrii – Tropea, Capo Vaticano, Scalea czy Soverato | tropea noclegi (140) | kalabria noclegi 110, hotele 70, hotel 50 | Where to stay in Calabria: best bases by coast (calabria hotels 100, villas 150) | gdzie-spac-w-kalabrii / where-to-stay-in-calabria |
| 14 | Nduja w kuchni – 7 przepisów, jak jeść i gdzie kupić prawdziwą ze Spilingi | nduja (49 500) | nduja co to 3 600 | Cooking with nduja: 7 recipes and where to buy the real thing | nduja-przepisy / nduja-recipes |
| 15 | Kalabria samochodem – trasa objazdowa na 10 dni po obu wybrzeżach | kalabria samochodem (10) | kalabria zwiedzanie 90; uzupełnia „Plan na 7 dni” | Calabria road trip: 10-day itinerary | kalabria-samochodem-10-dni / calabria-road-trip |
| 16 | Kalabria z dziećmi – plaże z płytką wodą, aquaparki, spokojne kurorty | brak w Senuto | wysoki intent z biur podróży | Calabria with kids | kalabria-z-dziecmi / calabria-with-kids |
| 17 | Parghelia, Zambrone i Capo Vaticano – plaże Costa degli Dei poza Tropeą | parghelia (880) | capo vaticano 5 400, capo vaticano plaże 30, ricadi 170 | Best beaches on the Costa degli Dei beyond Tropea (capo vaticano calabria beach 150) | plaze-costa-degli-dei / costa-degli-dei-beaches |
| 18 | Kalabria poza sezonem – maj, wrzesień i październik bez tłumów | kalabria pogoda wrzesień (70) | październik 50, w maju 10, w listopadzie 10 | Calabria in September and October | kalabria-poza-sezonem / calabria-off-season |
| 19 | Pizzo w pół dnia – tartufo, zamek Murata i kościół Piedigrotta | pizzo (720) | pizzo calabro 140, tartufo di pizzo 70 | Pizzo Calabro: tartufo, castle and Piedigrotta (400) | pizzo-w-pol-dnia / pizzo-calabro-guide |
| 20 | Kalabria bez samochodu – pociągiem i autobusem po wybrzeżu | brak w Senuto | wspiera planer dojazdu | Calabria without a car | kalabria-bez-samochodu / calabria-without-a-car |
| 21 | Soverato i Costa degli Aranci – plaże wybrzeża jońskiego | soverato (260) | catanzaro lido (strona istnieje) | Soverato and the Ionian coast | soverato / soverato-ionian-coast |
| 22 | Co przywieźć z Kalabrii – cebula z Tropei, nduja, bergamotka, likiery | cebula tropea (40) | cebula z tropei gdzie kupić 10 | What to buy in Calabria: food souvenirs | co-przywiezc-z-kalabrii / what-to-buy-in-calabria |
| 23 | Bergamotka z Reggio – dlaczego rośnie tylko tu i gdzie zobaczyć plantacje | bergamotka (22 200, intent mieszany) | – | Bergamot of Calabria: the Reggio coast (bergamotto di calabria 200) | bergamotka-z-reggio / bergamot-calabria |
| 24 | Święta i festiwale Kalabrii – kalendarz roku | brak w Senuto | wspiera stronę Tradycje | Calabria festivals: a year-round calendar | festiwale-kalabrii-kalendarz / calabria-festivals-calendar |
| E1 | – (tylko EN) | – | – | Where is Calabria? Map, coasts and how to get there (250, TP 1 800) | – / where-is-calabria |

Wolumeny dla wpisów 16, 20 i 24 są poniżej progu Senuto, ale pytania te pojawiają się w „people also ask” i domykają tematy, o które pytają czytelnicy planera dojazdu. Traktować jako wsparcie, nie jako priorytet ruchu.

## 4. Kalendarz publikacji (2 wpisy w miesiącu)

Kolejność dopasowana do sezonu wyszukiwań: rezerwacje na lato ruszają w styczniu i lutym, pytania o pogodę i plaże rosną od kwietnia, ruch „na miejscu” (prom, wycieczki, gdzie zjeść) szczytuje w lipcu i sierpniu.

| Miesiąc | Wpis A | Wpis B |
|---|---|---|
| Październik 2026 | #1 Co zobaczyć | #2 Pogoda miesiąc po miesiącu |
| Listopad 2026 | #3 Mapa Kalabrii | #9 Czy Kalabria jest bezpieczna + E1 Where is Calabria |
| Grudzień 2026 | #14 Nduja przepisy (prezenty, święta) | #22 Co przywieźć |
| Styczeń 2027 | #6 TUI Magic Life okolica | #7 Kalabria z biurem podróży |
| Luty 2027 | #5 Lotnisko Lamezia | #13 Gdzie spać |
| Marzec 2027 | #11 Kalabria czy Sycylia | #15 Trasa samochodem 10 dni |
| Kwiecień 2027 | #4 Scalea | #16 Kalabria z dziećmi |
| Maj 2027 | #12 Tropea w jeden dzień | #17 Plaże Costa degli Dei |
| Czerwiec 2027 | #8 Prom na Sycylię | #10 Wyspy Liparyjskie |
| Lipiec 2027 | #19 Pizzo | #21 Soverato |
| Sierpień 2027 | #20 Bez samochodu | #24 Festiwale |
| Wrzesień 2027 | #18 Poza sezonem | #23 Bergamotka |

## 5. Luki poza blogiem (nowe strony w Kierunkach)

Te miejscowości mają własny wolumen i turystów z Polski, a serwis ich nie ma. Blog może o nich pisać, ale docelowo potrzebują pełnych stron w `/pl/kierunki/` z planerem dojazdu i widgetem pogody:

1. **Scalea** (1 900) + Praia a Mare, Diamante, San Nicola Arcella (Arcomagno) – Riviera dei Cedri
2. **Parghelia** (880) i Zambrone – zaplecze Tropei
3. **Soverato** (260) – Costa degli Aranci
4. **Lamezia Terme** (3 600, w tym lotnisko) – strona przesiadkowa
5. **Villa San Giovanni** – prom, obsługuje wpis #8

## 6. Co mierzyć

- Search Console: kliknięcia i pozycje dla fraz głównych z tabeli, sprawdzane co miesiąc; cel po 6 miesiącach: 10 fraz w TOP10, w tym „kalabria co zobaczyć” i „kalabria pogoda”.
- Senuto: widoczność TOP10/TOP50 domeny (dziś 0/3).
- Na stronie: kliknięcia w ramkę „Zaplanuj” i linki Booking po wdrożeniu monetyzacji.
- FB: zasięg postów z linkami do bloga vs. do stron encyklopedycznych (po pierwszym miesiącu publikatora).
