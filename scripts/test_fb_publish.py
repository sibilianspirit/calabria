"""Testy jednostkowe fb_publish (logika bez sieci). Uruchamiaj z katalogu głównego repo:
    python -m pytest scripts/ -q
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import fb_publish as fp

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _cd_repo_root(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)


@pytest.fixture(scope="module")
def candidates():
    return list(fp.scan_candidates(REPO_ROOT / "content/pl"))


# --- filtr kandydatów -------------------------------------------------------
def test_is_technical():
    assert fp.is_technical(Path("_index.html"))
    assert fp.is_technical(Path("kierunki/_index.html"))
    assert fp.is_technical(Path("blog/_index.html"))
    assert fp.is_technical(Path("kontakt/index.html"))
    assert fp.is_technical(Path("o-nas/index.html"))
    assert not fp.is_technical(Path("kierunki/tropea/_index.html"))
    assert not fp.is_technical(Path("kierunki/tropea/plaze-tropea/index.html"))
    assert not fp.is_technical(Path("blog/najlepsze-plaze-kalabrii.html"))
    assert not fp.is_technical(Path("plaze/index.html"))


def test_scan_excludes_technical(candidates):
    paths = {c["path"] for c in candidates}
    assert "_index.html" not in paths
    assert "kierunki/_index.html" not in paths
    assert "kontakt/index.html" not in paths
    assert "o-nas/index.html" not in paths
    assert "wspolpraca/index.html" not in paths


def test_scan_includes_expected_pages(candidates):
    paths = {c["path"] for c in candidates}
    assert "kierunki/tropea/_index.html" in paths
    assert "kierunki/tropea/plaze-tropea/index.html" in paths
    assert "blog/najlepsze-plaze-kalabrii.html" in paths
    assert "natura/sila/index.html" in paths


def test_scan_fields(candidates):
    assert len(candidates) >= 60
    for c in candidates:
        assert c["title"] and c["description"]
        assert len(c["body"]) >= fp.MIN_BODY_CHARS
        assert "<" not in c["body"][:200]


# --- URL --------------------------------------------------------------------
@pytest.mark.parametrize(
    "rel,expected",
    [
        ("kierunki/tropea/_index.html", "https://bestofcalabria.com/pl/kierunki/tropea/"),
        ("kierunki/tropea/plaze-tropea/index.html", "https://bestofcalabria.com/pl/kierunki/tropea/plaze-tropea/"),
        ("natura/sila/index.html", "https://bestofcalabria.com/pl/natura/sila/"),
        ("plaze/index.html", "https://bestofcalabria.com/pl/plaze/"),
    ],
)
def test_url_for(rel, expected):
    assert fp.url_for(rel) == expected


def test_url_for_blog_matches_hugo_slug(candidates):
    """Wpisy blogowe mają slug w frontmatterze równy nazwie pliku – inaczej URL byłby błędny."""
    import frontmatter

    for c in candidates:
        if c["path"].startswith("blog/"):
            fm = frontmatter.load(str(REPO_ROOT / "content/pl" / c["path"]))
            assert fm.get("slug") == Path(c["path"]).stem, c["path"]


# --- tracking ---------------------------------------------------------------
def test_tracking_roundtrip(tmp_path):
    f = tmp_path / "t.json"
    t = fp.load_tracking(f)
    assert t == {"posts": []}
    assert not fp.is_published(t, "kierunki/tropea/_index.html")
    fp.record(t, "kierunki/tropea/_index.html", "https://x/", "1_2", "tekst")
    fp.save_tracking(t, f)
    t2 = fp.load_tracking(f)
    assert fp.is_published(t2, "kierunki/tropea/_index.html")
    assert t2["posts"][0]["fb_post_id"] == "1_2"
    assert json.loads(f.read_text(encoding="utf-8"))["posts"][0]["message"] == "tekst"


# --- czyszczenie tekstu -----------------------------------------------------
def test_clean_message():
    raw = '"Tropea — perła Kalabrii. https://bestofcalabria.com/x  \n\n\n#Kalabria #Tropea"'
    out = fp.clean_message(raw)
    assert out.startswith("Tropea – perła")
    assert "http" not in out
    assert "\n\n\n" not in out
    assert out.endswith("#Kalabria #Tropea")


def test_clean_message_empty():
    with pytest.raises(RuntimeError):
        fp.clean_message('""')


# --- wybór ------------------------------------------------------------------
def test_choose_pick(monkeypatch):
    rem = [{"path": "a"}, {"path": "b"}]
    monkeypatch.setenv("PICK", "b")
    assert fp.choose(rem)["path"] == "b"
    monkeypatch.setenv("PICK", "zzz")
    with pytest.raises(SystemExit):
        fp.choose(rem)
