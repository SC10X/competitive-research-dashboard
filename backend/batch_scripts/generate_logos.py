"""
Generate logo_url for all brands from website domains using Icon.Horse API.
Icon.Horse pattern: https://icon.horse/icon/{domain}
Returns PNG favicons with high compatibility.
"""
import sqlite3
import os
import re
from urllib.parse import urlparse

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'competitive_research.db')


def extract_domain(website: str) -> str | None:
    """Extract clean domain from website URL."""
    if not website:
        return None
    website = website.strip()
    if not website.startswith('http'):
        website = 'https://' + website
    try:
        parsed = urlparse(website)
        domain = parsed.netloc or parsed.path
        # Remove www. prefix
        domain = re.sub(r'^www\.', '', domain)
        # Remove trailing slash
        domain = domain.rstrip('/')
        return domain
    except Exception:
        return None


def main():
    if not os.path.exists(DB_PATH):
        print(f"DB not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get all brands with website but no logo or with old logo source
    cur.execute("""
        SELECT id, name, website FROM brands 
        WHERE website IS NOT NULL AND website != '' 
        AND (logo_url IS NULL OR logo_url = '' OR logo_url LIKE '%clearbit%' OR logo_url LIKE '%favicone%')
    """)
    brands = cur.fetchall()
    print(f"Found {len(brands)} brands needing logo_url")

    updated = 0
    failed = 0

    for brand_id, name, website in brands:
        domain = extract_domain(website)
        if domain:
            logo_url = f"https://icon.horse/icon/{domain}"
            cur.execute(
                "UPDATE brands SET logo_url = ?, updated_at = datetime('now') WHERE id = ?",
                (logo_url, brand_id)
            )
            updated += 1
            if updated % 50 == 0:
                print(f"  Progress: {updated}/{len(brands)}")
        else:
            failed += 1
            print(f"  Failed to parse domain for {name}: {website}")

    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*), COUNT(logo_url) FROM brands")
    total, has_logo = cur.fetchone()
    print(f"\nDone: {updated} updated, {failed} failed")
    print(f"Total brands: {total}, Has logo: {has_logo} ({has_logo/total*100:.1f}%)")

    # Show samples
    cur.execute("SELECT name, website, logo_url FROM brands WHERE logo_url IS NOT NULL LIMIT 5")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} -> {row[2]}")

    conn.close()


if __name__ == '__main__':
    main()
