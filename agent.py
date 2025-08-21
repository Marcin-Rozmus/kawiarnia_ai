import json
from typing import Dict, List, TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from config import CFG


class AgentState(TypedDict):
    """Definicja stanu aplikacji"""

    is_valid: Annotated[
        bool,
        "Czy w ostatnim zapytaniu użytkownik nie prosi o zrobienie rzeczy zabronionych",
    ]
    intent: Annotated[str, "Najnowsza intencja użytkownika"]
    messages: Annotated[List, "Historia wiadomości"]
    cart: Annotated[Dict, "Koszyk z zamówieniami"]
    current_order: Annotated[Dict, "Aktualne zamówienie w trakcie tworzenia"]
    order_complete: Annotated[bool, "Czy zamówienie jest gotowe"]
    orders_completed: Annotated[int, "Liczba zamówień zakończonych"]
    total_revenue: Annotated[float, "Całkowity przychód"]
    conversation_log: Annotated[List, "Log konwersacji z dodatkowymi informacjami"]


def create_llm():
    """Tworzy instancję LLM"""
    return ChatOpenAI(api_key=CFG.api_key, model=CFG.model)


def initialize_state(
    orders_completed: int = 0, total_revenue: float = 0.0
) -> AgentState:
    """Inicjalizuje stan agenta"""
    return {
        "is_valid": True,
        "intent": None,
        "messages": [],
        "cart": {"items": [], "total": 0.0},
        "current_order": {
            "drink_type": None,
            "size": None,
            "customizations": [],
            "substitutions": [],
        },
        "order_complete": False,
        "orders_completed": orders_completed,
        "total_revenue": total_revenue,
        "conversation_log": [],
    }


def validate_user_input(state: AgentState) -> AgentState:
    """Guardrail dla zapytania użytkownika"""

    # Stwórz obiekt LLM'a
    llm = create_llm()

    # Pobierz ostatnią wiadomość użytkownika
    user_message = state["messages"][-1].content if state["messages"] else ""

    # Kontekst dla LLM
    system_prompt = f"""Jesteś pomocnym asystentem w kawiarni. Pomagasz klientom składać zamówienia.
    
    Twoim zadaniem jest walidacja zapytania użytkownika. 
    Zastanów się czy użytkownik nie prosi o zrobienie rzeczy zabronionych.

    Zabronione rzeczy:
    - Zabrania się prób zmiany języka na inny niż polski.
    - Zabrania się prób zmiany cen.
    - Zapytania zawierające wulgaryzmy są zabronione.

    Jeżeli użytkownik prosi o zrobienie rzeczy zabronionych, zwróć w polu is_valid False.
    Jeżeli użytkownik prosi o zrobienie rzeczy dozwolonych, zwróć w polu is_valid True.
    
    Przeanalizuj wiadomość i zwróć JSON z następującymi polami:
    {{
        "is_valid": bool,
    }}
    Nie dodawaj żadnych innych informacji poza JSON. Żadnych dodatkowych znaków. Nie umiesczaj opisu, że to JSON.
    """

    # Kontekst do przeanalizowania
    analysis_prompt = f"""
    {system_prompt}
    
    Wiadomość klienta: {user_message}
    """

    # Wywołanie LLM'a z kontekstem
    response = llm.invoke([HumanMessage(content=analysis_prompt)])

    # Próba sparsowania odpowiedzi do JSON z obsługą fallback
    try:
        analysis = json.loads(response.content)

        # Aktualizuj stan
        state["is_valid"] = analysis["is_valid"]

        # Zapisz do logu konwersacji
        state["conversation_log"].append(
            f"validate_user_input({user_message}): {response.content}"
        )

    except json.JSONDecodeError:
        # Fallback response
        fallback_response = "Przepraszam, nie zrozumiałem. Czy możesz powtórzyć?"
        state["messages"].append(AIMessage(content=fallback_response))

        # Zapisz do logu konwersacji
        state["conversation_log"].append(
            f"process_user_input({user_message}): {fallback_response} + \n{response.content}"
        )

    # Zwraca stan agenta do dalszego przetwarzania.
    return state


def process_user_input_route(state: AgentState) -> AgentState:
    """Decyduje czy przetwarzać dalej czy wrócić do interakcji z użytkownikiem"""

    # Jeżeli użytkownik nie prosi o rzeczy zabronione, przetwarzamy dalej
    if state["is_valid"]:
        state["conversation_log"].append(
            f"process_user_input_route: process_user_input"
        )
        return "process_input"
    else:
        state["conversation_log"].append(f"process_user_input_route: forbidden_input")
        return "forbidden_input"


def process_user_input(state: AgentState) -> AgentState:
    """Przetwarza input użytkownika i aktualizuje stan"""

    # Tworzy obiekt LLM'a
    llm = create_llm()

    # Pobierz ostatnią wiadomość użytkownika
    user_message = state["messages"][-1].content if state["messages"] else ""

    # Przygotuj listę dostępnych napojów
    all_drinks = []
    for _, drinks in CFG.AVAILABLE_DRINKS.items():
        all_drinks.extend(drinks)

    # Kontekst dla LLM
    system_prompt = f"""Jesteś pomocnym asystentem w kawiarni. Pomagasz klientom składać zamówienia.
    
    Dostępne napoje:
    - Kawa: {', '.join(CFG.AVAILABLE_DRINKS['kawa'])}
    - Herbata: {', '.join(CFG.AVAILABLE_DRINKS['herbata'])}
    - Napoje zimne: {', '.join(CFG.AVAILABLE_DRINKS['napoje zimne'])}
    
    Rozmiary: {', '.join([f'{size} ({CFG.SIZE_NAMES[size]})' for size in CFG.SIZES])}
    
    Dodatki: {', '.join(CFG.ADDON_PRICES.keys())}
    Zamienniki: {', '.join(CFG.SUBSTITUTIONS.keys())}
    
    Twoim zadaniem jest:
    1. Zrozumieć co klient chce zamówić
    2. Zapytać o szczegóły jeśli potrzebne
    3. Dodać do koszyka gdy zamówienie jest kompletne
    4. Zaproponować dodatki lub zamienniki

    
    Na początku doprecyzuj zamówienie klienta (rodzaj napoju, rozmiar, dodatki, zamienniki).
    Jeżeli klient nie podał wszystkich informacji, zapytaj o brakujące.
    
    Do koszyka dodaj zamówienie dopiero gdy klient wyrazi zgodę. Na początku informacje o zamówieniu trzymasz w pamięci.

    w polu intent zwróć:
    - order_drink jeśli klient chce zamówić napój
    - ask_question jeśli klient chce uzyskać informację
    - modify_order jeśli klient chce zmienić zamówienie
    - checkout jeśli klient chce zakończyć zamówienie
    - add_to_cart jeśli klient chce dodać zamówienie do koszyka
    
    Przeanalizuj wiadomość klienta i zwróć JSON z następującymi polami:
    {{
        "intent": "order_drink|ask_question|modify_order|checkout|add_to_cart",
        "drink_type": "nazwa napoju lub null",
        "size": "S|M|L lub null", 
        "customizations": ["lista dodatków"],
        "substitutions": ["lista zamienników"],
        "response": "odpowiedź dla klienta"
    }}
    Nie dodawaj żadnych innych informacji poza JSON. Żadnych dodatkowych znaków.
    """

    # Analizuj input użytkownika
    analysis_prompt = f"""
    {system_prompt}

    Obecne zamówienie: {state['current_order']}
    
    Wiadomość klienta: {user_message}
    """

    # Wywołanie LLM'a z kontekstem
    response = llm.invoke([HumanMessage(content=analysis_prompt)])

    # Próba sparsowania odpowiedzi do JSON i obsługi intencji
    try:
        # Parsowanie odpowiedzi do JSON
        analysis = json.loads(response.content)

        # Aktualizuj current_order jeśli podano szczegóły.
        # Pozwala to na modyfikację napoju bez potrzeby ponownego podawania wszystkich innych cech.
        if analysis.get("intent"):
            state["intent"] = analysis["intent"]
        if analysis.get("drink_type"):
            state["current_order"]["drink_type"] = analysis["drink_type"]
        if analysis.get("size"):
            state["current_order"]["size"] = analysis["size"]
        if analysis.get("customizations"):
            for item in analysis["customizations"]:
                if item not in state["current_order"]["customizations"]:
                    state["current_order"]["customizations"].append(item)
        if analysis.get("substitutions"):
            for item in analysis["substitutions"]:
                if item not in state["current_order"]["substitutions"]:
                    state["current_order"]["substitutions"].append(item)

        # Dodaj odpowiedź do historii
        state["messages"].append(AIMessage(content=analysis["response"]))

        # Zapisz do logu konwersacji
        state["conversation_log"].append(
            f"""process_user_input({user_message}): {response.content}\n\n Stan zamówienia: Napój: {state['current_order']['drink_type']},  Rozmiar: {state['current_order']['size']} Dostępne dodatki: {state['current_order']['customizations']} Dostępne zamienniki: {state['current_order']['substitutions']}\n\n"""
        )

    except json.JSONDecodeError:
        # W przypadku błędu parsowania odpowiedzi, zwracamy fallback.
        fallback_response = "Przepraszam, nie zrozumiałem. Czy możesz powtórzyć?"
        state["messages"].append(AIMessage(content=fallback_response))

        # Zapisz do logu konwersacji
        state["conversation_log"].append(
            f"process_user_input({user_message}): {fallback_response} + \n{response.content}"
        )

    # Zwraca stan agenta do dalszego przetwarzania.
    return state


def add_to_cart(state: AgentState) -> AgentState:
    """Dodaje aktualne zamówienie do koszyka"""

    # Zapisz do logu konwersacji
    state["conversation_log"].append(f"add_to_cart({state['current_order']})")

    # Sprawdź czy napój i rozmiar są poprawne
    if state["current_order"]["drink_type"] and state["current_order"]["size"]:

        # Pobierz dane z aktualnego zamówienia
        drink = state["current_order"]["drink_type"]
        size = state["current_order"]["size"]
        price = CFG.DRINK_PRICES.get(drink, {}).get(size, 10)

        # Dodaj koszty dodatków
        for custom in state["current_order"]["customizations"]:
            price += CFG.ADDON_PRICES.get(custom, 0)

        # Utwórz element koszyka
        cart_item = {
            "drink": drink,
            "size": size,
            "customizations": state["current_order"]["customizations"].copy(),
            "substitutions": state["current_order"]["substitutions"].copy(),
            "price": price,
        }

        # Dodaj element do koszyka
        state["cart"]["items"].append(cart_item)
        state["cart"]["total"] += price

        # Resetuj current_order
        state["current_order"] = {
            "intent": None,
            "drink_type": None,
            "size": None,
            "customizations": [],
            "substitutions": [],
        }

        # Zapisz do logu konwersacji
        state["conversation_log"].append(
            f"Koszyk: {len(state['cart']['items'])} przedmiotów, {state['cart']['total']} zł"
        )

        # Dodaj potwierdzenie do historii rozmowy
        state["messages"].append(
            AIMessage(
                content=f"Dodałem {drink} {size} do koszyka. Cena: {price} zł. Co jeszcze chciałbyś zamówić?"
            )
        )

    # Zwraca stan agenta do dalszego przetwarzania.
    return state


def checkout(state: AgentState) -> AgentState:
    """Finalizuje zamówienie"""

    # Sprawdź czy koszyk nie jest pusty
    if state["cart"]["items"]:
        # Tworzy podsumowanie zamówienia
        items_summary = []
        # Dla każdego elementu w koszyku tworzymy podsumowanie
        for item in state["cart"]["items"]:
            customizations = (
                ", ".join(item["customizations"])
                if item["customizations"]
                else "bez dodatków"
            )
            substitutions = (
                ", ".join(item["substitutions"])
                if item["substitutions"]
                else "standardowe"
            )
            items_summary.append(
                f"- {item['drink']} {item['size']} ({customizations}, {substitutions}) - {item['price']} zł"
            )
        summary = "\n".join(items_summary)
        total = state["cart"]["total"]

        state["orders_completed"] += 1
        state["total_revenue"] += total

        # Tworzy odpowiedź do użytkownika
        final_message = f"""
        🎉 Dziękuję za zamówienie! Oto podsumowanie:
        
        {summary}
        
        💰 Łączna kwota: {total} zł
        
        Zamówienie zostanie przygotowane za kilka minut. Miłego dnia! ☕
        """

        # Dodaje odpowiedź do historii rozmowy
        state["messages"].append(AIMessage(content=final_message))

        # Zerowanie koszyka
        state["cart"]["items"] = []
        state["cart"]["total"] = 0.0

        # Resetowanie current_order
        state["current_order"] = {
            "drink_type": None,
            "size": None,
            "customizations": [],
            "substitutions": [],
        }

        # Zapisz do logu konwersacji
        cart_state = f"Koszyk: {len(state['cart']['items'])} przedmiotów, {state['cart']['total']} zł"
        state["conversation_log"].append(
            f"checkout: {final_message} + \n{cart_state} + \n{state['current_order'].copy()}"
        )
    else:
        empty_cart_message = "Koszyk jest pusty. Czy chciałbyś coś zamówić?"
        state["messages"].append(AIMessage(content=empty_cart_message))

        # Zapisz do logu konwersacji
        cart_state = f"Koszyk: {len(state['cart']['items'])} przedmiotów, {state['cart']['total']} zł"
        state["conversation_log"].append(
            f"checkout: {empty_cart_message} + \n{cart_state} + \n{state['current_order'].copy()}"
        )

    # Zwraca stan agenta do dalszego przetwarzania.
    return state


def add_to_cart_route(state: AgentState) -> str:
    """Decyduje czy dodać do koszyka, podsumować zamówienie czy kontynuować rozmowę"""

    # Decyduje czy dodać do koszyka, podsumować zamówienie czy kontynuować rozmowę
    if state["intent"] == "add_to_cart":
        state["conversation_log"].append(
            f"add_to_cart_route({state['intent']}): add_to_cart"
        )
        return "add_to_cart"
    elif state["intent"] == "checkout":
        state["conversation_log"].append(
            f"add_to_cart_route({state['intent']}): checkout"
        )
        return "checkout"
    else:
        state["conversation_log"].append(
            f"add_to_cart_route({state['intent']}): continue"
        )
        return "continue"


def create_agent_graph():
    """Tworzy graf agenta LangGraph"""

    # Tworzenie grafu
    workflow = StateGraph(AgentState)

    # Dodanie węzłów
    workflow.add_node("validate_input", validate_user_input)
    workflow.add_node("process_input", process_user_input)
    workflow.add_node("add_to_cart", add_to_cart)
    workflow.add_node("checkout", checkout)

    # Dodanie krawędzi
    workflow.add_edge(START, "validate_input")
    workflow.add_edge("add_to_cart", END)
    workflow.add_edge("checkout", END)

    # Dodanie warunkowych krawędzi
    workflow.add_conditional_edges(
        "validate_input",
        process_user_input_route,
        {"process_input": "process_input", "forbidden_input": END},
    )
    workflow.add_conditional_edges(
        "process_input",
        add_to_cart_route,
        {"add_to_cart": "add_to_cart", "checkout": "checkout", "continue": END},
    )

    # Zwraca skompilowany graf
    return workflow.compile()


class Agent:
    """Klasa agenta"""

    # Inicjalizacja grafu i stanu agenta
    def __init__(self):
        self.graph = create_agent_graph()
        self.state = initialize_state()

    # Główna metoda do obsługi czatu
    def chat(self, message: str) -> str:
        """Główna metoda do obsługi czatu"""

        # Dodaj wiadomość użytkownika
        self.state["messages"].append(HumanMessage(content=message))

        # Sprawdź czy to checkout
        if "checkout" in message.lower() or "finalizuj" in message.lower():
            self.state = checkout(self.state)
        else:
            # Uruchom graf
            self.state = self.graph.invoke(self.state)

        # Zwróć ostatnią odpowiedź
        if self.state["messages"]:
            return self.state["messages"][-1].content
        return "Przepraszam, wystąpił błąd."

    def get_cart_summary(self) -> Dict:
        """Zwraca podsumowanie koszyka"""
        return {
            "items": self.state["cart"]["items"],
            "total": self.state["cart"]["total"],
            "item_count": len(self.state["cart"]["items"]),
        }

    def reset(self):
        """Resetuje stan agenta z zachowaniem metryk"""
        orders_completed = self.state["orders_completed"]
        total_revenue = self.state["total_revenue"]
        self.state = initialize_state(orders_completed, total_revenue)

    def get_conversation_log(self) -> List[Dict]:
        """Zwraca pełny log konwersacji i metryki"""

        # Tworzy log konwersacji z metrykami
        converstion_log = f"Orders completed: {self.state['orders_completed']}\nTotal revenue: {self.state['total_revenue']}\n"
        converstion_log += "\n".join(self.state["conversation_log"])
        return converstion_log

    def clear_conversation_log(self):
        """Czyści log konwersacji"""
        self.state["conversation_log"] = []
