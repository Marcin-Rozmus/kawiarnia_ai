import gradio as gr
from agent import Agent
from config import get_menu


class CoffeeShopGUI:
    """Klasa interfejsu graficznego kawiarni"""

    def __init__(self):
        self.agent = Agent()

    def chat(self, message, history):
        """Funkcja obsługująca czat z agentem"""
        if not message.strip():
            return "", history

        # Pobierz odpowiedź od agenta
        response = self.agent.chat(message)

        # Dodaj wiadomość użytkownika i odpowiedź do historii w formacie messages
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})

        # Aktualizacja koszyka
        cart_info = self.get_cart_info()

        # Pobierz historię rozmowy
        conversation_log = self.agent.get_conversation_log()

        # Log jest już w formacie JSON, więc możemy go użyć bezpośrednio
        log_text = conversation_log

        # Zwróć odpowiedź, historię rozmowy, informacje o koszyku i log działania aplikacji
        return "", history, cart_info, log_text

    def get_cart_info(self):
        """Zwraca informacje o koszyku"""
        # Pobierz informacje o koszyku
        cart = self.agent.get_cart_summary()

        # Jeśli koszyk jest pusty, zwróć odpowiednią odpowiedź
        if not cart["items"]:
            return "🛒 Koszyk jest pusty"

        # Tworzenie tekstu koszyka
        cart_text = f"🛒 Koszyk ({cart['item_count']} przedmiotów)\n\n"

        # Tworzenie tekstu dla każdego elementu w koszyku
        for i, item in enumerate(cart["items"], 1):
            # Tworzenie opisu wybranych dodatków
            customizations = (
                ", ".join(item["customizations"])
                if item["customizations"]
                else "bez dodatków"
            )
            # Tworzenie opisu zamienników
            substitutions = (
                ", ".join(item["substitutions"])
                if item["substitutions"]
                else "standardowe"
            )
            # Tworzenie tekstu dla każdego elementu w koszyku
            cart_text += f"{i}. {item['drink'].title()} {item['size']}\n"
            cart_text += f"   Dodatki: {customizations}\n"
            cart_text += f"   Zamienniki: {substitutions}\n"
            cart_text += f"   Cena: {item['price']} zł\n\n"

        # Dodanie łącznej kwoty do tekstu
        cart_text += f"💰 Łączna kwota: {cart['total']} zł"

        # Zwróć tekst koszyka
        return cart_text

    def reset_agent(self):
        """Resetuje stan agenta"""
        self.agent.reset()
        return "🛒 Koszyk jest pusty", self.agent.get_conversation_log()

    def create_interface(self):
        """Tworzy interfejs Gradio"""
        with gr.Blocks(
            title="☕ Kawiarnia AI - Asystent Zamówień", theme=gr.themes.Soft()
        ) as gui:

            # Dodanie tytułu aplikacji
            gr.Markdown("""# ☕ Kawiarnia AI First""")

            gr.Markdown(
                """Aplikacja wykorzystuje LLM, nie podawaj danych wrażliwych."""
            )

            # Dodanie menu
            gr.Markdown(get_menu())

            # Dodanie czatu i koszyka
            with gr.Row():
                with gr.Column(scale=2):
                    # Czat
                    chatbot = gr.Chatbot(
                        label="Rozmowa z asystentem",
                        height=500,
                        show_label=True,
                        container=True,
                        type="messages",
                    )

                    with gr.Column():
                        msg = gr.Textbox(
                            label="Twoja wiadomość",
                            placeholder="Np. 'Chciałbym duże americano bez dodatków'",
                            scale=4,
                        )
                        send_btn = gr.Button("Wyślij", variant="primary", scale=1)

                with gr.Column(scale=1):
                    # Koszyk
                    cart_display = gr.Textbox(
                        label="🛒 Twój koszyk",
                        value="🛒 Koszyk jest pusty",
                        lines=20,
                        interactive=False,
                        container=True,
                    )

                    # Przykładowe wiadomości
                    gr.Markdown(
                        """
                    **💡 Przykładowe interakcje:**
                    - "Chciałbym latte średnie"
                    - "Dodaj syrop waniliowy"
                    - "Dodaj napój do koszyka"
                    - "Finalizuj zamówienie"
                    """
                    )

            # Dodanie logu działania aplikacji
            with gr.Row():
                with gr.Column(scale=2):
                    conversation_log_display = gr.Textbox(
                        label="📝 Log działania aplikacji",
                        value="📝 Brak logów",
                        lines=15,
                        interactive=False,
                        container=True,
                        elem_classes=["conversation-log"],
                    )

            # Dodanie przycisków kontrolnych
            with gr.Row():
                reset_btn = gr.Button("🔄 Resetuj agenta", variant="secondary")
                clear_log_btn = gr.Button("🧹 Wyczyść logi", variant="secondary")

            # Obsługa przycisku wysyłania wiadomości
            msg.submit(
                self.chat,
                [msg, chatbot],
                [msg, chatbot, cart_display, conversation_log_display],
            )
            send_btn.click(
                self.chat,
                [msg, chatbot],
                [msg, chatbot, cart_display, conversation_log_display],
            )

            # Obsługa przycisków kontrolnych
            reset_btn.click(
                self.reset_agent, outputs=[cart_display, conversation_log_display]
            )
            clear_log_btn.click(
                lambda: self.agent.clear_conversation_log()
                or self.agent.get_conversation_log(),
                outputs=[conversation_log_display],
            )

        return gui


def main():
    """Główna funkcja aplikacji"""
    gui_handler = CoffeeShopGUI()
    interface = gui_handler.create_interface()

    print("🚀 Uruchamianie aplikacji Kawiarnia AI...")
    print("📝 Pamiętaj, aby utworzyć plik .env z kluczem OPENAI_API_KEY")

    interface.launch(
        share=False,
        debug=True,
        server_name="127.0.0.1",
        server_port=7860,
        favicon_path="coffee.svg",
    )


if __name__ == "__main__":
    main()
