# Edi (Edgar's delightful interface)

Edi (pronounced "Eddie") is a command-line chatbot interface that allows users to interact with various AI models through the Poe API.
Edi supports maintaining conversation context across multiple messages.

If Edi has a song, it will be this one: [Erste Allgemeine Verunsicherung (EAV) - Edi](https://www.youtube.com/watch?v=QN1Ek7pAoVc)

## Features

- Multi-line input support.
- Context preservation during chat sessions.
- Easy configuration management.
- Loading indicators during model responses.
- Option to continue previous sessions or start fresh.

## Use Cases

Imagine this: you're in the terminal when a question pops up.
Instead of switching to a browser, just tap into your favorite AI bot right from the terminal.
Type your question, hit enter, and you get the answer!

As your conversation can be saved locally, you can call Edi as your mentor anytime from anywhere for wise advice based on prior interactions.

## Requirements

- Python 3.x

## Installation

1. Clone the repository or download the `edi.py` file.
2. Ensure you have Python 3 installed on your machine.
3. (Optional.) Link `edi.py` to `/usr/local/bin/edi` and make Edi executable, so you can just type `edi` on the terminal to run it:
```shell
chmod +x /path/to/edi.py
sudo ln -s /path/to/edi/edi.py /usr/local/bin/edi
```

## Configuration

Before running Edi, you need to set up your Poe API key under [https://poe.com/api_key](https://poe.com/api_key).

1. Run Edi:
```shell
python3 edi.py
edi # if linked to /usr/loca/bin/
```
2. Enter your Poe API key when prompted (it should be 43 characters long).
3. Select a model from the list provided.

The configuration will be saved in `~/.config/edi/config.json`.

The message history will be saved in `~/.config/edi/session.json`.

## Usage

### Interactive

1. Run Edi:
```shell
python3 edi.py
edi # if linked to /usr/loca/bin/
```
2. Run Edi with `--help` to see the list of supported command-line arguments.
3. Follow the prompts to enter your input.
4. Press Enter twice to end input.
5. Press Enter on a blank line to exit.

### Non-Interactive

You can pipe input into Edi and await the response from the bot for scripted use.
The optional `--continue` command-line argument allows you to continue the last session.
To start a fresh session, do not provide a command-line argument.

Example:
```shell
echo 'Please summarize.\nWrite a paragraph and a list of about 5 bullet points.' | \
  edi --continue
```

## Models Available

* Assistant
* Web-Search
* Claude-Opus-4.1
* Claude-Sonnet-4
* GPT-5
* GPT-5-Chat
* GPT-5-mini
* Gemini-2.5-Pro
* Grok-4
* ...and more models supported by [poe.com](https://poe.com/about)

# How Edi Was Written

Edi can be written using Edi, although you have to start somewhere.

For fun and the sake of good education, feel free read "Reflections on Trusting Trust" by Ken Thompson. 

# Contributing

This project was written to build something useful for myself, while getting familiar with the Poe API.
Feel free to submit pull requests for improvements or bug fixes.

# License

This project is licensed under the MIT License.
