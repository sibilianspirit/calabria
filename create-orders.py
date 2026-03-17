#!/usr/bin/env python3
"""
bestofcalabria.com — tworzenie zleceń w content-manager (Supabase)
Wywołanie: python3 create-orders.py
"""

import urllib.request
import json
import sys
from datetime import datetime, timezone

# ─── KONFIGURACJA ──────────────────────────────────────────────────────────────

SUPABASE_URL = "https://lkwdrdhzqlszsicguqxf.supabase.co"
ANON_KEY     = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxrd2RyZGh6cWxzenNpY2d1cXhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY0MDExNTksImV4cCI6MjA4MTk3NzE1OX0.duV0yt5yhTv5PT6p0YX9_Eli8vuORaoxGVHlTTcEZso"
EMAIL        = "sibilianspirit@gmail.com"
PASSWORD     = "Admin123!"
DOMAIN_ID    = "9c549fd3-9510-4d54-bcc0-dd7fae816ea3"  # bestofcalabria.com

# ─── TEMATY ────────────────────────────────────────────────────────────────────

TEMATY = [
    {
        "tytul": "Park Narodowy Aspromonte – dzika natura południowej Kalabrii",
        "keywords": ["Park Narodowy Aspromonte", "Aspromonte park narodowy", "Aspromonte Kalabria", "Aspromonte trekking"],
        "faq": [
            "Gdzie znajduje się Park Narodowy Aspromonte?",
            "Co można zobaczyć w Parku Narodowym Aspromonte?",
            "Jak dojechać do Aspromonte?",
            "Jakie szlaki turystyczne są w Aspromonte?",
            "Jakie zwierzęta żyją w Parku Aspromonte?",
        ],
        "brief": (
            "Artykuł o Parku Narodowym Aspromonte w południowej Kalabrii (prowincja Reggio Calabria). "
            "Opisz: lokalizację i zasięg parku, krajobraz (góry, wąwozy, lasy), florę i faunę (wilki, orły, lasy buczyne), "
            "główne atrakcje (Gambarie, wodospady Maesano, Pietra Cappa), szlaki trekkingowe, wskazówki praktyczne (jak dojechać, baza noclegowa). "
            "Ton: przewodnikowy, zachęcający do odwiedzin. "
            "Struktura: intro → H2 sekcje merytoryczne → boc-faq-box → boc-attractions-box → boc-transport-box → boc-nearby-box. "
            "Format HTML Gutenberg z klasami boc-. "
            "Język: polski i angielski (osobne wersje)."
        ),
    },
    {
        "tytul": "Park Narodowy Sila – płaskowyż i lasy Kalabrii",
        "keywords": ["Park Narodowy Sila", "Sila park narodowy", "Sila Kalabria", "Sila trekking", "Jezioro Arvo"],
        "faq": [
            "Gdzie jest Park Narodowy Sila?",
            "Co warto zobaczyć w Parku Narodowym Sila?",
            "Jak dojechać do Parku Sila z Cosenza?",
            "Czy w Sila można uprawiać sporty zimowe?",
            "Jakie jeziora są w Parku Sila?",
        ],
        "brief": (
            "Artykuł o Parku Narodowym Sila – płaskowyżu w centrum Kalabrii. "
            "Opisz: lokalizację (prowincje Cosenza, Catanzaro, Crotone), krajobraz (lasy sosnowe, jeziora sztuczne – Arvo, Ampollino, Cecita), "
            "faunę (wilki, jelenie, wydry), aktywności (trekking latem, narty zimą), główne miejscowości (Camigliatello Silano, San Giovanni in Fiore), "
            "wskazówki praktyczne. "
            "Ton: przewodnikowy, cztery pory roku – park dla rodzin i aktywnych. "
            "Struktura: intro → H2 sekcje merytoryczne → boc-faq-box → boc-attractions-box → boc-transport-box → boc-nearby-box. "
            "Format HTML Gutenberg z klasami boc-."
        ),
    },
    {
        "tytul": "Park Narodowy Pollino – największy park narodowy Włoch",
        "keywords": ["Park Narodowy Pollino", "Pollino park narodowy", "Pollino Kalabria", "Pollino trekking", "Bosco Magnano"],
        "faq": [
            "Gdzie jest Park Narodowy Pollino?",
            "Dlaczego Pollino jest wyjątkowy na tle innych parków Włoch?",
            "Jakie szczyty można zdobyć w Pollino?",
            "Co to jest sosna bośniacka i gdzie ją zobaczyć?",
            "Jak najlepiej zaplanować wizytę w Parku Pollino?",
        ],
        "brief": (
            "Artykuł o Parku Narodowym Pollino – największym parku narodowym Włoch (pogranicze Kalabrii i Basilicaty). "
            "Opisz: powierzchnię i granice parku, najwyższe szczyty (Serra Dolcedorme, Monte Pollino), "
            "unikalne gatunki (Pinus leucodermis – sosna bośniacka, symbol parku), "
            "kanion rzeki Raganello i trekking w nim, spływ kajakowy rzeką Lao, "
            "główne miejscowości bazowe (Civita, Morano Calabro, Castrovillari), "
            "wskazówki praktyczne (sezon, dojazd). "
            "Ton: przygodowy, park dla miłośników dzikiej natury. "
            "Struktura: intro → H2 sekcje merytoryczne → boc-faq-box → boc-attractions-box → boc-transport-box → boc-nearby-box. "
            "Format HTML Gutenberg z klasami boc-."
        ),
    },
    {
        "tytul": "Najlepsze plaże Kalabrii – przewodnik po wybrzeżach",
        "keywords": ["najlepsze plaże Kalabrii", "plaże Kalabria", "Kalabria plaże", "plaże Włochy Kalabria", "Costa degli Dei"],
        "faq": [
            "Jakie są najpiękniejsze plaże Kalabrii?",
            "Która plaża w Kalabrii jest najlepsza dla rodzin z dziećmi?",
            "Kiedy najlepiej jechać na plażę w Kalabrii?",
            "Czy plaże Kalabrii są płatne czy bezpłatne?",
            "Jakie jest morze w Kalabrii – Tyrreńskie czy Jońskie?",
        ],
        "brief": (
            "Przewodnik po najlepszych plażach Kalabrii. "
            "Opisz główne wybrzeża: Costa degli Dei (Tropea, Capo Vaticano), Costa Viola (Scilla, Palmi), "
            "wybrzeże Jońskie (Soverato, Locri, Isola di Capo Rizzuto), Costa dei Cedri na północy. "
            "Wyróżnij top 8–10 plaż z krótkim opisem każdej (typ: skalna/piaszczysta, woda: Tyrreńska/Jońska, rodzinna/dzika). "
            "Dodaj praktyczne info: sezon (czerwiec–wrzesień), lido vs plaża wolna, dojazd. "
            "Ton: inspirujący, przewodnikowy. "
            "Struktura: intro → H2 sekcje (wybrzeże tyrreńskie, jońskie, rady praktyczne) → boc-faq-box → boc-attractions-box (top plaże jako karty) → boc-transport-box → boc-nearby-box. "
            "Format HTML Gutenberg z klasami boc-."
        ),
    },
    {
        "tytul": "Capo Vaticano – skaliste wybrzeże i krystaliczna woda",
        "keywords": ["Capo Vaticano", "Capo Vaticano plaże", "Capo Vaticano Kalabria", "Capo Vaticano wakacje"],
        "faq": [
            "Gdzie jest Capo Vaticano?",
            "Jakie plaże są przy Capo Vaticano?",
            "Jak dojechać do Capo Vaticano?",
            "Co warto zobaczyć oprócz plaży w Capo Vaticano?",
            "Kiedy najlepiej odwiedzić Capo Vaticano?",
        ],
        "brief": (
            "Artykuł o Capo Vaticano – skalistym przylądku na wybrzeżu Kalabrii (gmina Ricadi, prowincja Vibo Valentia). "
            "Opisz: lokalizację (między Tropea a Palmi), krajobraz (klify, zatoczki, turkusowa woda), "
            "główne plaże (Grotticelle, Praia i Focu, Riaci), latarnię morską i punkt widokowy, "
            "snorkeling i nurkowanie w zatoce, dojazd z Tropei i Vibo Valentia, baza noclegowa (agroturystyki, wille). "
            "Ton: letniskowy, zachęcający – dla par i rodzin. "
            "Struktura: intro → H2 sekcje merytoryczne → boc-faq-box → boc-attractions-box → boc-transport-box → boc-nearby-box. "
            "Format HTML Gutenberg z klasami boc-."
        ),
    },
    {
        "tytul": "Costa Viola – Fioletowe Wybrzeże Kalabrii",
        "keywords": ["Costa Viola", "Costa Viola Kalabria", "Costa Viola plaże", "Palmi Costa Viola", "Scilla Costa Viola"],
        "faq": [
            "Gdzie jest Costa Viola?",
            "Skąd pochodzi nazwa Costa Viola?",
            "Jakie miejscowości są na Costa Viola?",
            "Jakie są najlepsze plaże na Costa Viola?",
            "Jak dojechać na Costa Viola?",
        ],
        "brief": (
            "Artykuł o Costa Viola – Fioletowym Wybrzeżu w południowej Kalabrii (między Scillą a Palmi, prowincja Reggio Calabria). "
            "Opisz: pochodzenie nazwy (fioletowe połyski wody przy zachodzie słońca), "
            "główne miejscowości (Scilla, Bagnara Calabra, Palmi, Seminara), "
            "plaże (Palmi – plaża miejska z widokiem na Stromboli, zatoczki Scilli), "
            "tradycje (połowy mieczników – pesca spada, muzeum w Bagnara), "
            "widoki na Sycylię i Wyspy Liparyjskie ze wzgórz, "
            "dojazd autostradą A2 i pociągiem. "
            "Ton: odkrywczy, mniej turystyczny niż Costa degli Dei – autentyczna Kalabria. "
            "Struktura: intro → H2 sekcje merytoryczne → boc-faq-box → boc-attractions-box → boc-transport-box → boc-nearby-box. "
            "Format HTML Gutenberg z klasami boc-."
        ),
    },
]

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def supabase_request(path, token, method="GET", data=None):
    url = f"{SUPABASE_URL}{path}"
    payload = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=payload, method=method)
    req.add_header("apikey", ANON_KEY)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=representation")
    resp = urllib.request.urlopen(req)
    return json.load(resp)


def login():
    payload = json.dumps({"email": EMAIL, "password": PASSWORD}).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        data=payload, method="POST"
    )
    req.add_header("apikey", ANON_KEY)
    req.add_header("Content-Type", "application/json")
    data = json.load(urllib.request.urlopen(req))
    return data["access_token"], data["user"]["id"]


def build_order(temat, domain_id, user_id):
    now = datetime.now(timezone.utc)
    if now.month == 12:
        deadline = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        deadline = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)

    return {
        "domain_id":           domain_id,
        "content_type":        "blog",
        "title":               temat["tytul"],
        "keywords":            temat["keywords"],
        "questions":           temat.get("faq", []),
        "target_audience":     "podróżnicy i turyści planujący wakacje w Kalabrii",
        "tone":                "informative",
        "target_word_count":   1800,
        "chapters":            6,
        "introduction_length": 150,
        "brief":               temat.get("brief", ""),
        "status":              "pending",
        "deadline":            deadline.isoformat(),
        "created_by":          user_id,
    }


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("Logowanie do Supabase...")
    token, user_id = login()
    print(f"OK. user_id = {user_id}\n")

    created = []
    errors  = []

    for i, temat in enumerate(TEMATY, 1):
        print(f"[{i}/{len(TEMATY)}] {temat['tytul'][:70]}")
        try:
            order = build_order(temat, DOMAIN_ID, user_id)
            result = supabase_request(
                "/rest/v1/content_orders",
                token, method="POST", data=order
            )
            order_id = result[0]["id"] if isinstance(result, list) else result["id"]
            created.append({"id": order_id, "title": temat["tytul"]})
            print(f"  ✓ {order_id}")
        except Exception as e:
            errors.append({"title": temat["tytul"], "error": str(e)})
            print(f"  ✗ Błąd: {e}")

    print(f"\n{'='*60}")
    print(f"Wynik: {len(created)} utworzonych, {len(errors)} błędów")

    if created:
        print("\nIDy zleceń:")
        for o in created:
            print(f"  {o['title'][:55]:55} → {o['id']}")


if __name__ == "__main__":
    main()
