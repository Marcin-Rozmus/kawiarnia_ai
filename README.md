# ☕ Kawiarnia AI First - Asystent Zamówień

Aplikacja wykorzystuje agenta AI zbudowanego w LangGraph do obsługi zamówień klientów w kawiarni.

W ten sposób adresujemy obsługę klienta w kawiarni. Pozwala to na zmniejszenie obłożenia pracowników/kasjerów.
To popularny obecnie trend delegowania zbierania zamówień z pracowników na systemy informatyczne/kioski.

Wszystkie elementy składowe mogą i powinny zostać rozbudowane w dalszych etapach.
Poszczególne kroki agenta można zastąpić integracjami z serwisami po API (np. checkout mógłby być wywołany po API z systemu kawiarni).

Aplikacja obecnie nie pozwala na edycję lub usuwanie elementów w koszyku. To kolejny krok rozwoju.
Następnym krokiem może być podpięcie systemu płatności.

Przykładowe interakcje w aplikacji są umieszczone w prawej części interfejsu użytkownika.

## Opis aplikacji

Klient prowadzi konwersację z chatbotem na temat napoju jaki chce zamówić, dobiera dodatki i zamienniki. Gdy jest zadowolony to dany produkt dodawany jest do koszyka. Gdy wszystkie pożądane produkty są już w koszyku można przejść do podsumowania.

## Jaki problem rozwiązuje agent?
Agent pokrywa kluczowe funkcje systemu sprzedaży i obsługi klienta.

Agent AI rozwiązuje problem długiego czasu obsługi i ograniczonej dostępności personelu w kawiarniach, szczególnie w godzinach szczytu. Automatyzując proces składania zamówień, udzielania informacji o ofercie oraz finalizacji transakcji, agent zwiększa efektywność operacyjną i poprawia doświadczenie klienta. Dzięki temu kawiarnia może obsłużyć więcej osób szybciej, przy mniejszym zaangażowaniu pracowników.

## Szybki start

### 1. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 2. Konfiguracja API OpenAI

Utwórz plik `.env` w głównym katalogu projektu:

```bash
OPENAI_API_KEY=twój_klucz_api_openai
```

### 3. Uruchomienie aplikacji

```bash
python main.py
```

Aplikacja będzie dostępna pod adresem: http://127.0.0.1:7860

## Uruchomienie testów

```bash
python tests.py
```

## Struktura projektu

```
/
├── main.py              # Główny plik aplikacji
├── gui.py               # Interfejs graficzny Gradio
├── agent.py             # Logika agenta AI i węzły grafu
├── config.py            # Konfiguracja i menu kawiarni
├── tests.py             # Testy aplikacji
├── requirements.txt     # Zależności Python
├── README.md           # Ten plik
└── .env                # Plik z kluczem API (do utworzenia)
```

## Funkcjonalności

- **Inteligentny asystent**: Agent rozumie naturalny język i pomaga w składaniu zamówień
- **Personalizacja**: Agent obsługuje wybór dodatków (syropy, mleko) i zamienników (mleko roślinne)
- **Zarządzanie koszykiem**: Agent dodaje wybrane produkty do koszyka i oblicza ceny
- **Interfejs graficzny**: Interakcja poprzez interfejs Gradio
- **Graf przepływu**: Aplikacja używa LangGraph do zarządzania stanem i przepływem rozmowy

## Przykładowe interakcje

- "Chciałbym latte średnie"
- "Dodaj syrop waniliowy"
- "Dodaj napój do koszyka"
- "Finalizuj zamówienie"

## Architektura

Aplikacja używa LangGraph do zarządzania przepływem rozmowy:

- **Węzeł START** - punkt, z którego rozpoczyna się praca agenta
- **Węzeł validate_input** - sprawdza czy użytkownik nie prosi o rzeczy zabronione
- **Węzeł process_input** - przetwarza intencję użytkownika i aktualizuje stan
- **Węzeł add_to_cart** - dodaje napój ze stanu agenta do koszyka
- **Węzeł checkout** - podsumowuje zamówienie
- **Węzeł END** - kończy daną turę interakcji

## Metryki

Aplikacja śledzi dwie metryki biznesowe:
- `orders_completed` - łączna ilość zamówień
- `total_revenue` - całkowity przychód

Metryki nie kasują się przy resecie stanu agenta dzięki czemu mamy zebrane gotowe dane dla uzasadnienia biznesowego użycia agenta.

## Monitoring działania i logika fallback
Logi są numerowane i wyświetlane w formie nazwa_kroku(dane_wejściowe): dane_wyjściowe plus dodatkowe informacje.
W produkcyjnych logach należy dodać id klienta, id rozmowy itd.

Odpowiedzi LLM są zwracane i przetwarzane w formacie JSON. W przypadku gdyby JSON się nie sparsował to jest to obsłużone (fallback).

## Bezpieczeństwo

Agent zawiera guardraile chroniące przed:
- Próbami zmiany języka na inny niż polski
- Próbami zmiany cen
- Zapytaniami zawierającymi wulgaryzmy

## Technologie

- **Python 3.8+**
- **LangGraph** - framework do budowy agentów AI
- **OpenAI GPT-4o-mini** - model językowy
- **Gradio** - interfejs graficzny
- **python-dotenv** - zarządzanie zmiennymi środowiskowymi

## Uwagi

- Aplikacja jest Proof of Concept i może wymagać rozbudowy w środowisku produkcyjnym
- Wszystkie elementy składowe mogą i powinny zostać rozbudowane w dalszych etapach
- Aplikacja obecnie nie pozwala na edycję lub usuwanie elementów w koszyku
- Następnym krokiem może być podpięcie systemu płatności

## Kontakt

W przypadku pytań lub problemów, sprawdź logi aplikacji lub uruchom testy.
