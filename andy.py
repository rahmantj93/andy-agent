"""Run this file to chat with Andy."""
from dotenv import load_dotenv
load_dotenv()  # load .env file (Anthropic API key) into environment variables  

from storage import load_tasks
from agent import step


def chat():
    print("👋 Hi, I'm Andy — your task assistant. Type 'quit' to exit.\n")
    messages = []

    while True:
        user_message = input("👤 You: ").strip()

        if user_message.lower() in {"quit", "exit", "bye"}:
            print("👋 Catch you later!")
            break
        if not user_message:
            continue

        messages.append({"role": "user", "content": user_message})
        step(messages)


if __name__ == "__main__":
    load_tasks()
    chat()