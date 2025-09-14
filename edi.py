#!/usr/bin/env python3

import argparse
import getpass
import http.client
import json
import os
import sys
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
        print(f"Invalid API key length. Expected {POE_API_KEY_LENGTH} characters.")


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


def show_loading_dots(loading: List[bool], omit_print: bool) -> None:
    """Show loading dots while waiting for the model response."""
    if omit_print:
        # Printing that loading the message output is in progress is only
        # relevant when the user is interacting with the CLI.
        return
    print("\nLoading", end="", flush=True)
    while True:
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(0.5)
        # loading is a List with a single bool to make the bool mutable
        if not loading[0]:  # Check if we should stop loading
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


def load_messages(continue_session: bool, omit_prompt: bool) -> MessagesType:
    """
    Return messages from a previous session if users wants to continue session
    or none otherwise.
    """
    messages = []  # List to hold the conversation context

    if continue_session:
        # CLI argument was passed to continue session
        messages = load_session()

    if omit_prompt:
        # This tool is not used interactively.
        #
        message = sys.stdin.read().strip()
        messages.append({"role": "user", "content": message})
        print(INPUT_PROMPT, end="", flush=True)
        print(message, end="", flush=True)
    elif not continue_session:
        # This tool is used interactively and the flag to continue the last
        # session was not present, so prompt the user:
        continue_session_str = input("Continue last session? (y/n): ").strip().lower()
        if continue_session_str == "y":
            messages = load_session()

    return messages


def message_loop(
    api_key: str, model: str, continue_session: bool, omit_print: bool
) -> None:
    """
    Implementation of the chat loop, reading user input and writing bot
    output in each iteration.
    """
    messages = load_messages(continue_session, omit_print)

    while True:
        if not omit_print:
            user_input = get_user_input(INPUT_PROMPT)
            if user_input.strip() == "":
                break  # Exit on blank input line
            messages.append({"role": "user", "content": user_input})

        # Start loading dots in a separate thread
        # loading is a variable shared with the thread with a bool in a List to
        # make the bool mutable
        loading = [True]
        loading_thread = threading.Thread(
            target=show_loading_dots, args=(loading, omit_print)
        )
        loading_thread.start()

        try:
            response_data = chat(api_key=api_key, model=model, messages=messages)
            loading[0] = False  # Stop loading dots
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
            if omit_print:
                break
        except Exception as e:
            loading[0] = False  # Stop loading dots
            loading_thread.join()  # Ensure loading thread finishes
            print(f"\n<<< Error: {e}")
            if omit_print:
                break


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

    parser = argparse.ArgumentParser(
        description="Control EDI behavior with command line arguments."
    )
    parser.add_argument(
        "--continue",
        dest="continue_session",
        action="store_true",
        help="Continue the previous session",
    )
    args = parser.parse_args()

    # Check if input is being piped
    omit_print = not sys.stdin.isatty()  # Omit printing if input is from a pipe

    if not omit_print:
        print("\nWelcome to EDI! (Edgar's Delightful Interface)\n")
        print(
            "Type 'Ctrl-D' or leave a blank line to end input and get the response.\n"
        )

    message_loop(
        api_key=api_key,
        model=model,
        continue_session=args.continue_session,
        omit_print=omit_print,
    )


if __name__ == "__main__":
    main()
