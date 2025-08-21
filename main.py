#!/usr/bin/env python3
"""
☕ Kawiarnia AI First - Asystent Zamówień

Aplikacja wykorzystuje agenta AI zbudowanego w LangGraph do obsługi zamówień klientów.
"""

import sys
import os

# Dodaj katalog główny do ścieżki Pythona
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Aplikacja została zatrzymana przez użytkownika")
    except Exception as e:
        print(f"❌ Wystąpił błąd: {e}")
        print(
            "📝 Sprawdź czy masz poprawnie skonfigurowany plik .env z kluczem OPENAI_API_KEY"
        )
