#!/usr/bin/env python3
"""
Testy dla aplikacji Kawiarnia AI
"""

import sys
import os

# Dodaj katalog główny do ścieżki Pythona
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import Agent


def run_tests():
    """Uruchamia wszystkie testy aplikacji"""
    print("🧪 Uruchamianie testów aplikacji Kawiarnia AI...")

    # Inicjalizacja agenta
    agent = Agent()

    # Test 1: Pusty koszyk
    print("\n📋 Test 1: Pusty koszyk")
    assert agent.get_cart_summary() == {
        "items": [],
        "total": 0.0,
        "item_count": 0,
    }
    print("✅ Pusty koszyk przeszedł test")

    # Test 2: Menu
    print("\n📋 Test 2: Menu")
    menu = agent.chat("Jakie mam napoje do wyboru?").lower()
    assert "espresso" in menu
    assert "americano" in menu
    assert "cappuccino" in menu
    assert "latte" in menu
    assert "flat white" in menu
    assert "czarna" in menu
    assert "zielona" in menu
    assert "owocowa" in menu
    assert "earl grey" in menu
    assert "frappuccino" in menu
    assert "smoothie" in menu
    assert "lemoniada" in menu
    print("✅ Menu przeszło test")

    # Test 3: Koszyk z jednym przedmiotem
    print("\n📋 Test 3: Koszyk z jednym przedmiotem")
    agent.chat("Dodaj do koszyka espresso, małe")
    assert agent.get_cart_summary() == {
        "items": [
            {
                "drink": "espresso",
                "size": "S",
                "customizations": [],
                "substitutions": [],
                "price": 8.0,
            }
        ],
        "total": 8.0,
        "item_count": 1,
    }
    print("✅ Koszyk z jednym przedmiotem przeszedł test")

    # Test 4: Koszyk z dwoma przedmiotami
    print("\n📋 Test 4: Koszyk z dwoma przedmiotami")
    agent.reset()
    agent.chat("Dodaj do koszyka latte, duże, bez dodatków")
    agent.chat("Dodaj do koszyka espresso, małe, z mlekiem")

    assert agent.get_cart_summary() == {
        "items": [
            {
                "drink": "latte",
                "size": "L",
                "customizations": [],
                "substitutions": [],
                "price": 17.0,
            },
            {
                "drink": "espresso",
                "size": "S",
                "customizations": ["mleko"],
                "substitutions": [],
                "price": 9.0,
            },
        ],
        "total": 26.0,
        "item_count": 2,
    }
    print("✅ Koszyk z dwoma przedmiotami przeszedł test")

    # Test 5: Przykładowy przepływ zamówienia
    print("\n📋 Test 5: Przykładowy przepływ zamówienia")
    agent.reset()
    agent.chat("Co mamy w menu?")
    agent.chat("Chce zamówić czarną herbatę.")
    agent.chat("Poproszę średnią.")
    agent.chat("Jakie dodatki mam do wyboru?")
    agent.chat("Proszę dodać cukier i syrop waniliowy.")
    agent.chat("OK, proszę dodać to do koszyka.")
    summary = agent.chat("Podsumuj zamówienie.")

    assert "🎉 Dziękuję za zamówienie! Oto podsumowanie:" in summary
    assert "czarna herbata M (cukier, syrop waniliowy, standardowe) - 12 zł" in summary
    assert "💰 Łączna kwota: 12.0 zł" in summary
    assert "Zamówienie zostanie przygotowane za kilka minut. Miłego dnia! ☕" in summary
    print("✅ Przykładowy przepływ przeszedł test")

    # Test 6: Metryki
    print("\n📋 Test 6: Metryki")
    agent.reset()  # Reset nie kasuje metryk - to jak przebieg w samochodzie

    agent.chat("Dodaj do koszyka espresso, małe")
    agent.chat("Podsumuj zamówienie")
    agent.chat("Dodaj do koszyka espresso, małe")
    agent.chat("Podsumuj zamówienie")
    conversation_log = agent.get_conversation_log()

    assert (
        "Orders completed: 3" in conversation_log
    )  # 2 zamówienia z testu metryk oraz jedno z testu przepływu
    assert "Total revenue: 28.0" in conversation_log
    print("✅ Metryki przeszły test")

    print("\n🎉 Wszystkie testy przeszły pomyślnie!")
    print("🚀 Aplikacja jest gotowa do uruchomienia!")


if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"❌ Testy nie przeszły: {e}")
        sys.exit(1)
