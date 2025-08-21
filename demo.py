#!/usr/bin/env python3
"""
Demo aplikacji Kawiarnia AI - pokazuje strukturę bez wymagania klucza API
"""

import sys
import os

# Dodaj katalog główny do ścieżki Pythona
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_menu, CFG


def demo_config():
    """Pokazuje konfigurację aplikacji"""
    print("☕ Kawiarnia AI First - Demo")
    print("=" * 50)

    print("\n📋 Menu kawiarni:")
    print(get_menu())

    print("\n💰 Cennik napojów:")
    for drink, sizes in CFG.DRINK_PRICES.items():
        print(
            f"  {drink.title()}: {', '.join([f'{size} ({price} zł)' for size, price in sizes.items()])}"
        )

    print("\n🔧 Dodatki i ceny:")
    for addon, price in CFG.ADDON_PRICES.items():
        print(f"  {addon}: {price} zł")

    print("\n🔄 Dostępne zamienniki:")
    for substitution, original in CFG.SUBSTITUTIONS.items():
        print(f"  {substitution} → {original}")


def demo_structure():
    """Pokazuje strukturę projektu"""
    print("\n📁 Struktura projektu:")
    print("elephant_coffe_assistant/")
    print("├── main.py              # Główny plik aplikacji")
    print("├── gui.py               # Interfejs graficzny Gradio")
    print("├── agent.py             # Logika agenta AI i węzły grafu")
    print("├── config.py            # Konfiguracja i menu kawiarni")
    print("├── tests.py             # Testy aplikacji")
    print("├── demo.py              # Ten plik demo")
    print("├── requirements.txt     # Zależności Python")
    print("├── README.md           # Dokumentacja")
    print("├── .env                # Plik z kluczem API (do utworzenia)")
    print("└── venv/               # Wirtualne środowisko Python")


def demo_usage():
    """Pokazuje instrukcje użycia"""
    print("\n🚀 Instrukcje uruchomienia:")
    print("1. Zainstaluj zależności: pip install -r requirements.txt")
    print("2. Utwórz plik .env z kluczem OPENAI_API_KEY")
    print("3. Uruchom aplikację: python main.py")
    print("4. Otwórz przeglądarkę: http://127.0.0.1:7860")

    print("\n🧪 Uruchomienie testów:")
    print("python tests.py")

    print("\n💡 Przykładowe interakcje:")
    print("- 'Chciałbym latte średnie'")
    print("- 'Dodaj syrop waniliowy'")
    print("- 'Dodaj napój do koszyka'")
    print("- 'Finalizuj zamówienie'")


def main():
    """Główna funkcja demo"""
    try:
        demo_config()
        demo_structure()
        demo_usage()

        print("\n" + "=" * 50)
        print("🎉 Demo zakończone pomyślnie!")
        print("📝 Aby uruchomić pełną aplikację, potrzebujesz klucza API OpenAI")
        print("🔑 Utwórz plik .env z zawartością: OPENAI_API_KEY=twój_klucz")

    except Exception as e:
        print(f"❌ Błąd podczas demo: {e}")


if __name__ == "__main__":
    main()
