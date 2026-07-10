"""
补充最后46个缺失母公司的品牌
这些品牌大部分是国际知名品牌或其北美分支
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'competitive_research.db')

# 精确的母公司映射 - 经过核实的品牌所有权信息
parent_map = {
    # 独立大公司 (没有传统意义上的"母公司"，但可以标注为独立)
    'chanel-na': 'Chanel Limited (私有独立)',
    'chanel': 'Chanel Limited (私有独立)',
    'hermes-na': 'Hermès International (独立上市)',
    'hermes': 'Hermès International (独立上市)',
    'burberry-na': 'Burberry Group plc (独立上市)',
    'burberry': 'Burberry Group plc (独立上市)',
    'ralph-lauren-na': 'Ralph Lauren Corporation (独立上市)',
    'ralph-lauren': 'Ralph Lauren Corporation (独立上市)',
    'pandora': 'Pandora A/S (独立上市)',
    'fossil-na': 'Fossil Group, Inc. (独立上市)',
    'fossil': 'Fossil Group, Inc. (独立上市)',
    'tory-burch-na': 'Tory Burch LLC (私有独立)',
    'tory-burch': 'Tory Burch LLC (私有独立)',
    'david-yurman': 'David Yurman Enterprises (私有独立)',
    'steve-madden-na': 'Steve Madden, Ltd. (独立上市)',
    'steve-madden': 'Steve Madden, Ltd. (独立上市)',
    'carhartt-na': 'Carhartt, Inc. (私有独立)',
    'carhartt': 'Carhartt, Inc. (私有独立)',
    'herschel': 'Herschel Supply Co. (私有独立)',
    'herschel-supply-co': 'Herschel Supply Co. (私有独立)',
    
    # 知名品牌集团
    'alexander-wang-na': 'Alexander Wang Inc. (私有独立)',
    'alexander-wang': 'Alexander Wang Inc. (私有独立)',
    'acne-studios-na': 'Acne Studios Holding AB (私有独立)',
    'acne-studios': 'Acne Studios Holding AB (私有独立)',
    'brunello-cucinelli-na': 'Brunello Cucinelli S.p.A. (独立上市)',
    'brunello-cucinelli': 'Brunello Cucinelli S.p.A. (独立上市)',
    'dolce-gabbana-na': 'Dolce & Gabbana S.r.l. (私有独立)',
    'dolce-gabbana': 'Dolce & Gabbana S.r.l. (私有独立)',
    'max-mara-na': 'Max Mara Fashion Group (私有独立)',
    'max-mara': 'Max Mara Fashion Group (私有独立)',
    'proenza-schouler-na': 'Proenza Schouler LLC (私有独立)',
    'proenza-schouler': 'Proenza Schouler LLC (私有独立)',
    
    # 运动/户外品牌
    'diadora-na': 'Diadora S.p.A. (私有独立)',
    'diadora': 'Diadora S.p.A. (私有独立)',
    'babolat-na': 'Babolat S.A.S. (私有独立)',
    'babolat': 'Babolat S.A.S. (私有独立)',
    'ecco-na': 'ECCO Sko A/S (私有独立)',
    'ecco': 'ECCO Sko A/S (私有独立)',
    'lowa-na': 'LOWA Sportschuhe GmbH (Tecnica Group)',
    'lowa': 'LOWA Sportschuhe GmbH (Tecnica Group)',
    'montbell-na': 'Montbell Co., Ltd. (私有独立)',
    'montbell': 'Montbell Co., Ltd. (私有独立)',
    'dansko-na': 'Dansko LLC (私有独立)',
    'dansko': 'Dansko LLC (私有独立)',
    
    # 配饰/眼镜品牌
    'apc-na': 'A.P.C. SAS (私有独立)',
    'apc': 'A.P.C. SAS (私有独立)',
    'quay-na': 'Quay Australia (私有独立)',
    'quay': 'Quay Australia (私有独立)',
    'diff-eyewear-na': 'Diff Eyewear LLC (私有独立)',
    'diff-eyewear': 'Diff Eyewear LLC (私有独立)',
    'crap-eyewear-na': 'Crap Eyewear (私有独立)',
    'crap-eyewear': 'Crap Eyewear (私有独立)',
    'daniel-wellington-na': 'Daniel Wellington AB (私有独立)',
    'daniel-wellington': 'Daniel Wellington AB (私有独立)',
    'miansai': 'Miansai Inc. (私有独立)',
    
    # 时装品牌
    'altuzarra-na': 'Altuzarra LLC (私有独立)',
    'altuzarra': 'Altuzarra LLC (私有独立)',
    'filippa-k-na': 'Filippa K AB (私有独立)',
    'filippa-k': 'Filippa K AB (私有独立)',
    'nanushka-na': 'Nanushka International (私有独立)',
    'nanushka': 'Nanushka International (私有独立)',
    'our-legacy-na': 'Our Legacy AB (私有独立)',
    'our-legacy': 'Our Legacy AB (私有独立)',
    'ulla-johnson-na': 'Ulla Johnson LLC (私有独立)',
    'ulla-johnson': 'Ulla Johnson LLC (私有独立)',
    
    # DTC / 新兴品牌
    'birddogs-na': 'Birddogs Inc. (私有独立)',
    'birddogs': 'Birddogs Inc. (私有独立)',
    'summersalt': 'Summersalt Inc. (私有独立)',
    'greyson-clothiers': 'Greyson Clothiers LLC (私有独立)',
    'crz-yoga': 'CRZ Yoga (私有独立)',
    
    # 户外/雨具
    'stutterheim-na': 'Stutterheim AB (私有独立)',
    'stutterheim': 'Stutterheim AB (私有独立)',
    'rains-na': 'Rains ApS (私有独立)',
    'rains': 'Rains ApS (私有独立)',
    'duckfeet-na': 'Duckfeet ApS (私有独立)',
    'duckfeet': 'Duckfeet ApS (私有独立)',
    
    # 手表
    'timex-na': 'Timex Group B.V. (私有独立)',
    'timex': 'Timex Group B.V. (私有独立)',
    
    # 运动/骑行
    'rapha-na': 'Rapha Racing Ltd. (私有独立)',
    'rapha': 'Rapha Racing Ltd. (私有独立)',
    
    # 内衣/运动
    'shock-absorber-na': 'Shock Absorber (私有独立)',
    'shock-absorber': 'Shock Absorber (私有独立)',
    
    # 珠宝
    'alex-and-ani': 'Alex and Ani LLC (私有独立)',
}

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()
    
    updated = 0
    not_found = []
    
    for slug, parent in parent_map.items():
        cursor.execute(
            'UPDATE brands SET parent_company = ? WHERE slug = ? AND (parent_company IS NULL OR parent_company = "")',
            (parent, slug)
        )
        if cursor.rowcount > 0:
            updated += 1
            print(f'  ✓ {slug} → {parent}')
        else:
            not_found.append(slug)
    
    conn.commit()
    
    # 检查剩余缺失
    cursor.execute('SELECT COUNT(*) FROM brands WHERE parent_company IS NULL OR parent_company = ""')
    remaining = cursor.fetchone()[0]
    
    cursor.execute('SELECT slug, name FROM brands WHERE parent_company IS NULL OR parent_company = "" ORDER BY name')
    remaining_list = cursor.fetchall()
    
    print(f'\n=== 结果 ===')
    print(f'本次更新: {updated}')
    print(f'未匹配: {len(not_found)}')
    if not_found:
        for s in not_found:
            print(f'  ✗ {s}')
    print(f'剩余缺失: {remaining}/{469}')
    if remaining_list:
        print('剩余品牌:')
        for s, n in remaining_list:
            print(f'  {s}: {n}')
    
    conn.close()

if __name__ == '__main__':
    main()
