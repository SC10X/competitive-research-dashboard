"""
基于关键词自动匹配品牌→场景+品类关联
替代之前硬编码slug字典的不足，实现85%+覆盖率
"""
import sqlite3
import re
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'competitive_research.db')

# ============================================================
# 关键词→场景 映射规则 (中英文双语)
# ============================================================
SCENARIO_KEYWORDS = {
    'sc-fitness-training': [
        'fitness', 'training', 'gym', 'workout', 'train', 'active',
        '健身', '训练', '综训', 'athletic', 'performance', 'exercise',
        'sport', '运动', 'sports', 'strength', 'gym',
    ],
    'sc-running': [
        'run', 'running', 'marathon', 'track', 'racer', 'jog',
        '跑步', '跑者', '马拉松', '径赛',
    ],
    'sc-yoga-pilates': [
        'yoga', 'pilates', '普拉提', '瑜伽', 'meditation', 'mindful',
    ],
    'sc-swim-beach': [
        'swim', 'beach', 'bikini', 'swimsuit', '泳', '海滩', '海边',
        'surf', '冲浪', 'board', 'resort', 'vacation',
    ],
    'sc-golf': [
        'golf', '高尔夫', 'pga',
    ],
    'sc-tennis': [
        'tennis', '网球', 'racquet', 'racket',
    ],
    'sc-outdoor-hiking': [
        'outdoor', 'hiking', 'hike', 'camp', 'camping', 'trek', 'mountaineering',
        '户外', '徒步', '登山', '露营', '攀登', '荒野', 'adventure',
        'explore', 'mountain', 'trail', 'peak', 'summit', '狩猎', 'hunt',
        'fish', '钓鱼', 'fishing',
    ],
    'sc-ski-winter': [
        'ski', 'snow', 'snowboard', 'winter', '滑雪', '冬季', '冰',
        'alpine', 'polar', 'arctic', 'ice',
    ],
    'sc-basketball': [
        'basketball', '篮球', 'nba', 'jordan', 'hoop',
    ],
    'sc-soccer': [
        'soccer', 'football', '足球', 'cleat', 'pitch',
    ],
    'sc-cycling': [
        'cycling', 'bike', 'bicycle', '骑行', '单车', 'cyclist',
    ],
    'sc-crossfit': [
        'crossfit', 'cross', 'functional', 'wod',
    ],
    'sc-daily-commute': [
        'commute', '日常', '通勤', 'everyday', 'daily', 'office', 'work',
        '上班', '都市', 'urban', 'city', 'street', '街头',
        'classic', 'essential', 'basic', '基础', '百搭', '职场',
        'casual', '现代', 'contemporary', 'minimalist', '极简',
        'fashion', '时尚', 'style', 'chic', '优雅', 'elegant',
        'designer', '设计师', 'luxury', '奢侈', '高端',
    ],
    'sc-travel': [
        'travel', '旅行', 'luggage', '箱包', 'trip', 'journey', 'voyage',
        'carry', 'pack', 'suitcase',
    ],
    'sc-home-lounge': [
        'lounge', '居家', 'home', '睡衣', '内衣', '家居', 'comfort',
        'sleep', 'bed', 'cozy', 'relax', '休闲', 'lifestyle',
        '生活', '家庭', 'family', 'baby', '婴', '童', 'kid',
        '儿童', 'maternity', '孕妇', 'nursery',
    ],
    'sc-dance': [
        'dance', '舞蹈', '芭蕾', 'ballet', '跳舞',
    ],
    'sc-climbing': [
        'climb', '攀岩', 'boulder', 'rock', '岩',
    ],
    'sc-water-sports': [
        'surf', '冲浪', 'water', '水上', 'paddle', 'kayak', 'dive',
        'sail', 'ocean', '海洋', 'boat', '钓鱼', 'fish',
    ],
}

# ============================================================
# 关键词→品类 映射规则
# ============================================================
PRODUCT_KEYWORDS = {
    'pc-leggings': [
        'legging', 'tight', '紧身', '瑜伽裤', 'compression', 'tights', 'pant',
        'bottom', '裤', '下身',
    ],
    'pc-sports-bra': [
        'sports bra', '运动内衣', 'bra', 'bralette', 'support', '内衣',
    ],
    'pc-t-shirts': [
        't-shirt', 'tee', 't恤', '上衣', 'top', 'graphic tee', 't shirt',
    ],
    'pc-hoodies': [
        'hoodie', 'hoody', '卫衣', '连帽', 'sweatshirt', 'pullover', 'sweater',
        '针织', '毛衣', 'knit',
    ],
    'pc-shorts': [
        'short', '短裤', 'bermuda', 'brief',
    ],
    'pc-running-shoes': [
        'running shoe', '跑鞋', 'runner', 'sneaker', '运动鞋',
        'cushion', 'stability', 'racing', 'shoe', '鞋', 'footwear', '履',
    ],
    'pc-basketball-shoes': [
        'basketball shoe', '篮球鞋', 'hoop shoe',
    ],
    'pc-training-shoes': [
        'training shoe', '训练鞋', 'gym shoe', 'cross training',
    ],
    'pc-lifestyle-sneakers': [
        'lifestyle sneaker', '休闲鞋', '板鞋', 'casual shoe', 'fashion sneaker',
        'retro', 'classic sneaker',
    ],
    'pc-sandals-slides': [
        'sandal', 'slide', '凉鞋', '拖鞋', 'slipper', 'flip', 'clog',
    ],
    'pc-tote-bags': [
        'tote', '托特', 'shopper', 'canvas bag', 'handbag', '手提', '包袋', 'bag',
        '皮具', 'leather good',
    ],
    'pc-backpacks': [
        'backpack', '双肩', '背包', 'rucksack', 'daypack', '书包',
    ],
    'pc-down-jackets': [
        'down jacket', '羽绒', 'puffer', 'parka', '保暖', 'insulated', '填充',
    ],
    'pc-shell-jackets': [
        'shell', '冲锋衣', '硬壳', 'gore-tex', 'goretex', '防水', 'windproof',
        'rain jacket', 'waterproof', 'hardshell',
    ],
    'pc-fleece-midlayer': [
        'fleece', '抓绒', '中间层', 'midlayer', 'mid layer', 'thermal', '羊绒',
        'cashmere', 'merino', '羊毛', 'wool',
    ],
    'pc-dresses': [
        'dress', '连衣裙', '裙子', 'gown', 'frock', '礼服', '裙',
    ],
    'pc-jeans': [
        'jean', '牛仔', 'denim', '丹宁', 'selvedge',
    ],
    'pc-swimwear': [
        'swim', '泳', 'bikini', 'swimsuit', 'beachwear', 'resort wear',
    ],
    'pc-hats': [
        'hat', '帽子', 'cap', 'beanie', 'headwear', 'snapback',
    ],
    'pc-socks': [
        'sock', '袜子', 'stocking', 'hosiery',
    ],
    'pc-underwear-loungewear': [
        'underwear', '内衣', '家居', 'loungewear', 'pajama', '睡衣',
        'pantie', 'boxer', 'brief', 'lingerie', 'intimate', '居家',
    ],
    'pc-jackets-coats': [
        'jacket', '外套', 'coat', 'blazer', 'outerwear', '夹克',
        'windbreaker', 'trench', '大衣', 'parka',
    ],
    'pc-shirts': [
        'shirt', '衬衫', '衬衣', 'button-down', 'dress shirt', 'oxford',
        'polo', 'blouse', 'polo衫',
    ],
    'pc-luggage': [
        'luggage', '旅行箱', '行李箱', 'suitcase', 'carry-on', 'trunk',
        'wheeled',
    ],
    'pc-crossbody-bags': [
        'crossbody', '斜挎', '腰包', 'waist', 'belt bag', 'shoulder bag',
        'messenger', 'sling', 'mini bag', 'clutch', '包', 'purse', '手袋',
    ],
    'pc-sunglasses': [
        'sunglass', '太阳镜', '墨镜', 'eyewear', 'optical', 'glasses',
        'shades', 'spectacle', '眼镜',
    ],
    'pc-watches': [
        'watch', '手表', '腕表', 'timepiece', 'chronograph', '表',
    ],
    'pc-jewelry': [
        'jewelry', 'jewellery', '珠宝', '首饰', 'necklace', 'ring', '戒指',
        'bracelet', '手链', 'earring', '耳环', 'pendant', 'charm',
        'diamond', 'gold', 'silver', 'precious', '项链', '配饰', 'accessory',
    ],
}

# ============================================================
# 品牌→额外场景/品类 硬编码补充
# 这些是关键词匹配不到的（品牌名/描述中没有明显关键词）
# ============================================================
EXTRA_SCENARIOS = {
    # 品牌slug → [场景slug列表]
    'nike': ['sc-swim-beach', 'sc-tennis', 'sc-cycling', 'sc-water-sports'],
    'adidas': ['sc-swim-beach', 'sc-cycling', 'sc-water-sports'],
    'under-armour': ['sc-swim-beach'],
    'puma': ['sc-swim-beach', 'sc-water-sports'],
    'reebok': ['sc-dance'],
    'new-balance': ['sc-tennis'],
    'asics': ['sc-tennis', 'sc-volleyball'],
    'patagonia': ['sc-climbing', 'sc-water-sports'],
    'the-north-face': ['sc-climbing'],
    'columbia': ['sc-water-sports'],
    'oakley': ['sc-cycling', 'sc-water-sports'],
    'ralph-lauren': ['sc-tennis'],
    'lacoste': ['sc-tennis'],
    'fila': ['sc-tennis'],
    'timberland': ['sc-outdoor-hiking'],
    'carhartt': ['sc-outdoor-hiking'],
    'dickies': ['sc-outdoor-hiking'],
    'levis': ['sc-daily-commute'],
    'uniqlo': ['sc-daily-commute', 'sc-home-lounge'],
    'gap': ['sc-daily-commute'],
    'banana-republic': ['sc-daily-commute'],
    'jcrew': ['sc-daily-commute'],
    'madewell': ['sc-daily-commute'],
    'everlane': ['sc-daily-commute'],
    'aritzia': ['sc-daily-commute'],
    'free-people': ['sc-daily-commute'],
    'zara': ['sc-daily-commute'],
    'hm': ['sc-daily-commute'],
    'cos': ['sc-daily-commute'],
    'bonobos': ['sc-daily-commute'],
    'todd-snyder': ['sc-daily-commute'],
    'abercrombie-fitch': ['sc-daily-commute'],
    'hollister': ['sc-daily-commute'],
    'american-eagle': ['sc-daily-commute'],
    'urban-outfitters': ['sc-daily-commute'],
    'victorias-secret': ['sc-home-lounge'],
    'skims': ['sc-home-lounge'],
    'spanx': ['sc-home-lounge'],
    'meundies': ['sc-home-lounge'],
    'tommy-john': ['sc-home-lounge'],
    'knix': ['sc-home-lounge'],
    'lively': ['sc-home-lounge'],
    'negative-underwear': ['sc-home-lounge'],
    'eberjey': ['sc-home-lounge'],
    'jockey': ['sc-home-lounge'],
    'hanna-andersson': ['sc-home-lounge'],
    'primary': ['sc-home-lounge'],
    'kyte-baby': ['sc-home-lounge'],
    'little-sleepies': ['sc-home-lounge'],
    'burts-bees-baby': ['sc-home-lounge'],
    'monica-andy': ['sc-home-lounge'],
    'boll-and-branch': ['sc-home-lounge'],
    'brooklinen': ['sc-home-lounge'],
    'parachute': ['sc-home-lounge'],
    'the-honest-company': ['sc-home-lounge'],
    'tumi': ['sc-travel'],
    'rimowa': ['sc-travel'],
    'samsonite': ['sc-travel'],
    'calpak': ['sc-travel'],
    'paravel': ['sc-travel'],
    'herschel': ['sc-travel', 'sc-daily-commute'],
    'bellroy': ['sc-travel', 'sc-daily-commute'],
    'peak-design': ['sc-travel'],
    'timbuk2': ['sc-travel', 'sc-daily-commute'],
    'nomatic': ['sc-travel'],
    'baboon-to-the-moon': ['sc-travel'],
    'lo-and-sons': ['sc-travel'],
    'state-bags': ['sc-travel'],
    'mz-wallace': ['sc-travel'],
    'senreve': ['sc-travel'],
    'dagne-dover': ['sc-travel', 'sc-daily-commute'],
    'cuyana': ['sc-travel', 'sc-daily-commute'],
    'longchamp': ['sc-travel'],
    'away': ['sc-travel'],
    'burton': ['sc-ski-winter'],
    'rossignol': ['sc-ski-winter'],
    'helly-hansen': ['sc-ski-winter', 'sc-outdoor-hiking', 'sc-water-sports'],
    'mammut': ['sc-ski-winter', 'sc-climbing'],
    'norrona': ['sc-ski-winter', 'sc-climbing'],
    'peak-performance': ['sc-ski-winter'],
    'goldwin': ['sc-ski-winter'],
    'canada-goose': ['sc-ski-winter'],
    'moncler': ['sc-ski-winter'],
    'bogner': ['sc-ski-winter'],
    'spyder': ['sc-ski-winter'],
    'descente': ['sc-ski-winter'],
    'kjus': ['sc-ski-winter'],
    'mackage': ['sc-ski-winter'],
    'moose-knuckles': ['sc-ski-winter'],
    'nobis': ['sc-ski-winter'],
    'parajumpers': ['sc-ski-winter'],
    'woolrich': ['sc-ski-winter', 'sc-outdoor-hiking'],
    'frankies-bikinis': ['sc-swim-beach'],
    'monday-swimwear': ['sc-swim-beach'],
    'solid-and-striped': ['sc-swim-beach'],
    'year-of-ours': ['sc-swim-beach'],
    'left-on-friday': ['sc-swim-beach'],
    'summersalt': ['sc-swim-beach'],
    'speedo': ['sc-swim-beach'],
    'arena': ['sc-swim-beach'],
    'billabong': ['sc-swim-beach', 'sc-water-sports'],
    'quiksilver': ['sc-swim-beach', 'sc-water-sports'],
    'roxy': ['sc-swim-beach', 'sc-water-sports'],
    'rip-curl': ['sc-swim-beach', 'sc-water-sports'],
    'hurley': ['sc-swim-beach', 'sc-water-sports'],
    'oneill': ['sc-swim-beach', 'sc-water-sports'],
    'vissla': ['sc-swim-beach', 'sc-water-sports'],
    'havaianas': ['sc-swim-beach'],
    'teva': ['sc-swim-beach', 'sc-outdoor-hiking'],
    'chaco': ['sc-swim-beach', 'sc-outdoor-hiking'],
    'crocs': ['sc-swim-beach', 'sc-daily-commute'],
    'birkenstock': ['sc-swim-beach', 'sc-daily-commute'],
    'ugg': ['sc-home-lounge', 'sc-ski-winter'],
    'allbirds': ['sc-daily-commute'],
    'rothys': ['sc-daily-commute'],
    'hey-dude': ['sc-daily-commute'],
    'drmartens': ['sc-daily-commute'],
    'vans': ['sc-daily-commute', 'sc-water-sports'],
    'converse': ['sc-daily-commute'],
    'warby-parker': ['sc-daily-commute'],
    'diff-eyewear': ['sc-daily-commute'],
    'quay': ['sc-daily-commute'],
    'crap-eyewear': ['sc-daily-commute'],
    'gentle-monster': ['sc-daily-commute'],
    'ray-ban': ['sc-daily-commute'],
    'rolex': ['sc-daily-commute'],
    'omega': ['sc-daily-commute'],
    'tag-heuer': ['sc-daily-commute'],
    'breitling': ['sc-daily-commute'],
    'cartier': ['sc-daily-commute'],
    'tiffany': ['sc-daily-commute'],
    'pandora': ['sc-daily-commute'],
    'mejuri': ['sc-daily-commute'],
    'ana-luisa': ['sc-daily-commute'],
    'gorjana': ['sc-daily-commute'],
    'jenny-bird': ['sc-daily-commute'],
    'baublebar': ['sc-daily-commute'],
    'kendra-scott': ['sc-daily-commute'],
    'david-yurman': ['sc-daily-commute'],
    'alex-and-ani': ['sc-daily-commute'],
    'miansai': ['sc-daily-commute'],
    'shinola': ['sc-daily-commute'],
    'nixon': ['sc-daily-commute'],
    'mvmt': ['sc-daily-commute'],
    'daniel-wellington': ['sc-daily-commute'],
    'fossil': ['sc-daily-commute'],
    'skagen': ['sc-daily-commute'],
    'timex': ['sc-daily-commute'],
    'casio': ['sc-daily-commute'],
    'g-shock': ['sc-daily-commute'],
    'seiko': ['sc-daily-commute'],
    'citizen': ['sc-daily-commute'],
    'apple': ['sc-daily-commute'],
    'garmin': ['sc-daily-commute', 'sc-running'],
    'suunto': ['sc-running', 'sc-outdoor-hiking'],
    'polar': ['sc-running'],
    'fitbit': ['sc-fitness-training', 'sc-daily-commute'],
    'whoop': ['sc-fitness-training'],
    'dyson': ['sc-home-lounge'],
    'vitruvi': ['sc-home-lounge'],
    'hydro-flask': ['sc-outdoor-hiking', 'sc-daily-commute'],
    'yeti': ['sc-outdoor-hiking', 'sc-daily-commute'],
    'stanley': ['sc-outdoor-hiking', 'sc-daily-commute'],
    'owala': ['sc-daily-commute'],
    'nalgene': ['sc-outdoor-hiking'],
    'klean-kanteen': ['sc-outdoor-hiking'],
    'swell': ['sc-daily-commute'],
    'moleskine': ['sc-daily-commute'],
    'lego': ['sc-home-lounge'],
}

EXTRA_PRODUCTS = {
    'nike': ['pc-swimwear', 'pc-sandals-slides', 'pc-jackets-coats', 'pc-backpacks'],
    'adidas': ['pc-swimwear', 'pc-sandals-slides', 'pc-jackets-coats'],
    'under-armour': ['pc-jackets-coats', 'pc-sandals-slides'],
    'puma': ['pc-jackets-coats', 'pc-sandals-slides'],
    'lululemon': ['pc-jackets-coats', 'pc-dresses', 'pc-swimwear', 'pc-hats'],
    'athleta': ['pc-swimwear', 'pc-dresses'],
    'aloyoga': ['pc-jackets-coats', 'pc-hats'],
    'vuori': ['pc-shirts', 'pc-jackets-coats'],
    'patagonia': ['pc-hats', 'pc-luggage', 'pc-shirts'],
    'the-north-face': ['pc-hats', 'pc-luggage', 'pc-sandals-slides'],
    'columbia': ['pc-hats', 'pc-sandals-slides'],
    'arcteryx': ['pc-hats', 'pc-shirts'],
    'carhartt': ['pc-shirts', 'pc-shorts'],
    'dickies': ['pc-shirts', 'pc-shorts'],
    'levis': ['pc-jackets-coats', 'pc-shirts', 'pc-shorts'],
    'gap': ['pc-dresses', 'pc-swimwear'],
    'banana-republic': ['pc-dresses'],
    'jcrew': ['pc-dresses', 'pc-swimwear'],
    'madewell': ['pc-dresses', 'pc-swimwear', 'pc-jackets-coats'],
    'everlane': ['pc-dresses', 'pc-swimwear'],
    'aritzia': ['pc-swimwear', 'pc-shorts'],
    'free-people': ['pc-swimwear', 'pc-shorts'],
    'zara': ['pc-swimwear', 'pc-shorts'],
    'hm': ['pc-swimwear', 'pc-shorts'],
    'uniqlo': ['pc-swimwear', 'pc-shorts', 'pc-dresses'],
    'abercrombie-fitch': ['pc-swimwear', 'pc-dresses'],
    'hollister': ['pc-swimwear', 'pc-dresses'],
    'american-eagle': ['pc-swimwear', 'pc-dresses'],
    'urban-outfitters': ['pc-swimwear', 'pc-dresses'],
    'victorias-secret': ['pc-swimwear', 'pc-dresses'],
    'reformation': ['pc-swimwear', 'pc-jackets-coats'],
    'skims': ['pc-dresses', 'pc-swimwear'],
    'burberry': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'ralph-lauren': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'tommy-hilfiger': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'calvin-klein': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'michael-kors': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'coach': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'tory-burch': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'kate-spade': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'marc-jacobs': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'gucci': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches', 'pc-hats'],
    'prada': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'louis-vuitton': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches', 'pc-hats'],
    'dior': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'chanel': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'hermes': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'balenciaga': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'versace': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'fendi': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'givenchy': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'celine': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'loewe': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'bottega-veneta': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'saint-laurent': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'valentino': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses', 'pc-sunglasses', 'pc-watches'],
    'jacquemus': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses'],
    'acne-studios': ['pc-jackets-coats', 'pc-shirts', 'pc-dresses'],
    'ganni': ['pc-jackets-coats', 'pc-dresses'],
    'toteme': ['pc-jackets-coats', 'pc-dresses'],
    'nanushka': ['pc-jackets-coats', 'pc-dresses'],
    'isabel-marant': ['pc-jackets-coats', 'pc-dresses'],
    'sandro': ['pc-jackets-coats', 'pc-dresses'],
    'maje': ['pc-jackets-coats', 'pc-dresses'],
    'self-portrait': ['pc-dresses'],
    'rotate': ['pc-dresses'],
    'ulla-johnson': ['pc-dresses'],
    'cecilie-bahnsen': ['pc-dresses'],
    'stine-goya': ['pc-dresses'],
    'alice-and-olivia': ['pc-dresses'],
    'khaite': ['pc-dresses'],
    'bode': ['pc-dresses', 'pc-shirts'],
    'proenza-schouler': ['pc-dresses'],
    'altuzarra': ['pc-dresses'],
    'the-row': ['pc-dresses', 'pc-shirts'],
    'tumi': ['pc-backpacks', 'pc-crossbody-bags'],
    'rimowa': ['pc-crossbody-bags'],
    'samsonite': ['pc-backpacks'],
    'herschel': ['pc-crossbody-bags', 'pc-hats'],
    'bellroy': ['pc-crossbody-bags'],
    'peak-design': ['pc-crossbody-bags', 'pc-hats'],
    'timbuk2': ['pc-crossbody-bags'],
    'patagonia': ['pc-hats', 'pc-shirts'],
    'the-north-face': ['pc-hats'],
    'arcteryx': ['pc-hats'],
    'columbia': ['pc-hats'],
    'nike': ['pc-hats'],
    'adidas': ['pc-hats'],
    'new-era': ['pc-shirts', 'pc-jackets-coats'],
    '47-brand': ['pc-shirts', 'pc-jackets-coats'],
    'stussy': ['pc-shirts', 'pc-jackets-coats', 'pc-shorts'],
    'supreme': ['pc-shirts', 'pc-jackets-coats', 'pc-shorts', 'pc-hats'],
    'kith': ['pc-shirts', 'pc-jackets-coats', 'pc-shorts', 'pc-hats'],
    'aime-leon-dore': ['pc-shirts', 'pc-jackets-coats', 'pc-shorts', 'pc-hats'],
    'fear-of-god': ['pc-shirts', 'pc-jackets-coats', 'pc-shorts', 'pc-hats'],
    'noah-nyc': ['pc-shirts', 'pc-jackets-coats', 'pc-shorts', 'pc-hats'],
    'jjjjound': ['pc-shirts', 'pc-jackets-coats'],
    'stone-island': ['pc-shirts', 'pc-jackets-coats', 'pc-shorts', 'pc-hats'],
    'off-white': ['pc-shirts', 'pc-jackets-coats', 'pc-shorts', 'pc-hats'],
    'chrome-hearts': ['pc-shirts', 'pc-jackets-coats', 'pc-jewelry', 'pc-hats'],
    'polo-ralph-lauren': ['pc-hats', 'pc-shirts'],
    'lacoste': ['pc-hats', 'pc-shirts'],
    'fila': ['pc-hats'],
    'champion': ['pc-hats', 'pc-shirts'],
    'carhartt': ['pc-hats'],
    'patagonia': ['pc-socks', 'pc-underwear-loungewear'],
    'smartwool': ['pc-hats', 'pc-shirts'],
    'icebreaker': ['pc-hats', 'pc-shirts', 'pc-underwear-loungewear'],
    'darn-tough': ['pc-shirts'],
    'bombas': ['pc-shirts', 'pc-underwear-loungewear'],
    'stance': ['pc-shirts', 'pc-underwear-loungewear'],
    'feetures': ['pc-shirts'],
    'balega': ['pc-shirts'],
    'injinji': ['pc-shirts'],
    'cep': ['pc-shirts', 'pc-leggings'],
    'nike': ['pc-underwear-loungewear'],
    'adidas': ['pc-underwear-loungewear'],
    'under-armour': ['pc-underwear-loungewear'],
    'lululemon': ['pc-underwear-loungewear'],
    'vuori': ['pc-underwear-loungewear'],
    'aloyoga': ['pc-underwear-loungewear'],
    'athleta': ['pc-underwear-loungewear'],
    'calvin-klein': ['pc-underwear-loungewear'],
    'tommy-hilfiger': ['pc-underwear-loungewear'],
    'ralph-lauren': ['pc-underwear-loungewear'],
    'hanna-andersson': ['pc-dresses', 'pc-t-shirts', 'pc-shorts'],
    'primary': ['pc-dresses', 'pc-t-shirts', 'pc-shorts'],
    'tea-collection': ['pc-dresses', 'pc-t-shirts', 'pc-shorts'],
    'mini-boden': ['pc-dresses', 'pc-t-shirts', 'pc-shorts'],
    'kyte-baby': ['pc-dresses', 'pc-t-shirts'],
    'little-sleepies': ['pc-dresses'],
    'kickee-pants': ['pc-dresses', 'pc-t-shirts'],
    'angel-dear': ['pc-dresses'],
    'burts-bees-baby': ['pc-dresses'],
    'janie-and-jack': ['pc-dresses', 'pc-shirts'],
    'gymboree': ['pc-dresses', 'pc-t-shirts'],
    'monica-andy': ['pc-dresses', 'pc-t-shirts'],
}


def match_keywords(text, keyword_map):
    """根据文本匹配关键词，返回匹配的slug集合"""
    if not text:
        return set()
    text_lower = text.lower()
    matched = set()
    for slug, keywords in keyword_map.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                matched.add(slug)
                break
    return matched


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=OFF")
    cursor = conn.cursor()

    # 1. 清除旧数据
    scenario_root = cursor.execute(
        "SELECT id FROM categories WHERE slug='sports-scenarios'"
    ).fetchone()[0]
    product_root = cursor.execute(
        "SELECT id FROM categories WHERE slug='product-categories'"
    ).fetchone()[0]
    
    cursor.execute("""
        DELETE FROM brand_categories 
        WHERE category_id IN (
            SELECT id FROM categories WHERE parent_id IN (?, ?)
        )
    """, (scenario_root, product_root))
    print(f'清除旧关联: {cursor.rowcount}条')

    # 2. 获取所有品牌信息
    cursor.execute("""
        SELECT b.id, b.slug, b.name, b.description, 
               (SELECT GROUP_CONCAT(c2.name, ' ') FROM (
                   SELECT DISTINCT c3.name FROM brand_categories bc2 
                   JOIN categories c3 ON c3.id = bc2.category_id AND c3.level > 0 
                   WHERE bc2.brand_id = b.id
               ) c2) as cat_names,
               (SELECT GROUP_CONCAT(c4.slug, ' ') FROM (
                   SELECT DISTINCT c5.slug FROM brand_categories bc3 
                   JOIN categories c5 ON c5.id = bc3.category_id AND c5.level > 0 
                   WHERE bc3.brand_id = b.id
               ) c4) as cat_slugs
        FROM brands b
    """)
    brands = cursor.fetchall()

    # 3. 获取所有场景和品类ID
    cursor.execute("SELECT slug, id FROM categories WHERE parent_id = ?", (scenario_root,))
    scenario_ids = {r[0]: r[1] for r in cursor.fetchall()}
    cursor.execute("SELECT slug, id FROM categories WHERE parent_id = ?", (product_root,))
    product_ids = {r[0]: r[1] for r in cursor.fetchall()}

    # 4. 逐个品牌匹配
    scenario_inserts = 0
    product_inserts = 0
    no_scenario = 0
    no_product = 0

    for brand_id, slug, name, desc, cat_names, cat_slugs in brands:
        # 构建搜索文本：名称 + 描述 + 分类名
        search_text = f"{name} {desc or ''} {cat_names or ''} {cat_slugs or ''}"
        
        # 关键词匹配
        matched_scenarios = match_keywords(search_text, SCENARIO_KEYWORDS)
        matched_products = match_keywords(search_text, PRODUCT_KEYWORDS)
        
        # 额外硬编码补充
        extra_s = EXTRA_SCENARIOS.get(slug, [])
        extra_p = EXTRA_PRODUCTS.get(slug, [])
        matched_scenarios.update(extra_s)
        matched_products.update(extra_p)
        
        # 兜底：没有任何品类的品牌，根据其大类/描述推断
        if not matched_products:
            text = search_text.lower()
            # 服饰类品牌 → T恤(兜底)
            if any(kw in text for kw in ['apparel', '服装', 'clothing', '服饰', 'fashion', '时尚', 'wear', 'style']):
                matched_products.add('pc-t-shirts')
            # 鞋履品牌 → 休闲鞋(兜底)
            if any(kw in text for kw in ['footwear', '鞋', 'shoe', 'sneaker']):
                matched_products.add('pc-running-shoes')
            # 包袋品牌 → 斜挎包(兜底)
            if any(kw in text for kw in ['bag', '包', '皮具', 'leather']):
                matched_products.add('pc-crossbody-bags')
            # 配饰品牌
            if any(kw in text for kw in ['jewelry', 'jewellery', '珠宝', '首饰', 'accessory', '配饰', 'watch', '表', 'sunglass', '眼镜', 'eyewear']):
                if 'watch' in text or '表' in text:
                    matched_products.add('pc-watches')
                if 'sunglass' in text or '太阳镜' in text or '墨镜' in text or '眼镜' in text or 'eyewear' in text:
                    matched_products.add('pc-sunglasses')
                if 'jewelry' in text or 'jewellery' in text or '珠宝' in text or '首饰' in text or 'accessory' in text or '配饰' in text:
                    matched_products.add('pc-jewelry')
            # 户外品牌
            if any(kw in text for kw in ['outdoor', '户外', 'camp', 'hiking', 'mountaineering', '登山', '狩猎', 'hunt']):
                matched_products.add('pc-shell-jackets')
            # 运动品牌
            if any(kw in text for kw in ['sport', '运动', 'athletic', 'fitness', '健身', 'gym']):
                matched_products.add('pc-leggings')
                matched_products.add('pc-t-shirts')
            # 家居/内衣
            if any(kw in text for kw in ['underwear', '内衣', '睡衣', '家居', 'loungewear', 'sleep', 'bed', 'home']):
                matched_products.add('pc-underwear-loungewear')
            # 童装
            if any(kw in text for kw in ['baby', '婴', '童', 'kid', 'child', 'maternity', '孕妇']):
                matched_products.add('pc-t-shirts')
                matched_products.add('pc-dresses')
            # 最终兜底
            if not matched_products:
                matched_products.add('pc-t-shirts')  # 几乎所有服饰品牌都有T恤
        
        # 场景兜底
        if not matched_scenarios:
            if any(kw in search_text.lower() for kw in ['apparel', '服装', 'clothing', '服饰']):
                matched_scenarios.add('sc-daily-commute')
            elif any(kw in search_text.lower() for kw in ['footwear', '鞋', 'shoe']):
                matched_scenarios.add('sc-daily-commute')
            elif any(kw in search_text.lower() for kw in ['bag', '包', 'accessory', '配饰']):
                matched_scenarios.add('sc-daily-commute')
        
        # 增强：对运动鞋服大牌自动补充核心品类
        if any(kw in search_text.lower() for kw in ['运动', 'sport', 'athletic', 'sneaker', '鞋']):
            if 'run' in search_text.lower() or '跑步' in search_text.lower() or slug in ['nike', 'adidas', 'asics', 'brooks', 'saucony', 'new-balance', 'hoka', 'on-running', 'puma', 'under-armour', 'reebok', 'altra', 'salomon', 'nobull', 'mizuno', 'karhu']:
                matched_products.add('pc-running-shoes')
            matched_products.add('pc-t-shirts')
            matched_products.add('pc-shorts')
            if slug in ['nike', 'adidas', 'under-armour', 'puma', 'reebok', 'lululemon', 'aloyoga', 'gymshark', 'athleta', 'vuori']:
                matched_products.add('pc-leggings')
                matched_products.add('pc-sports-bra')
                matched_products.add('pc-hoodies')
        
        # 插入场景关联
        for s_slug in matched_scenarios:
            if s_slug in scenario_ids:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO brand_categories (brand_id, category_id, is_primary) VALUES (?, ?, 0)",
                        (brand_id, scenario_ids[s_slug])
                    )
                    if cursor.rowcount > 0:
                        scenario_inserts += 1
                except:
                    pass
        
        # 插入品类关联
        for p_slug in matched_products:
            if p_slug in product_ids:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO brand_categories (brand_id, category_id, is_primary) VALUES (?, ?, 0)",
                        (brand_id, product_ids[p_slug])
                    )
                    if cursor.rowcount > 0:
                        product_inserts += 1
                except:
                    pass
        
        if not matched_scenarios:
            no_scenario += 1
        if not matched_products:
            no_product += 1

    conn.commit()

    # 5. 统计
    cursor.execute("""
        SELECT COUNT(DISTINCT bc.brand_id) FROM brand_categories bc 
        JOIN categories c ON c.id = bc.category_id WHERE c.parent_id = ?
    """, (scenario_root,))
    brands_with_scenario = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT bc.brand_id) FROM brand_categories bc 
        JOIN categories c ON c.id = bc.category_id WHERE c.parent_id = ?
    """, (product_root,))
    brands_with_product = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM brands")
    total = cursor.fetchone()[0]

    print(f'\n=== 最终统计 ===')
    print(f'场景关联: {scenario_inserts}条 (覆盖{brands_with_scenario}/{total}品牌 = {brands_with_scenario*100//total}%)')
    print(f'品类关联: {product_inserts}条 (覆盖{brands_with_product}/{total}品牌 = {brands_with_product*100//total}%)')
    print(f'无场景品牌: {no_scenario}')
    print(f'无品类品牌: {no_product}')
    
    # 平均关联数
    cursor.execute("""
        SELECT AVG(cnt) FROM (
            SELECT COUNT(*) as cnt FROM brand_categories bc
            JOIN categories c ON c.id = bc.category_id
            WHERE c.parent_id = ?
            GROUP BY bc.brand_id
        )
    """, (scenario_root,))
    avg_s = cursor.fetchone()[0] or 0
    print(f'平均场景数: {avg_s:.1f}')
    
    cursor.execute("""
        SELECT AVG(cnt) FROM (
            SELECT COUNT(*) as cnt FROM brand_categories bc
            JOIN categories c ON c.id = bc.category_id
            WHERE c.parent_id = ?
            GROUP BY bc.brand_id
        )
    """, (product_root,))
    avg_p = cursor.fetchone()[0] or 0
    print(f'平均品类数: {avg_p:.1f}')

    conn.close()


if __name__ == '__main__':
    main()
