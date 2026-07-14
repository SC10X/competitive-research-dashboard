"""
新增两个分类维度并关联品牌：
1. 运动场景 (sports-scenarios): 健身、跑步、瑜伽、游泳等
2. 细化品类 (product-categories): Legging、T恤、跑步鞋、托特包等
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'competitive_research.db')

# ============================================================
# 运动场景子分类 (18个)
# ============================================================
SCENARIOS = [
    ('健身/训练', 'sc-fitness-training', 1),
    ('跑步', 'sc-running', 2),
    ('瑜伽/普拉提', 'sc-yoga-pilates', 3),
    ('游泳/海滩', 'sc-swim-beach', 4),
    ('高尔夫', 'sc-golf', 5),
    ('网球', 'sc-tennis', 6),
    ('户外/徒步', 'sc-outdoor-hiking', 7),
    ('滑雪/冬季运动', 'sc-ski-winter', 8),
    ('篮球', 'sc-basketball', 9),
    ('足球', 'sc-soccer', 10),
    ('骑行', 'sc-cycling', 11),
    ('综训/CrossFit', 'sc-crossfit', 12),
    ('日常通勤', 'sc-daily-commute', 13),
    ('旅行', 'sc-travel', 14),
    ('居家/休闲', 'sc-home-lounge', 15),
    ('舞蹈', 'sc-dance', 16),
    ('攀岩', 'sc-climbing', 17),
    ('水上运动', 'sc-water-sports', 18),
]

# ============================================================
# 细化品类子分类 (28个)
# ============================================================
PRODUCT_CATEGORIES = [
    ('Legging/紧身裤', 'pc-leggings', 1),
    ('运动内衣', 'pc-sports-bra', 2),
    ('T恤', 'pc-t-shirts', 3),
    ('卫衣/Hoodie', 'pc-hoodies', 4),
    ('运动短裤', 'pc-shorts', 5),
    ('跑步鞋', 'pc-running-shoes', 6),
    ('篮球鞋', 'pc-basketball-shoes', 7),
    ('训练鞋', 'pc-training-shoes', 8),
    ('休闲鞋/板鞋', 'pc-lifestyle-sneakers', 9),
    ('凉鞋/拖鞋', 'pc-sandals-slides', 10),
    ('托特包', 'pc-tote-bags', 11),
    ('双肩包', 'pc-backpacks', 12),
    ('羽绒服', 'pc-down-jackets', 13),
    ('冲锋衣/硬壳', 'pc-shell-jackets', 14),
    ('抓绒/中间层', 'pc-fleece-midlayer', 15),
    ('连衣裙', 'pc-dresses', 16),
    ('牛仔裤', 'pc-jeans', 17),
    ('泳衣', 'pc-swimwear', 18),
    ('帽子', 'pc-hats', 19),
    ('袜子', 'pc-socks', 20),
    ('内衣/家居服', 'pc-underwear-loungewear', 21),
    ('夹克/外套', 'pc-jackets-coats', 22),
    ('衬衫', 'pc-shirts', 23),
    ('旅行箱', 'pc-luggage', 24),
    ('斜挎包/腰包', 'pc-crossbody-bags', 25),
    ('太阳镜', 'pc-sunglasses', 26),
    ('手表', 'pc-watches', 27),
    ('珠宝首饰', 'pc-jewelry', 28),
]

# ============================================================
# 品牌→场景 关联映射 (基于品牌定位/产品线/描述关键词)
# ============================================================
BRAND_SCENARIOS = {
    # 健身/训练
    'sc-fitness-training': [
        'nike', 'adidas', 'under-armour', 'reebok', 'puma', 'gymshark', 'aloyoga', 'vuori',
        'lululemon', 'fabletics', 'athleta', 'bombshell-sportswear', 'nvgtn', 'doyoueven',
        'ryderwear', 'aybl', 'muscle-nation', 'carbon38', 'setactive', 'nobull',
        'born-primitive', 'ten-thousand', 'myles-apparel', 'rhone', 'mack-weldon',
        'bylt-basics', 'csb-crop-shop-boutique', 'lndr', 'pe-nation', 'varley',
        'sweaty-betty', 'tala', '2xu', 'cep', 'compressport', 'craft-sportswear',
        'odlo', 'skins', 'x-bionic', 'salming',
        'under-armour-na', 'gymshark-na', 'fabletics-na', 'reebok-na',
        'lululemon-na', 'aloyoga-na', 'vuori-na', 'athleta-gap',
    ],
    # 跑步
    'sc-running': [
        'nike', 'adidas', 'asics', 'brooks', 'saucony', 'new-balance', 'hoka', 'on-running',
        'altra', 'topo-athletic', 'salomon', 'puma', 'under-armour', 'nobull',
        'tracksmith', 'satisfy-running', 'bandit-running', 'rabbit', 'janji',
        '2xu', 'cep', 'compressport', 'nike-na', 'adidas-na', 'asics-na',
        'new-balance-na', 'hoka-na', 'on-running-na', 'brooks-running',
        'moving-comfort-brooks', 'salomon-na', 'saucony-na',
    ],
    # 瑜伽/普拉提
    'sc-yoga-pilates': [
        'lululemon', 'aloyoga', 'beyond-yoga', 'athleta', 'girlfriend-collective',
        'outdoor-voices', 'fabletics', 'setactive', 'carbon38', 'sweaty-betty',
        'crz-yoga', 'bombshell-sportswear', 'varley', 'lndr', 'pe-nation',
        'mate-the-label', 'tala', 'aybl', 'nvgtn',
        'lululemon-na', 'aloyoga-na', 'beyond-yoga-na', 'athleta-gap',
    ],
    # 游泳/海滩
    'sc-swim-beach': [
        'frankies-bikinis', 'monday-swimwear', 'solid-and-striped', 'year-of-ours',
        'left-on-friday', 'summersalt', 'marysia', 'mikoh',
        'speedo', 'arena', 'billabong', 'quiksilver', 'roxy', 'rip-curl',
        'oakley', 'teva', 'chaco', 'crocs', 'havaianas',
    ],
    # 高尔夫
    'sc-golf': [
        'nike', 'adidas', 'puma', 'under-armour', 'peter-millar',
        'travis-mathew', 'greyson-clothiers', 'johnnie-o', 'gfore',
        'titleist', 'footjoy', 'callaway', 'taylormade', 'ping',
        'lacoste', 'ralph-lauren', 'polo-ralph-lauren',
        'travis-mathew-na', 'peter-millar-na',
    ],
    # 网球
    'sc-tennis': [
        'nike', 'adidas', 'wilson', 'head', 'babolat', 'asics',
        'lacoste', 'fila', 'prince', 'yonex',
        'wilson-na', 'babolat-na', 'head-na',
    ],
    # 户外/徒步
    'sc-outdoor-hiking': [
        'patagonia', 'the-north-face', 'arcteryx', 'columbia', 'marmot',
        'mountain-hardwear', 'outdoor-research', 'black-diamond', 'cotopaxi',
        'fjallraven', 'helly-hansen', 'mammut', 'norrona', 'rab',
        'mountain-equipment', 'sherpa-adventure-gear', 'haglofs', 'deuter',
        'osprey', 'gregory', 'keen', 'merrell', 'salomon', 'danner',
        'teva', 'chaco', 'lowa', 'scarpa', 'la-sportiva', 'altra',
        'topo-athletic', 'hoka', 'prana', 'kuhl', 'royal-robbins', 'stio',
        'smartwool', 'icebreaker', 'darn-tough', 'pendleton', 'woolrich',
        'gramicci', 'patagonia-na', 'the-north-face-na', 'arcteryx-na',
        'columbia-na', 'salomon-na', 'keen-na', 'merrell-na',
        'icebreaker-vf', 'black-diamond-na', 'osprey-na', 'gregory-na',
    ],
    # 滑雪/冬季运动
    'sc-ski-winter': [
        'the-north-face', 'patagonia', 'arcteryx', 'burton', 'helly-hansen',
        'rossignol', 'salomon', 'spyder', 'mammut', 'norrona', 'peak-performance',
        'goldwin', 'descente', 'kjus', 'bogner', 'moncler', 'canada-goose',
        'oakley', 'smith', 'goggle', 'dragon',
        'the-north-face-na', 'burton-na', 'rossignol-na',
    ],
    # 篮球
    'sc-basketball': [
        'nike', 'jordan-brand', 'adidas', 'puma', 'under-armour',
        'reebok', 'converse', 'anta', 'li-ning', 'peak',
        'nike-na', 'jordan-brand-nike', 'adidas-na', 'converse-nike',
        'spalding', 'spalding-na', 'wilson', 'wilson-na',
        'lakers',
    ],
    # 足球
    'sc-soccer': [
        'nike', 'adidas', 'puma', 'new-balance', 'umbro', 'diadora',
        'kappa', 'mizuno', 'hummel', 'macron',
        'adidas-na', 'puma-na', 'kappa-na', 'diadora-na', 'mizuno-na',
    ],
    # 骑行
    'sc-cycling': [
        'rapha', 'pas-normal-studios', 'pearl-izumi', 'maap', 'castelli',
        'assos', 'poc', 'giro', 'specialized', 'trek',
        'rapha-na', 'pearl-izumi-na',
    ],
    # 综训/CrossFit
    'sc-crossfit': [
        'nobull', 'reebok', 'nike', 'under-armour', 'born-primitive',
        'rogue', 'rvca', 'ten-thousand', 'myles-apparel',
    ],
    # 日常通勤
    'sc-daily-commute': [
        'lululemon', 'vuori', 'allbirds', 'rothys', 'everlane',
        'bonobos', 'ministry-of-supply', 'mizzen-main', 'outerknown',
        'faherty', 'taylor-stitch', 'marine-layer', 'buck-mason',
        'relwen', 'western-rise', 'flint-and-tinder', 'duer',
        'kit-and-ace', 'untuckit', 'todd-snyder', 'john-elliott',
        'aime-leon-dore', 'jjjjound', 'noah-nyc',
        'ag-jeans', 'paige', 'frame', 'mother-denim', 'rag-bone',
        'citizens-of-humanity', '7-for-all-mankind', 'hudson-jeans',
        'levis', 'madewell', 'jcrew', 'gap', 'banana-republic',
        'abercrombie-fitch', 'hollister', 'uniqlo', 'cos',
        'everlane-na', 'allbirds-na', 'bonobos-na',
    ],
    # 旅行
    'sc-travel': [
        'away', 'dagne-dover', 'calpak', 'paravel', 'tumi', 'rimowa',
        'samsonite', 'herschel', 'bellroy', 'peak-design', 'timbuk2',
        'nomatic', 'baboon-to-the-moon', 'lo-and-sons', 'state-bags',
        'mz-wallace', 'senreve', 'cuyana', 'longchamp',
        'tumi-na', 'rimowa-na', 'herschel-supply-co', 'away-travel',
        'patagonia', 'the-north-face', 'cotopaxi',
    ],
    # 居家/休闲
    'sc-home-lounge': [
        'skims', 'spanx', 'aritzia', 'free-people', 'urban-outfitters',
        'hanna-andersson', 'primary', 'tea-collection', 'mini-boden',
        'kyte-baby', 'little-sleepies', 'kickee-pants', 'angel-dear',
        'burts-bees-baby', 'janie-and-jack', 'gymboree',
        'monica-andy', 'boll-and-branch', 'brooklinen', 'parachute',
        'the-honest-company', 'meundies', 'tommy-john', 'eberjey',
        'negative-underwear', 'knix', 'jockey', 'victorias-secret',
        'skims-na', 'spanx-na', 'free-people-na',
    ],
    # 舞蹈
    'sc-dance': [
        'lululemon', 'athleta', 'beyond-yoga', 'capezio', 'bloch',
        'danskin', 'fabletics', 'sweaty-betty',
    ],
    # 攀岩
    'sc-climbing': [
        'patagonia', 'arcteryx', 'the-north-face', 'black-diamond',
        'prana', 'gramicci', 'la-sportiva', 'scarpa', 'mammut',
        'petzl', 'edelrid', 'topo-designs',
    ],
    # 水上运动
    'sc-water-sports': [
        'billabong', 'quiksilver', 'roxy', 'rip-curl', 'patagonia',
        'hurley', 'oneill', 'vissla', 'teva', 'chaco',
        'oakley', 'sperry', 'hey-dude', 'crocs', 'havaianas',
        'speedo', 'arena', 'tyr',
    ],
}

# ============================================================
# 品牌→细化品类 关联映射
# ============================================================
BRAND_PRODUCT_CATS = {
    'pc-leggings': [
        'lululemon', 'aloyoga', 'athleta', 'beyond-yoga', 'girlfriend-collective',
        'outdoor-voices', 'fabletics', 'gymshark', 'nvgtn', 'bombshell-sportswear',
        'setactive', 'carbon38', 'sweaty-betty', 'varley', 'lndr',
        'crz-yoga', 'aybl', 'doyoueven', 'ryderwear', 'muscle-nation',
        'tala', 'pe-nation', 'mate-the-label',
        'nike', 'adidas', 'under-armour', 'puma', 'reebok',
    ],
    'pc-sports-bra': [
        'lululemon', 'athleta', 'aloyoga', 'beyond-yoga', 'girlfriend-collective',
        'outdoor-voices', 'sweaty-betty', 'fabletics', 'gymshark', 'nvgtn',
        'bombshell-sportswear', 'setactive', 'carbon38', 'varley',
        'nike', 'adidas', 'under-armour', 'puma', 'reebok', 'shock-absorber',
        'brooks', 'moving-comfort-brooks', 'panache', 'freya',
        'lively', 'knix', 'negative-underwear',
    ],
    'pc-t-shirts': [
        'nike', 'adidas', 'under-armour', 'lululemon', 'vuori', 'aloyoga',
        'everlane', 'madewell', 'jcrew', 'gap', 'banana-republic',
        'bonobos', 'ministry-of-supply', 'outerknown', 'faherty',
        'taylor-stitch', 'marine-layer', 'buck-mason', 'relwen',
        'flint-and-tinder', 'todd-snyder', 'untuckit',
        'abercrombie-fitch', 'hollister', 'uniqlo', 'cos',
        'patagonia', 'arcteryx', 'the-north-face', 'cotopaxi',
        'rhone', 'ten-thousand', 'myles-apparel', 'mack-weldon',
    ],
    'pc-hoodies': [
        'nike', 'adidas', 'lululemon', 'vuori', 'aloyoga', 'gymshark',
        'fabletics', 'champion', 'abercrombie-fitch', 'hollister',
        'everlane', 'madewell', 'jcrew', 'gap', 'banana-republic',
        'patagonia', 'arcteryx', 'the-north-face', 'cotopaxi',
        'aime-leon-dore', 'fear-of-god', 'essentials', 'kith',
        'stussy', 'supreme', 'noah-nyc', 'jjjjound',
        'outerknown', 'faherty', 'flint-and-tinder',
        'american-giant', 'campland', 'reigning-champ',
    ],
    'pc-shorts': [
        'nike', 'adidas', 'lululemon', 'vuori', 'aloyoga', 'gymshark',
        'fabletics', 'under-armour', 'athleta', 'beyond-yoga',
        'outdoor-voices', 'rhone', 'ten-thousand', 'myles-apparel',
        'birddogs', 'chubbies', 'bonobos', 'jcrew', 'madewell',
        'patagonia', 'columbia', 'the-north-face', 'prana', 'kuhl',
    ],
    'pc-running-shoes': [
        'nike', 'adidas', 'asics', 'brooks', 'saucony', 'new-balance',
        'hoka', 'on-running', 'altra', 'topo-athletic', 'salomon',
        'puma', 'under-armour', 'mizuno', 'nobull', 'karhu',
        'la-sportiva', 'scarpa',
    ],
    'pc-basketball-shoes': [
        'nike', 'jordan-brand', 'adidas', 'puma', 'under-armour',
        'reebok', 'converse', 'anta', 'li-ning', 'peak',
    ],
    'pc-training-shoes': [
        'nike', 'adidas', 'reebok', 'under-armour', 'puma', 'nobull',
        'new-balance', 'asics', 'inov-8',
    ],
    'pc-lifestyle-sneakers': [
        'nike', 'adidas', 'new-balance', 'vans', 'converse', 'puma',
        'reebok', 'asics', 'common-projects', 'greats', 'koio',
        'oliver-cabell', 'cariuma', 'veja', 'beckett-simonon',
        'thursday-boot', 'taft', 'koio', 'axel-arigato', 'eytys',
        'golden-goose', 'gucci', 'balenciaga', 'prada', 'dior',
        'louis-vuitton', 'alexander-mcqueen', 'saint-laurent',
        'skechers', 'crocs', 'hey-dude', 'allbirds', 'rothys',
    ],
    'pc-sandals-slides': [
        'birkenstock', 'teva', 'chaco', 'crocs', 'havaianas',
        'ugg', 'dansko', 'keen', 'merrell', 'oofos', 'drmartens',
        'birkenstock-1774', 'suicoke', 'yeezy',
    ],
    'pc-tote-bags': [
        'longchamp', 'cuyana', 'madewell', 'everlane', 'mz-wallace',
        'dagne-dover', 'lo-and-sons', 'state-bags', 'paravel',
        'baggu', 'llbean', 'lands-end', 'marc-jacobs',
        'tory-burch', 'coach', 'kate-spade', 'michael-kors',
        'goyard', 'louis-vuitton', 'hermes', 'chanel', 'dior',
        'faherty', 'marine-layer',
    ],
    'pc-backpacks': [
        'herschel', 'jansport', 'the-north-face', 'patagonia',
        'fjallraven', 'osprey', 'deuter', 'gregory', 'mountain-hardwear',
        'eastpak', 'timbuk2', 'topo-designs', 'cotopaxi',
        'peak-design', 'bellroy', 'nomatic', 'away', 'tumi',
        'herschel-supply-co', 'baboon-to-the-moon', 'duluth-pack',
    ],
    'pc-down-jackets': [
        'canada-goose', 'moncler', 'patagonia', 'the-north-face',
        'arcteryx', 'mountain-hardwear', 'fjallraven', 'mammut',
        'norrona', 'rab', 'helly-hansen', 'peak-performance',
        'united-by-blue', 'cotopaxi', 'eddie-bauer', 'llbean',
        'columbia', 'lands-end', 'woolrich', 'bogner',
    ],
    'pc-shell-jackets': [
        'arcteryx', 'patagonia', 'the-north-face', 'mountain-hardwear',
        'outdoor-research', 'mammut', 'norrona', 'rab', 'black-diamond',
        'helly-hansen', 'fjallraven', 'columbia', 'marmot',
        'haglofs', 'mountain-equipment', 'sherpa-adventure-gear',
        'stio', 'kuhl', 'cotopaxi', 'peak-performance',
        'goldwin', 'gramicci',
    ],
    'pc-fleece-midlayer': [
        'patagonia', 'the-north-face', 'arcteryx', 'columbia',
        'mountain-hardwear', 'cotopaxi', 'fjallraven', 'marmot',
        'llbean', 'eddie-bauer', 'lands-end', 'woolrich',
        'prana', 'kuhl', 'stio', 'outerknown', 'faherty',
    ],
    'pc-dresses': [
        'reformation', 'free-people', 'aritzia', 'everlane',
        'madewell', 'jcrew', 'hanna-andersson', 'zara',
        'alice-and-olivia', 'ulla-johnson', 'cecilie-bahnsen',
        'stine-goya', 'ganni', 'nanushka', 'toteme', 'the-row',
        'isabel-marant', 'sandro', 'maje', 'self-portrait', 'rotate',
        'altuzarra', 'proenza-schouler', 'khaite', 'bode',
        'victoria-beckham', 'jacquemus',
    ],
    'pc-jeans': [
        'levis', 'madewell', 'ag-jeans', 'paige', 'frame', 'mother-denim',
        'rag-bone', 'citizens-of-humanity', '7-for-all-mankind', 'hudson-jeans',
        'everlane', 'abercrombie-fitch', 'hollister', 'gap', 'banana-republic',
        'old-navy', 'jcrew', 'reformation', 'free-people', 'good-american',
        'levis-na', 'levi-strauss-co', 'ag-jeans-na',
    ],
    'pc-swimwear': [
        'frankies-bikinis', 'monday-swimwear', 'solid-and-striped',
        'year-of-ours', 'left-on-friday', 'summersalt',
        'speedo', 'arena', 'billabong', 'quiksilver', 'roxy', 'rip-curl',
        'marysia', 'mikoh', 'lspace', 'mikoh',
    ],
    'pc-hats': [
        'new-era', '47-brand', 'nike', 'adidas', 'patagonia',
        'the-north-face', 'carhartt', 'stussy', 'supreme',
        'kith', 'aime-leon-dore', 'noah-nyc',
    ],
    'pc-socks': [
        'bombas', 'stance', 'smartwool', 'darn-tough', 'balega',
        'feetures', 'nike', 'adidas', 'under-armour', 'puma',
        'lululemon', 'injinji', 'cep', 'gold-toe',
    ],
    'pc-underwear-loungewear': [
        'skims', 'spanx', 'victorias-secret', 'meundies', 'tommy-john',
        'knix', 'lively', 'negative-underwear', 'eberjey',
        'jockey', 'hanes', 'calvin-klein', 'pact', 'organic-basics',
        'lululemon', 'athleta', 'beyond-yoga', 'aritzia',
    ],
    'pc-jackets-coats': [
        'canada-goose', 'moncler', 'patagonia', 'the-north-face',
        'arcteryx', 'burberry', 'barbour', 'woolrich',
        'ralph-lauren', 'tommy-hilfiger', 'calvin-klein',
        'everlane', 'aritzia', 'zara', 'cos',
        'carhartt', 'dickies', 'levis', 'filson',
        'mackage', 'moose-knuckles', 'nobis', 'parajumpers',
    ],
    'pc-shirts': [
        'bonobos', 'ministry-of-supply', 'mizzen-main', 'untuckit',
        'jcrew', 'banana-republic', 'todd-snyder', 'taylor-stitch',
        'everlane', 'madewell', 'frank-and-eileen', 'eileen-fisher',
        'faherty', 'marine-layer', 'outerknown', 'buck-mason',
        'relwen', 'flint-and-tinder', 'western-rise',
        'ralph-lauren', 'tommy-hilfiger', 'calvin-klein', 'lacoste',
    ],
    'pc-luggage': [
        'away', 'tumi', 'rimowa', 'samsonite', 'calpak', 'paravel',
        'dagne-dover', 'baboon-to-the-moon', 'lo-and-sons',
        'mz-wallace', 'herschel', 'the-north-face', 'patagonia',
        'louis-vuitton', 'rimowa-na', 'tumi-na',
    ],
    'pc-crossbody-bags': [
        'lululemon', 'baggu', 'fjallraven', 'patagonia', 'cuyana',
        'madewell', 'everlane', 'herschel', 'topo-designs', 'cotopaxi',
        'senreve', 'tumi', 'louis-vuitton', 'gucci', 'prada',
        'chanel', 'hermes', 'loewe', 'bottega-veneta', 'celine',
        'dior', 'fendi', 'givenchy', 'saint-laurent', 'balenciaga',
        'coach', 'kate-spade', 'tory-burch', 'michael-kors',
        'longchamp', 'mansur-gavriel', 'staud', 'cult-gaia',
    ],
    'pc-sunglasses': [
        'ray-ban', 'oakley', 'warby-parker', 'diff-eyewear', 'quay',
        'crap-eyewear', 'maui-jim', 'persol', 'garrett-leight',
        'oliver-peoples', 'gentle-monster',
        'gucci', 'prada', 'dior', 'chanel', 'louis-vuitton',
        'tom-ford', 'celine', 'balenciaga',
    ],
    'pc-watches': [
        'rolex', 'omega', 'tag-heuer', 'breitling', 'cartier',
        'patek-philippe', 'audemars-piguet', 'iwc', 'panerai',
        'richard-mille', 'tudor', 'seiko', 'casio', 'g-shock',
        'timex', 'daniel-wellington', 'mvmt', 'nixon', 'shinola',
        'apple', 'garmin', 'fossil', 'skagen', 'miansai',
    ],
    'pc-jewelry': [
        'tiffany', 'cartier', 'bulgari', 'van-cleef-arpels',
        'harry-winston', 'david-yurman', 'alex-and-ani',
        'pandora', 'mejuri', 'ana-luisa', 'gorjana', 'jenny-bird',
        'baublebar', 'kendra-scott', 'catbird', 'missoma',
        'monica-vinader', 'apm-monaco', 'swarovski',
    ],
}


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=OFF")
    cursor = conn.cursor()

    # 清理旧数据（如果之前执行过）
    cursor.execute("DELETE FROM brand_categories WHERE category_id IN (SELECT id FROM categories WHERE level = 0)")
    cursor.execute("DELETE FROM categories WHERE level = 0 OR (parent_id IN (SELECT id FROM categories WHERE level = 0))")

    # 1. 创建两个维度顶级节点
    cursor.execute("INSERT INTO categories (name, slug, parent_id, level, sort_order) VALUES (?, ?, NULL, 0, ?)",
                   ('运动场景', 'sports-scenarios', 1))
    scenarios_root_id = cursor.lastrowid

    cursor.execute("INSERT INTO categories (name, slug, parent_id, level, sort_order) VALUES (?, ?, NULL, 0, ?)",
                   ('细化品类', 'product-categories', 2))
    products_root_id = cursor.lastrowid

    print(f'维度节点创建: 运动场景={scenarios_root_id}, 细化品类={products_root_id}')

    # 2. 插入运动场景子分类
    scenario_ids = {}
    for name, slug, sort in SCENARIOS:
        cursor.execute(
            "INSERT INTO categories (name, slug, parent_id, level, sort_order) VALUES (?, ?, ?, 1, ?)",
            (name, slug, scenarios_root_id, sort)
        )
        scenario_ids[slug] = cursor.lastrowid
    print(f'运动场景子分类: {len(scenario_ids)}个')

    # 3. 插入细化品类子分类
    product_cat_ids = {}
    for name, slug, sort in PRODUCT_CATEGORIES:
        cursor.execute(
            "INSERT INTO categories (name, slug, parent_id, level, sort_order) VALUES (?, ?, ?, 1, ?)",
            (name, slug, products_root_id, sort)
        )
        product_cat_ids[slug] = cursor.lastrowid
    print(f'细化品类子分类: {len(product_cat_ids)}个')

    # 4. 关联品牌到场景
    scenario_count = 0
    for scenario_slug, brand_slugs in BRAND_SCENARIOS.items():
        cat_id = scenario_ids.get(scenario_slug)
        if not cat_id:
            continue
        for brand_slug in brand_slugs:
            cursor.execute("SELECT id FROM brands WHERE slug = ?", (brand_slug,))
            brand = cursor.fetchone()
            if not brand:
                # 尝试模糊匹配
                cursor.execute("SELECT id FROM brands WHERE slug LIKE ?", (f'{brand_slug}%',))
                brand = cursor.fetchone()
            if brand:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO brand_categories (brand_id, category_id, is_primary) VALUES (?, ?, 0)",
                        (brand[0], cat_id)
                    )
                    if cursor.rowcount > 0:
                        scenario_count += 1
                except:
                    pass

    print(f'场景关联: {scenario_count}条')

    # 5. 关联品牌到细化品类
    product_count = 0
    for cat_slug, brand_slugs in BRAND_PRODUCT_CATS.items():
        cat_id = product_cat_ids.get(cat_slug)
        if not cat_id:
            continue
        for brand_slug in brand_slugs:
            cursor.execute("SELECT id FROM brands WHERE slug = ?", (brand_slug,))
            brand = cursor.fetchone()
            if not brand:
                cursor.execute("SELECT id FROM brands WHERE slug LIKE ?", (f'{brand_slug}%',))
                brand = cursor.fetchone()
            if brand:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO brand_categories (brand_id, category_id, is_primary) VALUES (?, ?, 0)",
                        (brand[0], cat_id)
                    )
                    if cursor.rowcount > 0:
                        product_count += 1
                except:
                    pass

    print(f'品类关联: {product_count}条')

    conn.commit()

    # 统计
    cursor.execute("SELECT COUNT(*) FROM brand_categories bc JOIN categories c ON c.id = bc.category_id WHERE c.parent_id = ?", (scenarios_root_id,))
    total_scenario_links = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM brand_categories bc JOIN categories c ON c.id = bc.category_id WHERE c.parent_id = ?", (products_root_id,))
    total_product_links = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT bc.brand_id) FROM brand_categories bc JOIN categories c ON c.id = bc.category_id WHERE c.parent_id = ?", (scenarios_root_id,))
    brands_with_scenario = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT bc.brand_id) FROM brand_categories bc JOIN categories c ON c.id = bc.category_id WHERE c.parent_id = ?", (products_root_id,))
    brands_with_product = cursor.fetchone()[0]

    print(f'\n=== 最终统计 ===')
    print(f'运动场景关联: {total_scenario_links}条 (覆盖{brands_with_scenario}个品牌)')
    print(f'细化品类关联: {total_product_links}条 (覆盖{brands_with_product}个品牌)')
    print(f'场景分类数: {len(SCENARIOS)}')
    print(f'品类分类数: {len(PRODUCT_CATEGORIES)}')

    conn.close()


if __name__ == '__main__':
    main()
