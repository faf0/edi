#!/usr/bin/env python3

import getpass
import http.client
import json
import os
import threading
import time
from typing import Dict, Any, List

CONFIG_PATH = os.path.expanduser("~/.config/edi/config.json")
SESSION_FILE = os.path.expanduser("~/.config/edi/session.json")
MODELS = [
    "Assistant",
    "Web-Search",
    "Claude-Opus-4.1",
    "Claude-Sonnet-4",
    "GPT-5",
    "GPT-5-Chat",
    "GPT-5-mini",
    "Gemini-2.5-Pro",
    "Grok-4",
]
POE_API_KEY_LENGTH = 43
MessageType = Dict[str, Any]
MessagesType = List[MessageType]
INPUT_PROMPT = ">>> \n"
OUTPUT_PROMPT = "\n<<< \n"

loading: bool


def load_config() -> Dict[str, str]:
    """Load the configuration from the config file."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(api_key: str, model: str) -> None:
    """Save the API key and selected model to the config file."""
    config = {
        "api_key": api_key,
        "model": model,
    }
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f)


def save_session(messages: MessagesType) -> None:
    """Save the session messages to a file."""
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f)


def load_session() -> MessagesType:
    """Load the session messages from a file."""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_user_input(prompt: str) -> str:
    """Get user input from the command line."""
    print(prompt, end="", flush=True)
    lines = []
    while True:
        try:
            line = input()
        except EOFError:  # Ctrl-D
            break
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)


def get_api_key() -> str:
    """Get the API key from the user, masking the input."""
    while True:
        api_key = getpass.getpass(
            "Enter your Poe API key.\n"
            "No characters will be displayed as you type.\n"
            "Press Enter when done.\n"
        )
        if len(api_key) == POE_API_KEY_LENGTH:
            return api_key
        print("Invalid API key length. " f"Expected {POE_API_KEY_LENGTH} characters.")


def get_model() -> str:
    """Get the Poe.com model/bot from the user."""
    print("Available models:")
    for i, model in enumerate(MODELS):
        print(f"{i + 1}: {model}")

    model_choice = int(input("Select a model by number: ")) - 1
    if 0 <= model_choice < len(MODELS):
        return MODELS[model_choice]
    print(f"Invalid choice, defaulting to {MODELS[0]}.")
    return MODELS[0]


def show_loading_dots() -> None:
    """Show loading dots while waiting for the model response."""
    print("\nLoading", end="", flush=True)
    while True:
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(0.5)
        if not loading:  # Check if we should stop loading
            break
    print()  # New line after loading complete


def chat(api_key: str, model: str, messages: MessagesType) -> MessagesType:
    """Send chat messages (interaction history) to the Poe API and return the response."""
    conn = http.client.HTTPSConnection("api.poe.com")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "stream": False,
        }
    )

    conn.request("POST", "/v1/chat/completions", payload, headers)
    response = conn.getresponse()

    if response.status != 200:
        raise Exception(f"Error: {response.status} {response.reason}")

    response_data = response.read()
    conn.close()
    return json.loads(response_data)


def load_messages() -> MessagesType:
    """
    Return messages from a previous session if users wants to continue session
    or none otherwise.
    """
    messages = []  # List to hold the conversation context

    continue_session = input("Continue last session? (y/n): ").strip().lower()
    if continue_session not in ["y", "n", ""]:
        continue_session = "n"  # Default to 'no' if input is invalid

    if continue_session == "n":
        messages.clear()  # Clear previous messages if starting new session
    else:
        messages = load_session()

    return messages


def message_loop(api_key: str, model: str) -> None:
    """
    Implementation of the chat loop, reading user input and writing bot
    output in each iteration.
    """
    messages = load_messages()
    global loading

    while True:
        user_input = get_user_input(INPUT_PROMPT)
        if user_input.strip() == "":
            break  # Exit on blank input line

        messages.append(
            {"role": "user", "content": user_input}
        )  # Add user input to messages

        # Start loading dots in a separate thread
        loading = True
        loading_thread = threading.Thread(target=show_loading_dots)
        loading_thread.start()

        try:
            response_data = chat(api_key=api_key, model=model, messages=messages)
            loading = False  # Stop loading dots
            loading_thread.join()  # Wait for loading thread to finish

            choices = response_data.get("choices", [])
            if choices:
                print(OUTPUT_PROMPT, end="")
                for choice in choices:
                    content = choice["message"].get("content", "")
                    print(content, end="", flush=True)
                print()  # New line after the response
                # Add assistant's response to messages for context
                messages.append({"role": "assistant", "content": content})
                save_session(messages)
            else:
                print("\n<<< No response received.")
        except Exception as e:
            loading = False  # Stop loading dots
            loading_thread.join()  # Ensure loading thread finishes
            print(f"\n<<< Error: {e}")


def main() -> None:
    """Main function to run the EDI chatbot."""
    config = load_config()

    if config:
        api_key = config["api_key"]
        model = config["model"]
    else:
        api_key = get_api_key()
        model = get_model()
        save_config(api_key, model)

    print("\nWelcome to EDI! (Edgar's Delightful Interface)\n")
    print("Type 'Ctrl-D' or leave a blank line to end input and get the response.\n")

    message_loop(api_key=api_key, model=model)


if __name__ == "__main__":
    main()
