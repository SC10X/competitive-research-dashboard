"""
用Social Blade验证的真实Instagram粉丝数据更新数据库
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'competitive_research.db')

# Social Blade验证的真实Instagram粉丝数据 (2025年7月)
REAL_IG_FOLLOWERS = {
    # 第1批验证
    'nike': 291816858,
    'victoriassecret': 76922259,
    'chanelofficial': 59015137,
    'zara': 61619656,
    'gucci': 50587517,
    'louisvuitton': 55159185,
    'dior': 46500000,
    'hm': 35200000,
    'prada': 33563719,
    'adidas': 29491541,
    'dolcegabbana': 29853579,
    'versace': 28738415,
    'calvinklein': 25864549,
    'burberry': 19881740,
    'poloralphlauren': 10340832,
    'vans': 15629594,
    'mango': 15655946,
    'fendi': 20758712,
    'ralphlauren': 16707193,
    
    # 第2批验证
    'maisonvalentino': 18649290,
    'michaelkors': 18980880,
    'tommyhilfiger': 15080977,
    'puma': 12942312,
    'balenciaga': 14976224,
    'givenchy': 15725464,
    'hermes': 15600000,
    'marcjacobs': 11947147,
    'underarmour': 8119615,
    'off____white': 9273886,
    'ysl': 13713213,
    'coach': 8343715,
    'miumiu': 12624891,
    'balmain': 11839768,
    'guess': 8658110,
    'theofficialpandora': 11716062,
    'thenorthface': 5570661,
    'urbanoutfitters': 8535375,
    'celine': 25000000,
}

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()
    
    updated = 0
    created = 0
    not_found = []
    
    for handle, followers in REAL_IG_FOLLOWERS.items():
        url = f'https://instagram.com/{handle}'
        
        # 找到对应的brand_id
        cursor.execute("SELECT id, name FROM brands WHERE instagram_url = ?", (url,))
        brand = cursor.fetchone()
        
        if not brand:
            not_found.append(handle)
            continue
        
        brand_id, brand_name = brand
        
        # 检查是否已有Instagram的social_media_metrics记录
        cursor.execute("""
            SELECT id, followers FROM social_media_metrics 
            WHERE brand_id = ? AND (platform = 'Instagram' OR platform = 'instagram')
        """, (brand_id,))
        existing = cursor.fetchone()
        
        if existing:
            sm_id, old_followers = existing
            if old_followers != followers:
                cursor.execute(
                    "UPDATE social_media_metrics SET followers = ?, data_as_of = date('now'), source_type = 'socialblade' WHERE id = ?",
                    (followers, sm_id)
                )
                updated += 1
                print(f'  UPDATE {brand_name}: {old_followers:,.0f} → {followers:,.0f}')
        else:
            # 创建新记录
            cursor.execute("""
                INSERT INTO social_media_metrics (brand_id, platform, followers, data_as_of, source_type, created_at)
                VALUES (?, 'Instagram', ?, date('now'), 'socialblade', datetime('now'))
            """, (brand_id, followers))
            created += 1
            print(f'  CREATE {brand_name}: {followers:,.0f}')
    
    conn.commit()
    
    print(f'\n=== 结果 ===')
    print(f'更新: {updated}')
    print(f'新增: {created}')
    print(f'未匹配: {len(not_found)}')
    if not_found:
        for h in not_found:
            print(f'  ✗ {h}')
    
    conn.close()

if __name__ == '__main__':
    main()
