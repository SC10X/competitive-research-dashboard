"""
Runtime database updates — runs at container startup to apply
data changes that may not be reflected in the Docker image cache.
"""
import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'competitive_research.db')

def apply_updates():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}, skipping updates")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check if instagram_url column has data
    cur.execute("SELECT COUNT(*) FROM brands WHERE instagram_url IS NOT NULL")
    has_ig = cur.fetchone()[0]
    
    if has_ig > 0:
        print(f"DB already has {has_ig} instagram URLs, skipping updates")
        conn.close()
        return
    
    print(f"DB has 0 instagram URLs, applying updates...")
    
    # Add columns if missing
    for col in ['instagram_url', 'twitter_url', 'tiktok_url']:
        try:
            cur.execute(f'ALTER TABLE brands ADD COLUMN {col} VARCHAR(300)')
        except:
            pass
    
    # Standardize price tiers
    tier_map = {
        'Luxury': 'Luxury', 'luxury': 'Luxury', 'Premium-Luxury': 'Luxury',
        'premium_luxury': 'Luxury', 'contemporary_luxury': 'Luxury',
        'Premium': 'Premium', 'Premium DTC': 'Premium',
        'Mid': 'Mid', 'Mid-Market': 'Mid', 'mid_range': 'Mid',
        'Mid-Premium': 'Mid', 'Mid Premium': 'Mid', 'Mass Premium': 'Mid',
        'Mass': 'Mass', 'Mass Market': 'Mass', 'Mass-Market': 'Mass',
        'mass_market': 'Mass', 'Mass DTC': 'Mass', 'Budget-Friendly': 'Mass',
    }
    for old, new in tier_map.items():
        cur.execute('UPDATE brand_positioning SET price_tier=? WHERE price_tier=?', (new, old))
    
    # Apply Instagram URLs
    ig_handles = {
        '& Other Stories': 'andotherstories', '2XU': '2xu', '7 For All Mankind': '7forallmankind',
        'A.P.C.': 'apc_paris', 'AG Jeans': 'agjeans', 'ASICS': 'asics',
        'AYBL': 'aybl', 'Abercrombie & Fitch': 'abercrombie', 'Acne Studios': 'acnestudios',
        'Aday': 'aday', 'Adidas': 'adidas', 'Aether Apparel': 'aetherapparel',
        'Aime Leon Dore': 'aimeleondore', 'Aldo': 'aldo',
        'Alexander Wang': 'alexanderwang', 'Alice + Olivia': 'aliceolivia',
        'Allbirds': 'allbirds', 'Alo Yoga': 'aloyoga', 'Altuzarra': 'altuzarra',
        'American Eagle': 'americaneagle', 'American Giant': 'americangiant',
        'Arc\'teryx': 'arcteryx', 'Athleta': 'athleta', 'Away': 'away',
        'Balenciaga': 'balenciaga', 'Balmain': 'balmain', 'Banana Republic': 'bananarepublic',
        'Beyond Yoga': 'beyondyoga', 'Birkenstock': 'birkenstock', 'Black Diamond': 'blackdiamond',
        'Blundstone': 'blundstone', 'Bode': 'bode', 'Bonobos': 'bonobos',
        'Bottega Veneta': 'bottegaveneta', 'Brooks': 'brooksrunning', 'Brunello Cucinelli': 'brunellocucinelli',
        'Burberry': 'burberry', 'Burton': 'burtonsnowboards',
        'Canada Goose': 'canadagoose', 'Carhartt': 'carhartt', 'Cartier': 'cartier',
        'Celine': 'celine', 'Champion': 'champion', 'Chanel': 'chanelofficial',
        'Chrome Hearts': 'chromeheartsofficial', 'Coach': 'coach', 'Columbia': 'columbia1938',
        'Common Projects': 'commonprojects', 'Converse': 'converse', 'Cotopaxi': 'cotopaxi',
        'Crocs': 'crocs', 'Cuyana': 'cuyana', 'Dagne Dover': 'dagnedover',
        'Dior': 'dior', 'Dr. Martens': 'drmartensofficial', 'Everlane': 'everlane',
        'Fendi': 'fendi', 'Filson': 'filson1897', 'Gap': 'gap',
        'Girlfriend Collective': 'girlfriendcollective', 'Golden Goose': 'goldengoose',
        'Gucci': 'gucci', 'Gymshark': 'gymshark',
        'H&M': 'hm', 'Helly Hansen': 'hellyhansen', 'Hermes': 'hermes',
        'HeyDude': 'heydude', 'Hoka': 'hoka', 'Hollister': 'hollisterco',
        'J.Crew': 'jcrew', 'Jacquemus': 'jacquemus', 'JanSport': 'jansport',
        'Keen': 'keen', 'Kith': 'kith', 'Lacoste': 'lacoste',
        "Levi's": 'levis', 'Louis Vuitton': 'louisvuitton', 'Lululemon': 'lululemon',
        'Madewell': 'madewell', 'Mansur Gavriel': 'mansurgavriel', 'Marc Jacobs': 'marcjacobs',
        'Merrell': 'merrell', 'Michael Kors': 'michaelkors', 'Moncler': 'moncler',
        'New Balance': 'newbalance', 'Nike': 'nike', 'North Face': 'thenorthface',
        'Off-White': 'off____white', 'On': 'on', 'Outdoor Voices': 'outdoorvoices',
        'Patagonia': 'patagonia', 'Polo Ralph Lauren': 'poloralphlauren', 'Prada': 'prada',
        'Puma': 'puma', 'Ralph Lauren': 'ralphlauren', 'Reebok': 'reebok',
        'Reformation': 'reformation', 'Rhone': 'rhone', 'Rimowa': 'rimowa',
        'Rothy\'s': 'rothys', 'Salomon': 'salomon', 'Saucony': 'saucony',
        'Skechers': 'skechers', 'Skims': 'skims', 'Staud': 'staud.clothing',
        'Steve Madden': 'stevemadden', 'Stone Island': 'stoneisland_official',
        'Stussy': 'stussy', 'Supreme': 'supremenewyork',
        'Teva': 'teva', 'Timberland': 'timberland', 'Toms': 'toms',
        'Tory Burch': 'toryburch', 'Tumi': 'tumi',
        'UGG': 'ugg', 'Under Armour': 'underarmour', 'Uniqlo': 'uniqlo',
        'Urban Outfitters': 'urbanoutfitters',
        'Valentino': 'maisonvalentino', 'Vans': 'vans', 'Veja': 'veja',
        'Versace': 'versace', 'Vuori': 'vuoriclothing',
        'Warby Parker': 'warbyparker', 'Yeezy': 'yeezy',
        'Zara': 'zara', 'Zegna': 'zegnaofficial',
    }
    
    updated = 0
    for name, handle in ig_handles.items():
        url = f'https://instagram.com/{handle}'
        # Match brand names with or without (北美) suffix
        cur.execute(
            "UPDATE brands SET instagram_url=? WHERE name=? OR name=?",
            (url, name, name + ' (北美)')
        )
        if cur.rowcount > 0:
            updated += cur.rowcount
    
    # Also handle brands not in the explicit list
    cur.execute("SELECT id, name FROM brands WHERE instagram_url IS NULL")
    no_ig = cur.fetchall()
    for bid, bname in no_ig:
        clean = bname.replace(' (北美)', '').replace(' (北美线)', '').lower()
        clean = clean.replace(' ', '').replace("'", '').replace('.', '').replace('&', 'and').replace('+', '')
        url = f'https://instagram.com/{clean}'
        cur.execute("UPDATE brands SET instagram_url=? WHERE id=?", (url, bid))
        updated += 1
    
    conn.commit()
    conn.close()
    print(f"Applied updates: {updated} instagram URLs, standardized price tiers")

if __name__ == '__main__':
    apply_updates()
