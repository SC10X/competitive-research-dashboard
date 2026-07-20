"""
Download brand logos from Clearbit and save them as local static assets.
This is the most reliable way to display logos when external API domains are blocked by user networks.
"""
import sqlite3
import os
import re
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import time

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'competitive_research.db')
# Save to backend/static/logos so FastAPI can serve them
STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'logos')


def extract_domain(website: str) -> str | None:
    if not website:
        return None
    website = website.strip()
    if not website.startswith('http'):
        website = 'https://' + website
    try:
        domain = urlparse(website).netloc
        domain = re.sub(r'^www\.', '', domain)
        return domain.rstrip('/')
    except Exception:
        return None


def download_logo(domain: str, dest_path: str) -> bool:
    """Download logo from Clearbit. Returns True if successful."""
    url = f'https://logo.clearbit.com/{domain}?size=200'
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; LogoBot/1.0)'})
        with urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                data = resp.read()
                if len(data) > 100:  # ensure not empty/error response
                    with open(dest_path, 'wb') as f:
                        f.write(data)
                    return True
    except HTTPError as e:
        print(f"  HTTP error for {domain}: {e.code}")
    except URLError as e:
        print(f"  URL error for {domain}: {e}")
    except Exception as e:
        print(f"  Error downloading {domain}: {e}")
    return False


def main():
    if not os.path.exists(DB_PATH):
        print(f"DB not found: {DB_PATH}")
        return

    os.makedirs(STATIC_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, slug, website, logo_url FROM brands WHERE website IS NOT NULL AND website != ''")
    brands = cur.fetchall()
    print(f"Downloading logos for {len(brands)} brands to {STATIC_DIR}...")

    downloaded = 0
    failed = 0

    for brand_id, slug, website, existing_logo in brands:
        domain = extract_domain(website)
        if not domain:
            failed += 1
            continue

        local_path = os.path.join(STATIC_DIR, f'{slug}.png')
        local_url = f'/logos/{slug}.png'

        # Download if not already exists or if existing is tiny
        if not os.path.exists(local_path) or os.path.getsize(local_path) < 100:
            if download_logo(domain, local_path):
                downloaded += 1
                # Update DB to point to local logo
                cur.execute(
                    "UPDATE brands SET logo_url=?, updated_at=datetime('now') WHERE id=?",
                    (local_url, brand_id)
                )
                if downloaded % 50 == 0:
                    conn.commit()
                    print(f"  Progress: {downloaded}/{len(brands)}")
                time.sleep(0.2)  # be polite to Clearbit
            else:
                failed += 1
                # If existing logo_url was set, keep it; otherwise fallback to Clearbit remote
                if not existing_logo:
                    cur.execute(
                        "UPDATE brands SET logo_url=?, updated_at=datetime('now') WHERE id=?",
                        (f'https://logo.clearbit.com/{domain}', brand_id)
                    )
        else:
            # Already downloaded, just ensure DB points to local
            cur.execute(
                "UPDATE brands SET logo_url=?, updated_at=datetime('now') WHERE id=?",
                (local_url, brand_id)
            )
            downloaded += 1

    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*), COUNT(logo_url) FROM brands")
    total, has_logo = cur.fetchone()
    print(f"\nDone: {downloaded} logos local/updated, {failed} failed")
    print(f"Total brands: {total}, Has logo: {has_logo}")

    conn.close()


if __name__ == '__main__':
    main()
