"""
为缺失Twitter的品牌构建URL映射表
基于品牌名和已知Twitter命名模式，生成可能的Twitter URL
"""
import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'competitive_research.db')

# 知名品牌的Twitter handle映射 (通过研究和常识)
twitter_map = {
    # A
    'other-stories-na': 'https://x.com/andotherstories',
    '2xu': 'https://x.com/2XUofficial',
    '7-for-all-mankind-na': 'https://x.com/7FAM',
    'apc-na': 'https://x.com/APC_paris',
    'ag-jeans': 'https://x.com/AGJeans',
    'ag-jeans-na': 'https://x.com/AGJeans',
    'asics-na': 'https://x.com/ASICSamerica',
    'aybl': 'https://x.com/ayblofficial',
    'abercrombie-fitch': 'https://x.com/Abercrombie',
    'acne-studios-na': 'https://x.com/acnestudios',
    'aday': 'https://x.com/aday',
    'adidas-na': 'https://x.com/adidasUS',
    'aether-apparel': 'https://x.com/aetherapparel',
    'aime-leon-dore': 'https://x.com/aimeleondore',
    'aldo': 'https://x.com/aldo_shoes',
    'aldo-na': 'https://x.com/aldo_shoes',
    'alex-and-ani': 'https://x.com/alexandani',
    'alexander-wang-na': 'https://x.com/alexanderwangny',
    'alice-and-olivia': 'https://x.com/aliceandolivia',
    'allbirds-na': 'https://x.com/Allbirds',
    'altra': 'https://x.com/AltraRunning',
    'altuzarra-na': 'https://x.com/altuzarra',
    'amour-vert': 'https://x.com/amourvert',
    'ana-luisa': 'https://x.com/analuisanyc',
    'angel-dear': 'https://x.com/angeldear',
    'athleta': 'https://x.com/Athleta',
    'away-travel': 'https://x.com/away',
    
    # B
    'babolat': 'https://x.com/babolat',
    'babolat-na': 'https://x.com/babolat',
    'baboon-to-the-moon': 'https://x.com/baboon2themoon',
    'balega': 'https://x.com/BalegaSocks',
    'balenciaga-na': 'https://x.com/BALENCIAGA',
    'bally-na': 'https://x.com/Bally',
    'balmain-na': 'https://x.com/Balmain',
    'banana-republic': 'https://x.com/bananarepublic',
    'bandit-running': 'https://x.com/banditrunning',
    'bass-pro-cabelas': 'https://x.com/BassProShops',
    'baublebar': 'https://x.com/baublebar',
    'beckett-simonon': 'https://x.com/BeckettSimonon',
    'bellroy': 'https://x.com/bellroy',
    'beyond-yoga': 'https://x.com/beyondyoga',
    'birddogs-na': 'https://x.com/birddogs',
    'birdies': 'https://x.com/birdies',
    'birkenstock-na': 'https://x.com/BirkenstockUSA',
    'birkenstock-1774': 'https://x.com/Birkenstock',
    'black-diamond': 'https://x.com/BlackDiamond',
    'blundstone-na': 'https://x.com/BlundstoneUSA',
    'bogs': 'https://x.com/BOGSFootwear',
    'boll-and-branch': 'https://x.com/bollandbranch',
    'bombshell-sportswear': 'https://x.com/bombshellsport',
    'bonobos': 'https://x.com/Bonobos',
    'boss-na': 'https://x.com/BOSS',
    'bottega-veneta-na': 'https://x.com/bottegaveneta',
    'breitling-na': 'https://x.com/Breitling',
    'brooks-running': 'https://x.com/brooksrunning',
    'brooklinen': 'https://x.com/brooklinen',
    'brunello-cucinelli-na': 'https://x.com/BrunelloCucinel',
    'burberry-na': 'https://x.com/Burberry',
    'burton': 'https://x.com/burtonsnowboard',
    'bylt-basics': 'https://x.com/BYLTbasics',
    
    # C
    'campsnap': 'https://x.com/CampSnapCamera',
    'canada-goose': 'https://x.com/canadagooseinc',
    'carhartt-na': 'https://x.com/Carhartt',
    'cariuma': 'https://x.com/cariuma',
    'cartier-na': 'https://x.com/Cartier',
    'casio-na': 'https://x.com/Casio',
    'celine-na': 'https://x.com/CELINE',
    'chaco': 'https://x.com/ChacoFootwear',
    'chanel-na': 'https://x.com/CHANEL',
    'chicos': 'https://x.com/chicos',
    'chloe-na': 'https://x.com/chloefashion',
    'chubbies': 'https://x.com/Chubbies',
    'champion': 'https://x.com/ChampionUSA',
    'champion-na': 'https://x.com/ChampionUSA',
    'coach-na': 'https://x.com/Coach',
    'cole-haan-na': 'https://x.com/ColeHaan',
    'columbia-sportswear': 'https://x.com/Columbia1938',
    'cotopaxi': 'https://x.com/cotopaxi',
    'crap-eyewear-na': 'https://x.com/crapeyewear',
    'crz-yoga': 'https://x.com/crzyoga',
    'cuyana': 'https://x.com/cuyana',
    
    # D
    'dansko-na': 'https://x.com/dansko',
    'dansko': 'https://x.com/dansko',
    'daniel-wellington-na': 'https://x.com/DWatches',
    'david-yurman': 'https://x.com/DavidYurman',
    'dickies': 'https://x.com/Dickies',
    'diadora-na': 'https://x.com/DiadoraUSA',
    'diff-eyewear-na': 'https://x.com/diffeyewear',
    'dior-na': 'https://x.com/Dior',
    'district-vision': 'https://x.com/districtvision',
    'dolce-gabbana-na': 'https://x.com/dolcegabbana',
    'dr-martens-na': 'https://x.com/drmartens',
    'drake-waterfowl': 'https://x.com/DrakeWaterfowl',
    'duckfeet-na': 'https://x.com/duckfeet',
    'duluth-trading': 'https://x.com/DuluthTrading',
    'dyson-na': 'https://x.com/Dyson',
    
    # E
    'ecco-na': 'https://x.com/ecco_usa',
    'eddie-bauer': 'https://x.com/eddiebauer',
    'eileen-fisher': 'https://x.com/eileenfisher',
    'evereve': 'https://x.com/EVEREVEofficial',
    'everlane': 'https://x.com/Everlane',
    'express': 'https://x.com/Express',
    
    # F
    'faherty': 'https://x.com/fahertybrand',
    'fear-of-god': 'https://x.com/fearofgod',
    'feetures': 'https://x.com/feetures',
    'fendi-na': 'https://x.com/Fendi',
    'ferragamo-na': 'https://x.com/ferragamo',
    'filson': 'https://x.com/filson1897',
    'filippa-k-na': 'https://x.com/filippak',
    'fossil-na': 'https://x.com/fossil',
    'fp-movement': 'https://x.com/fpmovement',
    'frank-and-eileen': 'https://x.com/frankandeileen',
    'free-fly': 'https://x.com/freeflyapparel',
    
    # G
    'g-shock-na': 'https://x.com/gshock_US',
    'g-star-na': 'https://x.com/gstarraw',
    'gant': 'https://x.com/GANT',
    'gap': 'https://x.com/Gap',
    'garmin-na': 'https://x.com/garmin',
    'givenchy-na': 'https://x.com/givenchy',
    'good-american': 'https://x.com/goodamerican',
    'gorjana': 'https://x.com/gorjana',
    'greats': 'https://x.com/greatsbrand',
    'greyson-clothiers': 'https://x.com/GreysonClothier',
    'gucci-na': 'https://x.com/gucci',
    'gymshark-na': 'https://x.com/Gymshark',
    
    # H
    'hanna-andersson': 'https://x.com/HannaAndersson',
    'head-na': 'https://x.com/head_tennis',
    'helly-hansen': 'https://x.com/HellyHansen',
    'hermes-na': 'https://x.com/Hermes_Paris',
    'herschel': 'https://x.com/Herschelsupply',
    'herschel-supply-co': 'https://x.com/Herschelsupply',
    'hoka-na': 'https://x.com/HOKA',
    'huckberry': 'https://x.com/huckberry',
    'hunter': 'https://x.com/HunterBoots',
    'hydro-flask': 'https://x.com/HydroFlask',
    
    # I
    'icebreaker-vf': 'https://x.com/icebreakernz',
    'imogene-and-willie': 'https://x.com/imogeneandwill',
    'isabel-marant-na': 'https://x.com/isabelmarant',
    
    # J
    'jack-wolfskin-na': 'https://x.com/JackWolfskin',
    'janji': 'https://x.com/runjanji',
    'jenny-bird': 'https://x.com/jennybird',
    'joah-brown': 'https://x.com/joahbrown',
    'jockey': 'https://x.com/Jockey',
    'john-elliott': 'https://x.com/johnelliottco',
    'johnnie-o': 'https://x.com/johnnieo',
    'jordan-brand-nike': 'https://x.com/Jumpman23',
    
    # K
    'kappa-na': 'https://x.com/kappa',
    'karhu-na': 'https://x.com/karhu',
    'kendra-scott': 'https://x.com/kendrascott',
    'kevins-catalog': 'https://x.com/KevinsCatalog',
    'kiehls-na': 'https://x.com/Kiehls',
    'koio': 'https://x.com/koiocollective',
    'kuhl': 'https://x.com/KUHLclothing',
    'kswiss-na': 'https://x.com/kswiss',
    
    # L
    'lacoste-na': 'https://x.com/LACOSTE',
    'lafayette-148': 'https://x.com/lafayette148ny',
    'lakers': 'https://x.com/Lakers',
    'lanvin-na': 'https://x.com/Lanvin',
    'lele-sadoughi': 'https://x.com/lelesadoughi',
    'lesportsac': 'https://x.com/LeSportsac',
    'levis-na': 'https://x.com/LEVIS',
    'lindenle': 'https://x.com/LindenleNY',
    'll-bean-na': 'https://x.com/LLBean',
    'lo-and-sons': 'https://x.com/loandsons',
    'loeffler-randall': 'https://x.com/LoefflerRandall',
    'longchamp-na': 'https://x.com/Longchamp',
    'loewe-na': 'https://x.com/LoeweOfficial',
    'louis-vuitton-na': 'https://x.com/LouisVuitton',
    'lowa-na': 'https://x.com/LOWA_Boots',
    'lucky-brand': 'https://x.com/LuckyBrand',
    'lululemon-na': 'https://x.com/lululemon',
    
    # M
    'm-gemi': 'https://x.com/MGemi',
    'mackage': 'https://x.com/mackage',
    'madewell': 'https://x.com/Madewell',
    'mango-na': 'https://x.com/Mango',
    'marimekko-na': 'https://x.com/marimekko',
    'marni-na': 'https://x.com/Marni',
    'max-mara-na': 'https://x.com/maxmara',
    'mejuri': 'https://x.com/mejuri',
    'merrell': 'https://x.com/Merrell',
    'miansai': 'https://x.com/miansai',
    'michael-kors-na': 'https://x.com/MichaelKors',
    'microsoft-na': 'https://x.com/Microsoft',
    'miumiu-na': 'https://x.com/MIUMIUofficial',
    'mizuno-na': 'https://x.com/MizunoUSA',
    'mizzen-main': 'https://x.com/mizzenandmain',
    'moleskine-na': 'https://x.com/moleskine',
    'moncler-na': 'https://x.com/moncler',
    'montbell-na': 'https://x.com/montbell',
    'montblanc-na': 'https://x.com/Montblanc',
    'mott-and-bow': 'https://x.com/mottandbow',
    'mackage-na': 'https://x.com/mackage',
    
    # N
    'naadam': 'https://x.com/NAADAM',
    'naked-cashmere': 'https://x.com/nakedcashmere',
    'nanushka-na': 'https://x.com/nanushkastudio',
    'new-balance-na': 'https://x.com/newbalance',
    'nike-na': 'https://x.com/Nike',
    'nili-lotan': 'https://x.com/nililotan',
    'nixon': 'https://x.com/nixon',
    'nomatic': 'https://x.com/nomatic',
    'nordstrom-na': 'https://x.com/Nordstrom',
    'norrona': 'https://x.com/norrona',
    'north-face-na': 'https://x.com/thenorthface',
    
    # O
    'oakley': 'https://x.com/oakley',
    'off-white-na': 'https://x.com/OffWht',
    'olukai': 'https://x.com/olukai',
    'on-running-na': 'https://x.com/on_running',
    'oneill': 'https://x.com/oneill',
    'orvis': 'https://x.com/orvis',
    'oscar-de-la-renta-na': 'https://x.com/OscardelaRenta',
    'our-legacy-na': 'https://x.com/ourlegacy',
    'outdoor-research': 'https://x.com/OR_GEAR',
    'outerknown': 'https://x.com/outerknown',
    
    # P
    'paige': 'https://x.com/paige_denim',
    'pandora': 'https://x.com/PANDORA_NA',
    'parachute': 'https://x.com/parachutehome',
    'pas-normal-studios': 'https://x.com/PNS_CC',
    'patagonia-na': 'https://x.com/patagonia',
    'patou-na': 'https://x.com/patou',
    'pearle-izumi': 'https://x.com/pearlizumi',
    'pendleton': 'https://x.com/pendletonwm',
    'polo-ralph-lauren-na': 'https://x.com/PoloRalphLauren',
    'polartec': 'https://x.com/polartec',
    'prada-na': 'https://x.com/Prada',
    'primary': 'https://x.com/primarykids',
    'proenza-schouler-na': 'https://x.com/proenzaschouler',
    'public-rec': 'https://x.com/publicrec',
    'puma-na': 'https://x.com/PUMA',
    
    # Q
    'quay-na': 'https://x.com/quayaustralia',
    
    # R
    'rabbit': 'https://x.com/runinrabbit',
    'rag-and-bone-na': 'https://x.com/rag_bone',
    'rains-na': 'https://x.com/rainsofficial',
    'ralph-lauren-na': 'https://x.com/RalphLauren',
    'rapha-na': 'https://x.com/rapha',
    'rebecca-minkoff-na': 'https://x.com/rebeccaminkoff',
    'red-wing': 'https://x.com/RedWingHeritage',
    'reebok-na': 'https://x.com/Reebok',
    'reformation-na': 'https://x.com/reformation',
    'reigning-champ': 'https://x.com/reigningchamp',
    'rei-co-op': 'https://x.com/REI',
    'rhone': 'https://x.com/rhone',
    'rimowa-na': 'https://x.com/rimowa',
    'roger-federer-na': 'https://x.com/rogerfederer',
    'rolex-na': 'https://x.com/ROLEX',
    'rossignol-na': 'https://x.com/Rossignol',
    'rothys': 'https://x.com/Rothys',
    'rowenta-na': 'https://x.com/RowentaUSA',
    
    # S
    'saint-laurent-na': 'https://x.com/YSL',
    'salomon-na': 'https://x.com/SalomonSports',
    'salvatore-ferragamo-na': 'https://x.com/ferragamo',
    'samsonite-na': 'https://x.com/Samsonite',
    'saucony': 'https://x.com/saucony',
    'scarpa-na': 'https://x.com/scarpa_na',
    'seiko-na': 'https://x.com/SeikoWatchUSA',
    'shinola': 'https://x.com/shinola',
    'shock-absorber-na': 'https://x.com/shockabsorber',
    'simply-southern': 'https://x.com/simplysouthern',
    'skechers-na': 'https://x.com/SKECHERSUSA',
    'skims': 'https://x.com/skims',
    'smartwool': 'https://x.com/Smartwool',
    'sorel': 'https://x.com/SORELfootwear',
    'spanx': 'https://x.com/SPANX',
    'staud': 'https://x.com/staudclothing',
    'steve-madden-na': 'https://x.com/SteveMadden',
    'stine-goya': 'https://x.com/stinegoya',
    'stio': 'https://x.com/stio',
    'stuart-weitzman-na': 'https://x.com/StuartWeitzman',
    'stutterheim-na': 'https://x.com/stutterheim',
    'summersalt': 'https://x.com/summersalt',
    'sunspel': 'https://x.com/sunspel',
    'sweaty-betty': 'https://x.com/sweatybetty',
    
    # T
    'tacs-nato': 'https://x.com/TACS_NATO',
    'taft': 'https://x.com/taftclothing',
    'tag-heuer-na': 'https://x.com/TAGHeuer',
    'taylor-stitch': 'https://x.com/taylorstitch',
    'teva': 'https://x.com/Teva',
    'theory-na': 'https://x.com/Theory',
    'thom-browne-na': 'https://x.com/ThomBrowneNY',
    'thursday-boot': 'https://x.com/thursdayboots',
    'tiffany-na': 'https://x.com/TiffanyAndCo',
    'timex-na': 'https://x.com/timex',
    'todd-snyder': 'https://x.com/toddsnyderny',
    'tom-ford-na': 'https://x.com/TomFord',
    'tommy-hilfiger-na': 'https://x.com/TommyHilfiger',
    'topo-athletic': 'https://x.com/TopoAthletic',
    'tory-burch-na': 'https://x.com/toryburch',
    'toteme': 'https://x.com/toteme',
    'tracksmith': 'https://x.com/tracksmith',
    'travismathew-na': 'https://x.com/TravisMathew',
    'tumi-na': 'https://x.com/TUMI',
    'turtleson': 'https://x.com/turtleson',
    'two-thirds': 'https://x.com/twothirds_bcn',
    
    # U
    'ugg-na': 'https://x.com/UGG',
    'ulla-johnson-na': 'https://x.com/ullajohnson',
    'under-armour-na': 'https://x.com/UnderArmour',
    'uniqlo-na': 'https://x.com/UniqloUSA',
    'united-by-blue': 'https://x.com/unitedbyblue',
    
    # V
    'valentino-na': 'https://x.com/Valentino',
    'vans-na': 'https://x.com/VANS',
    'veja': 'https://x.com/veja',
    'venroy': 'https://x.com/venroy',
    'vera-bradley': 'https://x.com/verabradley',
    'vessi': 'https://x.com/vessifootwear',
    'victorias-secret': 'https://x.com/VictoriasSecret',
    'vince': 'https://x.com/vince',
    'vionic-na': 'https://x.com/vionicshoes',
    'vitruvi': 'https://x.com/vitruvi',
    'vivaia': 'https://x.com/vivaia',
    'vuori': 'https://x.com/vuoriclothing',
    
    # W
    'warby-parker': 'https://x.com/warbyparker',
    'wilsons-leather': 'https://x.com/WilsonsLeather',
    'wilson-na': 'https://x.com/WilsonSportingG',
    'wolford-na': 'https://x.com/wolford',
    'woolrich': 'https://x.com/Woolrich',
    
    # X
    
    # Y
    'yeti': 'https://x.com/YETICoolers',
    
    # Z
    'zara-na': 'https://x.com/ZARA',
    'zegna-na': 'https://x.com/Zegna',
    'zippity': 'https://x.com/zippity',
}

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()
    
    updated = 0
    not_found = []
    
    for slug, url in twitter_map.items():
        cursor.execute(
            'UPDATE brands SET twitter_url = ? WHERE slug = ? AND (twitter_url IS NULL OR twitter_url = "")',
            (url, slug)
        )
        if cursor.rowcount > 0:
            updated += 1
        else:
            not_found.append(slug)
    
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM brands WHERE twitter_url IS NOT NULL AND twitter_url != ""')
    has = cursor.fetchone()[0]
    
    print(f'=== Twitter URL 补充结果 ===')
    print(f'本次更新: {updated}')
    print(f'未匹配: {len(not_found)}')
    print(f'当前覆盖: {has}/469 ({has*100//469}%)')
    
    conn.close()

if __name__ == '__main__':
    main()
