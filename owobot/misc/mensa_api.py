import requests
from datetime import datetime

# These could be Enums but I'm not a java addict!
# Do I get headpats?
MENSA_LIST = {
    "GARCHING": {
        "display_name": "Garching",
        "graphite": "ap.ap*-?mg*.ssid.*",
        "id": "mensa-garching",
        "capacity": 1500,
        "thumbnail": "https://cdn.discordapp.com/attachments/829494984348270602/1076448239382966323/mensa.png",
    },
    "STUCAFE_GARCHING": {
        "display_name": "StuCafé Garching",
        "id": "stucafe-garching",
        "thumbnail": "https://cdn.discordapp.com/attachments/829494984348270602/1076917552481054740/mensa_garching_web1.jpg",
    },
    "ARCISSTR": {
        "display_name": "Arcisstraße",
        "graphite": "ap.ap*-?bn*.ssid.*",
        "id": "mensa-arcisstr",
        "capacity": 1000,
        "thumbnail": "https://cdn.discordapp.com/attachments/829494984348270602/1076580173060784188/csm_062016_mensa_arcissstr_cr_silvie_tillard-4_dd2d349ec2.webp",
    },
    "LEOPOLDSTR": {
        "display_name": "Leopoldstraße",
        "graphite": "ap.ap*-?lm*.ssid.*",
        "id": "mensa-leopoldstr",
        "capacity": 1000,
        "thumbnail": "https://cdn.discordapp.com/attachments/829494984348270602/1076448600210550794/mensa_leopoldstr.png",
    },
    "MARTINSRIED": {
        "display_name": "Martinsried",
        "graphite": "ap.ap*-?ij*.ssid.*",
        "id": "mensa-martinsried",
        "capacity": 500,
        "thumbnail": "https://cdn.discordapp.com/attachments/829494984348270602/1076448600525111296/mensa_martinsried.png",
    },
}

LABELS = {
    "GLUTEN": "🌿",
    "WHEAT": "GlW",
    "RYE": "GlR",
    "BARLEY": "GlG",
    "OAT": "GlH",
    "SPELT": "GlD",
    "HYBRIDS": "GlHy",
    "SHELLFISH": "🦀",
    "CHICKEN_EGGS": "🥚",
    "FISH": "🐟",
    "PEANUTS": "🥜",
    "SOY": "So",
    "MILK": "🥛",
    "LACTOSE": "La",
    "ALMONDS": "ScM",
    "HAZELNUTS": "🌰",
    "WALNUTS": "ScW",
    "CASHEWS": "ScC",
    "PECAN": "ScP",
    "PISTACHIOES": "ScP",
    "MACADAMIA": "ScMa",
    "CELERY": "Sl",
    "MUSTARD": "Sf",
    "SESAME": "Se",
    "SULPHURS": "🔻",
    "SULFITES": "🔺",
    "LUPIN": "Lu",
    "MOLLUSCS": "🐙",
    "SHELL_FRUITS": "🥥",
    "BAVARIA": "GQB",
    "MSC": "🎣",
    "DYESTUFF": "🎨",
    "PRESERVATIVES": "🥫",
    "ANTIOXIDANTS": "⚗",
    "FLAVOR_ENHANCER": "🔬",
    "WAXED": "🐝",
    "PHOSPATES": "🔷",
    "SWEETENERS": "🍬",
    "PHENYLALANINE": "💊",
    "COCOA_CONTAINING_GREASE": "🍫",
    "GELATIN": "🍮",
    "ALCOHOL": "🍷",
    "PORK": "🐖",
    "BEEF": "🐄",
    "VEAL": "🐂",
    "WILD_MEAT": "🐗",
    "LAMB": "🐑",
    "GARLIC": "🧄",
    "POULTRY": "🐔",
    "CEREAL": "🌾",
    "MEAT": "🍖",
    "VEGAN": "🥦",
    "VEGETARIAN": "🥕",
}

LABEL_MAP = {
    "🌿": "Gluten-containing cereals",
    "GlW": "Wheat",
    "GlR": "Rye",
    "GlG": "Barley",
    "GlH": "Oat",
    "GlD": "Spelt",
    "GlHy": "Hybrid strains",
    "🦀": "Shellfish",
    "🥚": "Egg",
    "🐟": "Fish",
    "🥜": "Peanut",
    "So": "Soy",
    "🥛": "Milk",
    "La": "Lactose",
    "ScM": "Almonds",
    "🌰": "Hazelnuts",
    "ScW": "Walnuts",
    "ScC": "Cashews",
    "ScP": "Pistachios",
    "ScMa": "Macadamias",
    "Sl": "Celery",
    "Sf": "Mustard",
    "Se": "Sesame",
    "🔻": "Sulphurs",
    "🔺": "Sulfites",
    "Lu": "Lupin",
    "🐙": "Molluscs",
    "🥥": "Shell fruits",
    "GQB": "Certified quality bavaria",
    "🎣": "Marine stewardship council",
    "🎨": "Dyestuff",
    "🥫": "Preservatives",
    "⚗": "Antioxidants",
    "🔬": "Flavor enhancer",
    "🐝": "Waxed",
    "🔷": "Phosphates",
    "🍬": "Sweeteners",
    "💊": "With a source of phenylalanine",
    "🍫": "Cocoa-containing grease",
    "🍮": "Gelatin",
    "🍷": "Alcohol",
    "🐖": "Pork",
    "🐄": "Beef",
    "🐂": "Veal",
    "🐗": "Wild meat",
    "🐑": "Lamb",
    "🧄": "Garlic",
    "🐔": "Poultry",
    "🌾": "Cereal",
    "🍖": "Meat",
    "🥦": "Vegan",
    "🥕": "Vegetarian",
}

TYPES = {
    "Fleisch": "🥩",
    "Fisch": "🐟",
    "Pasta": "🍝",
    "Wok": "🥘",
    "Studitopf": "🍲",
    "Süßspeise": "🍩",
    "Beilagen": "🍴",
    "Grill": "🍗",
    "Vegetarisch/fleischlos": "🥦",
}
    
FOOD_TO_EMOJI = {"reis": "🍚", "saft": "🧃", "kartoffel": "🥔", "gemüse": "🥗"}

def get_dish_emoji(dish):
    '''
    Return an appropriate emoji for a given dish name
    '''
    for food, emoji in FOOD_TO_EMOJI.items():
        if food in dish.get("name", "").lower():
            return emoji

    return TYPES.get(dish.get("dish_type"), "🍽")


async def mensa_from_string(name):
    """
    Returns mensa static data from a given name
    """
    name = name.lower()
    for mensa in MENSA_LIST.values():
        display_name = mensa.get("display_name", "").lower()

        skip = False
        for i, c in enumerate(name):
            if i > len(display_name) or c != display_name[i]:
                skip = True
                break

        if skip:
            continue
        return mensa


async def get_occupancy(mensa):
    """
    Given a key from MENSA_LIST, return the current
    occupation to a certain cafeteria.
    """
    if not mensa.get("graphite"):
        return 
    
    page = await get_stats(mensa)

    # Maps and regroups access points from different entries into a single dict
    # Thanks mensa.liste.party!
    aps = list(
        map(
            lambda x: (
                x["target"].split(".")[1],
                x["datapoints"][-1][0] or x["datapoints"][-2][0] or 0,
            ),
            page,
        )
    )
    stats = dict()
    for ap, current in aps:
        if ap in stats:
            stats[ap] += current
        else:
            stats[ap] = current

    return sum(stats.values())


async def get_stats(mensa):
    """
    Use graphite to query data from access points within the given mensa, in the last hour.
    """
    return requests.get(
        f"http://graphite-kom.srv.lrz.de/render/?from=-1h&target={mensa['graphite']}&format=json"
    ).json()


async def get_menu(id, year, week):
    """
    Get the daily menu from a given mensa-id
    """
    return requests.get(f"https://tum-dev.github.io/eat-api/{id}/{year}/{week}.json")


async def process_dishes(dishes):
    for dish in dishes:
        dish_name = dish["name"]
        dish_short = None
        if "mit" in dish_name:
            tbl = dish_name.split(" mit ")
            dish_short = tbl[0]

            dish["name_extension"] = "mit " + "".join(tbl[1:])
        dish["display_name"] = dish_short if dish_short else dish_name
        dish["emoji"] = get_dish_emoji(dish)
    return dishes


cache = {}
CACHE_MAX_SIZE = len(MENSA_LIST)

async def get_dishes_for_date(mensa, date):
    """
    Returns a post-processed list of dishes for a given day

    Uses a trivial cache which clears itself when full (CACHE_MAX_SIZE is the amount of cafeterias!)
    """
    global cache
    if len(cache) >= CACHE_MAX_SIZE:
        cache = {}

    key = (mensa.get("id"), date.strftime("%Y-%m-%d"))

    if not cache.get(key):
        cache[key] = await process_dishes(await get_raw_dishes_for_date(mensa, date))
    return cache[key]


async def get_raw_dishes_for_date(mensa, date):
    """
    Internal use: requests mensa data for a given day.
    """
    year, week = date.year, date.strftime("%U")
    data = await get_menu(mensa["id"], year, week)
    data = data.json()

    for day in data["days"]:
        if day["date"] == date.strftime("%Y-%m-%d"):
            return day["dishes"]


async def get_dishes_for_today(mensa):
    '''
    Returns the current dishes for today
    '''
    return await get_dishes_for_date(mensa, datetime.today())


def dish_to_string(dish):
    '''
    Simple to_string method which shows dish type, name, prices and labels.
    '''
    return f'{dish["dish_type"]} {dish["name"]} €{dish["prices"]["students"]["price_per_unit"]} / {dish["prices"]["students"]["unit"]} {" ".join(map(lambda x : LABELS.get(x), dish["labels"]))}'
