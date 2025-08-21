import os
from dotenv import load_dotenv

# Pobranie klucza API z pliku .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class CFG:
    """Konfiguracja aplikacji"""

    # Konfiguracja OpenAI
    api_key = OPENAI_API_KEY
    model = "gpt-4o-mini"

    # Cennik napojów
    DRINK_PRICES = {
        "espresso": {"S": 8, "M": 10, "L": 12},
        "americano": {"S": 10, "M": 12, "L": 14},
        "cappuccino": {"S": 12, "M": 14, "L": 16},
        "latte": {"S": 13, "M": 15, "L": 17},
        "flat white": {"S": 13, "M": 15, "L": 17},
        "czarna": {"S": 8, "M": 10, "L": 12},
        "zielona": {"S": 8, "M": 10, "L": 12},
        "owocowa": {"S": 9, "M": 11, "L": 13},
        "earl grey": {"S": 9, "M": 11, "L": 13},
        "frappuccino": {"S": 15, "M": 17, "L": 19},
        "smoothie": {"S": 16, "M": 18, "L": 20},
        "lemoniada": {"S": 12, "M": 14, "L": 16},
    }

    # Dodatki i ich ceny
    ADDON_PRICES = {
        "mleko": 1,
        "śmietanka": 1,
        "cukier": 0,
        "syrop waniliowy": 2,
        "syrop karmelowy": 2,
        "syrop czekoladowy": 2,
    }

    # Dostępne napoje
    AVAILABLE_DRINKS = {
        "kawa": ["espresso", "americano", "cappuccino", "latte", "flat white"],
        "herbata": ["czarna", "zielona", "owocowa", "earl grey"],
        "napoje zimne": ["frappuccino", "smoothie", "lemoniada"],
    }

    # Rozmiary
    SIZES = ["S", "M", "L"]
    SIZE_NAMES = {"S": "mały", "M": "średni", "L": "duży"}

    # Zamienniki
    SUBSTITUTIONS = {
        "mleko migdałowe": "mleko",
        "mleko sojowe": "mleko",
        "mleko kokosowe": "mleko",
        "słodzik": "cukier",
    }


def get_menu():
    """Pokaż dostępne napoje"""
    menu = "**Dostępne napoje:**\n"

    for category, drinks in CFG.AVAILABLE_DRINKS.items():
        if category == "kawa":
            menu += f"- ☕ Kawa: {', '.join(drinks)}\n"
        elif category == "herbata":
            menu += f"- 🍵 Herbata: {', '.join(drinks)}\n"
        elif category == "napoje zimne":
            menu += f"- 🥤 Napoje zimne: {', '.join(drinks)}\n"

    menu += f"\n**Rozmiary:** {', '.join([f'{size} ({CFG.SIZE_NAMES[size]})' for size in CFG.SIZES])}\n"
    menu += f"\n**Dodatki:** {', '.join(CFG.ADDON_PRICES.keys())}\n"
    menu += f"\n**Zamienniki:** {', '.join(CFG.SUBSTITUTIONS.keys())}"

    return menu
