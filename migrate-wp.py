#!/usr/bin/env python3
"""Migrate all WP pages to Hugo markdown files."""

import json
import os
import re
import requests
from urllib.parse import urlparse

API = "https://bestofcalabria.com/wp-json/wp/v2/pages"
AUTH = ("admin", "JwGw oBQ1 yaHo hXeg oadm Kx86")
OUT = "/mnt/c/projekty/calabria/wp-backup"

# URL structure mapping for Hugo content directories
# PL pages nested under /pl/ prefix
# EN pages at root

def get_all_pages():
    """Fetch all pages from WP API."""
    pages = []
    page_num = 1
    while True:
        r = requests.get(API, auth=AUTH, params={
            "per_page": 100,
            "page": page_num,
            "context": "edit"
        })
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        pages.extend(batch)
        page_num += 1
    return pages

def get_page_path(page):
    """Determine Hugo content path from WP page link."""
    link = page.get("link", "")
    parsed = urlparse(link)
    path = parsed.path.strip("/")

    if not path:
        return None

    return path

def sanitize_content(content):
    """Keep raw HTML/Gutenberg content as-is for backup."""
    return content

def save_page(page):
    """Save a single page as markdown with frontmatter."""
    slug = page.get("slug", "")
    title = page.get("title", {}).get("raw", "")
    content = page.get("content", {}).get("raw", "")
    excerpt = page.get("excerpt", {}).get("raw", "")
    status = page.get("status", "")
    page_id = page.get("id", "")
    link = page.get("link", "")
    parent = page.get("parent", 0)

    if not slug or not content:
        return False

    # Determine path from link
    path = get_page_path(page)
    if not path:
        return False

    # Create directory structure mirroring URL
    dir_path = os.path.join(OUT, path)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "index.html")

    # Build frontmatter
    frontmatter = f"""---
title: "{title.replace('"', '\\"')}"
slug: "{slug}"
wp_id: {page_id}
wp_link: "{link}"
wp_parent: {parent}
status: "{status}"
---

"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(content)

    return True

def main():
    os.makedirs(OUT, exist_ok=True)

    print("Fetching all pages from WordPress...")
    pages = get_all_pages()
    print(f"Found {len(pages)} pages")

    saved = 0
    skipped = 0
    for page in pages:
        if save_page(page):
            title = page.get("title", {}).get("raw", "")
            print(f"  ✓ {page['id']} {title}")
            saved += 1
        else:
            title = page.get("title", {}).get("raw", "")
            print(f"  ✗ {page['id']} {title} (empty/no path)")
            skipped += 1

    print(f"\nDone: {saved} saved, {skipped} skipped")
    print(f"Backup location: {OUT}")

if __name__ == "__main__":
    main()
