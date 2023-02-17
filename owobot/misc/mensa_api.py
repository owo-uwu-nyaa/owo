import requests
from datetime import datetime

# These could be Enums but I'm not a java addict!
# Do I get heapats?
MENSA_LIST = {    
    "GARCHING" : {
        "display_name": "Garching",
        "graphite" : "ap.ap*-?mg*.ssid.*",
        "id" : "mensa-garching",
        "capacity": 1500
    },
    "ARCISSTR" : {
        "display_name": "Arcisstraße",
        "graphite" : "ap.ap*-?bn*.ssid.*",
        "id" : "mensa-arcisstr"
    },
    "LEOPOLDSTR" : {
        "display_name": "Leopoldstraße",
        "graphite" : "ap.ap*-?lm*.ssid.*",
        "id" : "mensa-leopoldstr"
    },
    "MARTINSRIED" : {
        "display_name": "Martinsried",
        "graphite" : "ap.ap*-?ij*.ssid.*",
        "id" : "mensa-martinsried"
    }
}

LABELS = {'GLUTEN': '🌿', 'WHEAT': 'GlW', 'RYE': 'GlR', 'BARLEY': 'GlG', 'OAT': 'GlH', 'SPELT': 'GlD', 'HYBRIDS': 'GlHy', 'SHELLFISH': '🦀', 'CHICKEN_EGGS': '🥚', 'FISH': '🐟', 'PEANUTS': '🥜', 'SOY': 'So', 'MILK': '🥛', 'LACTOSE': 'La', 'ALMONDS': 'ScM', 'HAZELNUTS': 
'🌰', 'WALNUTS': 'ScW', 'CASHEWS': 'ScC', 'PECAN': 'ScP', 'PISTACHIOES': 'ScP', 'MACADAMIA': 'ScMa', 'CELERY': 'Sl', 'MUSTARD': 'Sf', 'SESAME': 'Se', 'SULPHURS': '🔻', 'SULFITES': '🔺', 'LUPIN': 'Lu', 'MOLLUSCS': '🐙', 'SHELL_FRUITS': '🥥', 'BAVARIA': 'GQB', 'MSC': '🎣', 'DYESTUFF': '🎨', 'PRESERVATIVES': '🥫', 'ANTIOXIDANTS': '⚗', 'FLAVOR_ENHANCER': '🔬', 'WAXED': '🐝', 'PHOSPATES': '🔷', 'SWEETENERS': '🍬', 'PHENYLALANINE': '💊', 'COCOA_CONTAINING_GREASE': '🍫', 'GELATIN': '🍮', 'ALCOHOL': '🍷', 'PORK': '🐖', 'BEEF': '🐄', 'VEAL': '🐂', 'WILD_MEAT': '🐗', 'LAMB': '🐑', 'GARLIC': '🧄', 'POULTRY': '🐔', 'CEREAL':  '🌾', 'MEAT': '🍖', 'VEGAN': 
'🥦', 'VEGETARIAN': '🥕'}

TYPES = {
    "Fleisch" : "🥩",
    "Fisch" : "🐟",
    "Pasta" : "🍝",
    "Wok" : "🥘",
    "Studitopf" : "🍲",
    "Süßspeise" : "🍩",
    "Beilagen" : "🍴"
}

async def mensa_from_string(name):
    '''
        Returns mensa static data from a given name
    '''
    key = name.upper()
    # Optionally create a partial match checker (im lazy)
    if not key in MENSA_LIST.keys():
        return
    
    return MENSA_LIST.get(key)

async def get_occupancy(mensa):
    '''
    Given a key from MENSA_LIST, return the current
    occupation to a certain cafeteria.
    '''
    page = await get_stats(mensa)

    # Maps and regroups access points from different entries into a single dict
    # Thanks mensa.liste.party!
    aps = list(map(lambda x: (x['target'].split('.')[1], x['datapoints'][-1][0] or x['datapoints'][-2][0] or 0), page))
    stats = dict()
    for ap, current in aps:
        if ap in stats:
            stats[ap] += current
        else:
            stats[ap] = current

    return sum(stats.values())

async def get_stats(mensa):
    '''
    Use graphite to query data from access points within the given mensa, in the last hour.
    '''
    return requests.get(f"http://graphite-kom.srv.lrz.de/render/?from=-1h&target={mensa['graphite']}&format=json").json()

async def get_menu(id, year, week):
    '''
    Get the daily menu from a given mensa-id
    '''
    return requests.get(f"https://tum-dev.github.io/eat-api/{id}/{year}/{week}.json")

async def get_dishes_for_date(mensa, date):
    '''
    Returns a list of dishes (dicts) for a given day
    '''
    year, week = date.year, date.strftime("%U")
    data = await get_menu(mensa["id"], year, week)
    data=data.json()

    for day in data["days"]:
        if day["date"] == date.strftime("%Y-%m-%d"):
            return day["dishes"]

async def get_dishes_for_today(mensa):
    return await get_dishes_for_date(mensa, datetime.today())


def dish_to_string(dish):
    return f'{dish["dish_type"]} {dish["name"]} €{dish["prices"]["students"]["price_per_unit"]} / {dish["prices"]["students"]["unit"]} {" ".join(map(lambda x : LABELS.get(x), dish["labels"]))}'
