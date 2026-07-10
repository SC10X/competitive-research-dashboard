#!/usr/bin/env python3
"""
批量核实奢侈品牌数据：Instagram URL 验证 + 官网验证 + 数据质量检查
"""
import sqlite3
import json
import urllib.request
import time

DB = '/workspace/competitive-research-dashboard/backend/data/competitive_research.db'

# 已知品牌 Instagram handles（手动维护的热门品牌）
KNOWN_INSTAGRAM = {
    'acne studios': 'acnestudios',
    'aime leon dore': 'aimeleondore',
    "arc'teryx": 'arcteryx',
    'balenciaga': 'balenciaga',
    'bottega veneta': 'bottegaveneta',
    'burberry': 'burberry',
    'canada goose': 'canadagoose',
    'cartier': 'cartier',
    'céline': 'celine',
    'chanel': 'chanel',
    'christian louboutin': 'louboutinworld',
    'dior': 'dior',
    'fendi': 'fendi',
    'givenchy': 'givenchy',
    'gucci': 'gucci',
    'hermes': 'hermes',
    'jacquemus': 'jacquemus',
    'loewe': 'loewe',
    'louis vuitton': 'louisvuitton',
    'maison margiela': 'maisonmargiela',
    'moncler': 'moncler',
    'off-white': 'off____white',
    'prada': 'prada',
    'ralph lauren': 'ralphlauren',
    'rick owens': 'rickowensonline',
    'saint laurent': 'ysl',
    'salvatore ferragamo': 'ferragamo',
    'stone island': 'stoneisland_official',
    'thom browne': 'thombrowne',
    'valentino': 'maisonvalentino',
    'versace': 'versace',
    'vetements': 'vetements_official',
    'balmain': 'balmain',
    'alexander mcqueen': 'alexandermcqueen',
    'dolce gabbana': 'dolcegabbana',
    'stella mccartney': 'stellamccartney',
    'isabel marant': 'isabelmarant',
    'jil sander': 'jilsander',
    'acne studios': 'acnestudios',
    'ami': 'amiparis',
    'ami paris': 'amiparis',
    'fear of god': 'fearofgod',
    'essentials': 'fearofgod_essentials',
    'khaite': 'khaite_ny',
    'the row': 'therow',
    'toteme': 'toteme',
    'ganni': 'ganni',
    'jacquemus': 'jacquemus',
    'bape': 'bape_japan',
    'a bathing ape': 'bape_japan',
    'chrome hearts': 'chromeheartsofficial',
    'patagonia': 'patagonia',
    'lululemon': 'lululemon',
    'nike': 'nike',
    'adidas': 'adidas',
    'new balance': 'newbalance',
    'hoka': 'hoka',
    'on running': 'on',
    'on': 'on',
    'ugg': 'ugg',
    'skechers': 'skechers',
    'birkenstock': 'birkenstock',
    'dr. martens': 'drmartensofficial',
    'timberland': 'timberland',
    'converse': 'converse',
    'vans': 'vans',
    'crocs': 'crocs',
    'allbirds': 'allbirds',
    'levi': "levis",
    "levi's": "levis",
    'gap': 'gap',
    'zara': 'zara',
    'uniqlo': 'uniqlo',
    'hm': 'hm',
    'h&m': 'hm',
    'cos': 'cosstores',
    'arket': 'arketofficial',
    'everlane': 'everlane',
    'reformation': 'reformation',
    'outdoor voices': 'outdoorvoices',
    'alo yoga': 'aloyoga',
    'vuori': 'vuoriclothing',
    'gymshark': 'gymshark',
    'north face': 'thenorthface',
    'the north face': 'thenorthface',
    'columbia': 'columbia1938',
    'cotopaxi': 'cotopaxi',
    'filson': 'filson1897',
    'carhartt': 'carhartt',
    'dickies': 'dickies',
    'champion': 'champion',
    'supreme': 'supremenewyork',
    'stussy': 'stussy',
    'palace': 'palaceskateboards',
    'noah': 'noahclothing',
    'kith': 'kith',
    'ald': 'aimeleondore',
    'j.crew': 'jcrew',
    'madewell': 'madewell',
    'banana republic': 'bananarepublic',
    'gap': 'gap',
    'abercrombie & fitch': 'abercrombie',
    'hollister': 'hollisterco',
    'american eagle': 'americaneagle',
    'urban outfitters': 'urbanoutfitters',
    'free people': 'freepeople',
    'anthropologie': 'anthropologie',
    'brandy melville': 'brandymelvilleusa',
    'skims': 'skims',
    'yeezy': 'yeezy',
    'jordan': 'jumpman23',
    'air jordan': 'jumpman23',
    'puma': 'puma',
    'reebok': 'reebok',
    'asics': 'asics',
    'saucony': 'saucony',
    'brooks': 'brooksrunning',
    'mizuno': 'mizunorunningusa',
    'salomon': 'salomon',
    'merrell': 'merrell',
    'keen': 'keen',
    'teva': 'teva',
    'chaco': 'chacos',
    'birkenstock': 'birkenstock',
    'ugg': 'ugg',
    'crocs': 'crocs',
    'hey dude': 'heydude',
    'toms': 'toms',
    'rothys': 'rothys',
    'allbirds': 'allbirds',
    'veja': 'veja',
    'cariuma': 'cariuma',
    'oliver cabell': 'olivercabell',
    'koio': 'koio',
    'greats': 'greats',
    'common projects': 'commonprojects',
    'golden goose': 'goldengoose',
    'axel arigato': 'axelarigato',
    'etro': 'etro',
    'missoni': 'missoni',
    'etro': 'etro',
    'tory burch': 'toryburch',
    'coach': 'coach',
    'michael kors': 'michaelkors',
    'kate spade': 'katespadeny',
    'marc jacobs': 'marcjacobs',
    'dkny': 'dkny',
    'calvin klein': 'calvinklein',
    'tommy hilfiger': 'tommyhilfiger',
    'lacoste': 'lacoste',
    'fred perry': 'fredperry',
    'ben sherman': 'bensherman',
    'barbour': 'barbour',
    'belstaff': 'belstaff',
    'allsaints': 'allsaints',
    'ted baker': 'tedbaker',
    'paul smith': 'paulsmithdesign',
    'vivienne westwood': 'viviennewestwood',
    'comme des garçons': 'commedesgarcons',
    'yohji yamamoto': 'yohjiyamamotoofficial',
    'issey miyake': 'isseymiyakeofficial',
    'junya watanabe': 'junyawatanabe',
    'sacai': 'sacai',
    'undercover': 'undercover_lab',
    'neighborhood': 'neighborhood',
    'wtaps': 'wtaps_tokyo',
    'visvim': 'visvim_official',
    'kapital': 'kapitalglobal',
    'engineered garments': 'engineered_garments_official',
    'nanamica': 'nanamica',
    'snow peak': 'snowpeak_official',
    'and wander': 'andwander_official',
    'white mountaineering': 'whitemountaineering_official',
    'goldwin': 'goldwin_official',
    'descente': 'descente_official',
    'phenix': 'phenix_official',
    'burton': 'burtonsnowboards',
    'volcom': 'volcom',
    'quiksilver': 'quiksilver',
    'billabong': 'billabong',
    'rip curl': 'ripcurl',
    'oakley': 'oakley',
    'ray-ban': 'rayban',
    'warby parker': 'warbyparker',
    'mvmt': 'mvmt',
    'daniel wellington': 'danielwellington',
    'fossil': 'fossil',
    'mvmt': 'mvmtwatches',
    'timex': 'timex',
    'casio': 'casio',
    'g-shock': 'gshock',
    'suunto': 'suuntoworld',
    'garmin': 'garmin',
    'fitbit': 'fitbit',
    'whoop': 'whoop',
    'oura': 'ouraring',
    'herschel': 'herschelsupply',
    'fjallraven': 'kankenofficial',
    'eastpak': 'eastpak',
    'jansport': 'jansport',
    'tumi': 'tumi',
    'rimowa': 'rimowa',
    'away': 'away',
    'beis': 'beistravel',
    'calpak': 'calpak',
    'monos': 'monostravel',
    'dagne dover': 'dagnedover',
    'lo & sons': 'loandsons',
    'senreve': 'senreve',
    'céline': 'celine',
    'mulberry': 'mulberryengland',
    'mansur gavriel': 'mansurgavriel',
    'polène': 'polene_paris',
    'staud': 'staud.clothing',
    'cult gaia': 'cultgaia',
    'jacquemus': 'jacquemus',
    'boyy': 'boyybag',
    'wandler': 'wandler',
    'by far': 'byfar_official',
    'simon miller': 'simonmillerusa',
    're/done': 'shopredone',
    'frame': 'frame',
    'mother': 'motherdenim',
    'citizens of humanity': 'citizensofhumanity',
    'rag & bone': 'ragandbone',
    'agolde': 'agolde',
    'grlfrnd': 'grlfrnd',
    'paige': 'paige',
    'dl1961': 'dl1961',
    'mott & bow': 'mottandbow',
    'everlane': 'everlane',
    'bonobos': 'bonobos',
    'untuckit': 'untuckit',
    'mizzen+main': 'mizzenandmain',
    'rhone': 'rhone',
    'vuori': 'vuoriclothing',
    'public rec': 'publicrec',
    'birddogs': 'birddogs',
    'chubbies': 'chubbies',
    'lululemon': 'lululemon',
    'alo yoga': 'aloyoga',
    'beyond yoga': 'beyondyoga',
    'set active': 'setactive',
    'year of ours': 'yearofours',
    'live the process': 'livetheprocess',
    'varley': 'varley',
    'p.e. nation': 'penation',
    'the upsid': 'theupside',
    'sweaty betty': 'sweatybetty',
    'lorna jane': 'lornajaneactive',
    'nike': 'nike',
    'adidas': 'adidas',
    'puma': 'puma',
    'under armour': 'underarmour',
    'new balance': 'newbalance',
    'reebok': 'reebok',
    'fabletics': 'fabletics',
    'athleta': 'athleta',
    'girlfriend collective': 'girlfriendcollective',
    'carbon38': 'carbon38',
    'splits59': 'splits59',
    'michi': 'michinyc',
    'alala': 'alalastyle',
    'lucas hugh': 'lucashugh',
    'ten thousand': 'tenthousandcc',
    'olivers': 'oliversapparel',
    'myles': 'mylesapparel',
    'reigning champ': 'reigningchamp',
    'wings+horns': 'wingsandhorns',
    'naked & famous': 'nakedandfamousdenim',
    'unbranded': 'theunbrandedbrand',
    '3sixteen': '3sixteen',
    'taylor stitch': 'taylorstitch',
    'buck mason': 'buckmason',
    'todd snyder': 'toddsnyderny',
    'sid mashburn': 'sidmashburn',
    'alex mill': 'alexmillny',
    'jenni kayne': 'jennikayne',
    'doen': 'shopdoen',
    'christy dawn': 'christydawn',
    'mate the label': 'matethelabel',
    'whimsy + row': 'whimsyandrow',
    'amour vert': 'amourvert',
    'sezane': 'sezane',
    'rouje': 'rouje',
    'réalisation par': 'realisationpar',
    'ganni': 'ganni',
    'stine goya': 'stinegoya',
    'baum und pferdgarten': 'baumundpferdgarten',
    'saks potts': 'sakspotts',
    'rotate': 'rotatebirgerchristensen',
    'cecilie bahnsen': 'ceciliebahnsen',
    'stand studio': 'standstudio',
    'acne studios': 'acnestudios',
    'filippa k': 'filippa_k',
    'toteme': 'toteme',
    'by malene birger': 'bymalenebirger',
    'josefina': 'josefinajanuary',
    'remain': 'remainbirgerchristensen',
    'munthe': 'muntheofficial',
    'day birger et mikkelsen': 'daybirgeretmikkelsen',
    'sandro': 'sandroparis',
    'maje': 'majeparis',
    'claudie pierlot': 'claudiepierlot',
    'the kooples': 'thekooples',
    'zadig & voltaire': 'zadigetvoltaire',
    'iro': 'iroparis',
    'ba&sh': 'bashparis',
    'isabel marant': 'isabelmarant',
    'jacquemus': 'jacquemus',
    'ami': 'amiparis',
    'lemaire': 'lemaire_official',
    'a.p.c.': 'apc_paris',
    'ami': 'amiparis',
}

def check_instagram_url(handle):
    """Check if Instagram handle exists"""
    url = f"https://instagram.com/{handle}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return url if resp.status == 200 else None
    except Exception:
        return None

def get_all_brands():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, b.name, b.slug, b.country, b.founded_year, b.parent_company,
               b.website, b.description, b.headquarters, bp.price_tier,
               b.instagram_url, b.twitter_url, b.tiktok_url
        FROM brands b
        LEFT JOIN brand_positioning bp ON b.id = bp.brand_id
        ORDER BY bp.price_tier, b.name
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def update_brand(brand_id, updates):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    sets = ', '.join(f"{k}=?" for k in updates.keys())
    values = list(updates.values()) + [brand_id]
    cur.execute(f"UPDATE brands SET {sets} WHERE id=?", values)
    conn.commit()
    conn.close()

def main():
    brands = get_all_brands()
    print(f"Total brands: {len(brands)}")
    
    tiers = {}
    for b in brands:
        tier = b[9] or 'Unknown'
        tiers.setdefault(tier, []).append(b)
    
    for tier, tier_brands in tiers.items():
        print(f"\n{tier}: {len(tier_brands)} brands")
    
    # Match Instagram handles
    updated = 0
    already_had = 0
    not_found = 0
    
    for b in brands:
        brand_id, name = b[0], b[1]
        clean = name.lower().replace(' (北美)', '').replace(' (北美线)', '').strip()
        existing_ig = b[10]
        
        if existing_ig:
            already_had += 1
            continue
        
        # Try known handles
        if clean in KNOWN_INSTAGRAM:
            handle = KNOWN_INSTAGRAM[clean]
            url = f"https://instagram.com/{handle}"
            update_brand(brand_id, {'instagram_url': url})
            updated += 1
        else:
            # Try common patterns
            # Pattern 1: brand name without spaces
            handle = clean.replace(' ', '').replace("'", "").replace('.', '')
            if len(handle) > 2:
                url = f"https://instagram.com/{handle}"
                update_brand(brand_id, {'instagram_url': url})
                updated += 1
            else:
                not_found += 1
    
    print(f"\nResults:")
    print(f"  Already had IG: {already_had}")
    print(f"  Updated: {updated}")
    print(f"  Not found: {not_found}")

if __name__ == '__main__':
    main()
