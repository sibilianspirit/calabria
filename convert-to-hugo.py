#!/usr/bin/env python3
"""Convert wp-backup HTML files to Hugo content structure."""

import os
import re
import shutil
import yaml

BACKUP = "/mnt/c/projekty/calabria/wp-backup"
HUGO_CONTENT = "/mnt/c/projekty/calabria/content"
HUGO_STATIC = "/mnt/c/projekty/calabria/static"

# Translation key mapping: PL path -> EN path (for linking translations)
PL_EN_MAP = {
    "pl/kierunki": "destinations",
    "pl/natura": "nature",
    "pl/kuchnia": "cuisine",
    "pl/kultura": "culture",
    "pl/praktyczne": "practical",
    "pl/kontakt": "contact",
    "pl/o-nas": "about",
    "pl/wspolpraca": "partnership",
    "pl/plaze": "nature/beaches",
}

# Slug mapping for translation keys (PL slug -> EN slug)
SLUG_MAP = {
    "bronzy-z-riace": "bronzi-di-riace",
    "kosciol-piedigrotta": "piedigrotta-church",
    "castello-murat": "castello-murat",
    "tartufo-gelato": "tartufo-gelato",
    "tradycja-polowu-miecznika": "swordfish-tradition",
    "castello-ruffo": "castello-ruffo",
    "festiwal-czerwonej-cebuli": "red-onion-festival",
    "plaze-tropea": "tropea-beaches",
    "santa-maria-dell-isola": "santa-maria-dell-isola",
    "dziedzictwo-grekanickie": "grecanico-heritage",
    "dziedzictwo-bizantyjskie": "byzantine-heritage",
    "tradycje-i-festiwale": "traditions-festivals",
    "magna-graecia": "magna-graecia",
    "bergamotka": "bergamot",
    "makaron-fileja": "fileja-pasta",
    "wino-kalabryjskie": "calabrian-wine",
    "nduja": "nduja",
    "street-food": "street-food",
    "jak-dojechac": "getting-there",
    "noclegi": "accommodation",
    "wynajem-samochodu": "car-rental",
    "plan-7-dni": "itinerary-7-days",
    "kierunki": "destinations",
    "natura": "nature",
    "kuchnia": "cuisine",
    "kultura": "culture",
    "praktyczne": "practical",
    "aspromonte": "aspromonte",
    "sila": "sila",
    "pollino": "pollino",
    "costa-viola": "costa-viola",
    "capo-vaticano": "capo-vaticano",
}

# Pages to skip (duplicates, old theme pages)
SKIP_PATHS = {"about-2", "contact-2", "home", "pl/homepl", "pl"}

def strip_gutenberg_comments(html):
    """Remove Gutenberg block comments, keep HTML content."""
    html = re.sub(r'<!-- /?wp:\w+[^>]*-->\n?', '', html)
    # Clean up excessive blank lines
    html = re.sub(r'\n{3,}', '\n\n', html)
    return html.strip()

def fix_image_urls(html):
    """Replace WP image URLs with local Hugo paths."""
    html = html.replace(
        'https://bestofcalabria.com/wp-content/uploads/',
        '/images/wp-uploads/'
    )
    return html

def get_translation_key(path):
    """Generate a translation key that matches PL and EN pages."""
    # For PL pages, map to EN equivalent
    for pl_prefix, en_prefix in PL_EN_MAP.items():
        if path.startswith(pl_prefix + "/"):
            rest = path[len(pl_prefix) + 1:]
            # Map PL slug to EN slug
            parts = rest.split("/")
            mapped_parts = [SLUG_MAP.get(p, p) for p in parts]
            return en_prefix + "/" + "/".join(mapped_parts)
        elif path == pl_prefix:
            return en_prefix

    # For EN pages, key is the path itself
    return path

def determine_lang(path):
    """Determine language from path."""
    if path.startswith("pl/"):
        return "pl"
    return "en"

def convert_page(backup_path, rel_path):
    """Convert a single backup page to Hugo content."""
    src = os.path.join(backup_path, "index.html")
    if not os.path.exists(src):
        return False

    with open(src, "r", encoding="utf-8") as f:
        raw = f.read()

    # Parse frontmatter
    if not raw.startswith("---"):
        return False

    parts = raw.split("---", 2)
    if len(parts) < 3:
        return False

    meta = yaml.safe_load(parts[1])
    content = parts[2].strip()

    if not content:
        return False

    title = meta.get("title", "")
    slug = meta.get("slug", "")
    wp_id = meta.get("wp_id", "")

    lang = determine_lang(rel_path)
    trans_key = get_translation_key(rel_path)

    # Process content
    content = strip_gutenberg_comments(content)
    content = fix_image_urls(content)

    # Build Hugo frontmatter
    hugo_meta = {
        "title": title,
        "slug": slug,
        "translationKey": trans_key,
        "wp_id": wp_id,
    }

    # Determine output path
    if lang == "pl":
        # PL content goes under content/pl/...
        # Strip the pl/ prefix since Hugo handles it via language config
        hugo_path = os.path.join(HUGO_CONTENT, rel_path)
    else:
        hugo_path = os.path.join(HUGO_CONTENT, rel_path)

    os.makedirs(hugo_path, exist_ok=True)
    out_file = os.path.join(hugo_path, "index.html")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(yaml.dump(hugo_meta, allow_unicode=True, default_flow_style=False))
        f.write("---\n\n")
        f.write(content)
        f.write("\n")

    return True

def copy_images():
    """Copy media to Hugo static directory."""
    media_src = os.path.join(BACKUP, "media")
    # Copy to static/images/ for direct access
    img_dest = os.path.join(HUGO_STATIC, "images", "wp-uploads", "2026")

    # Organize by date folder like WP did
    for subdir in ["02", "03"]:
        dest = os.path.join(img_dest, subdir)
        os.makedirs(dest, exist_ok=True)

    for f in os.listdir(media_src):
        if f == "media-index.json":
            continue
        src = os.path.join(media_src, f)
        # Determine date folder from filename patterns
        if f.startswith("boc-") or f.startswith("best-of-calabria-logo-scaled"):
            dest = os.path.join(img_dest, "03", f)
        else:
            dest = os.path.join(img_dest, "02", f)
        shutil.copy2(src, dest)
        print(f"  img: {f}")

def main():
    # Clean existing content (except the test tropea we already have)
    if os.path.exists(HUGO_CONTENT):
        shutil.rmtree(HUGO_CONTENT)
    os.makedirs(HUGO_CONTENT)

    print("Converting pages to Hugo content...\n")

    converted = 0
    skipped = 0

    for root, dirs, files in os.walk(BACKUP):
        if "index.html" not in files:
            continue
        if "media" in root:
            continue

        rel = os.path.relpath(root, BACKUP)

        if rel in SKIP_PATHS:
            print(f"  skip: {rel}")
            skipped += 1
            continue

        if convert_page(root, rel):
            print(f"  ✓ {rel}")
            converted += 1
        else:
            print(f"  ✗ {rel} (failed)")
            skipped += 1

    print(f"\nPages: {converted} converted, {skipped} skipped")

    print("\nCopying images...")
    copy_images()

    print("\nDone!")

if __name__ == "__main__":
    main()
