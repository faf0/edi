# EDI (Edgar's Delightful Interface)

EDI (pronounced "Eddie") is a command-line chatbot interface that allows users to interact with various AI models through the Poe API.
This interface supports maintaining conversation context across multiple messages.

If EDI has a song, it will be this one: [Erste Allgemeine Verunsicherung (EAV) - Edi](https://www.youtube.com/watch?v=QN1Ek7pAoVc)

## Features

- Multi-line input support.
- Context preservation during chat sessions.
- Easy configuration management.
- Loading indicators during model responses.
- Option to continue previous sessions or start fresh.

## Use Cases

Imagine this: you're in the terminal when a question pops up.
Instead of switching to a browser, just tap into your AI bot right from the terminal!
Type your question, hit enter, and voila!

As your conversation can be saved locally, you can call EDI as your mentor anytime from anywhere for wise advice based on your prior interactions.

## Requirements

- Python 3.x

## Installation

1. Clone the repository or download the `edi.py` file.
2. Ensure you have Python 3 installed on your machine.
3. Create a Poe API key under [https://poe.com/api_key](https://poe.com/api_key).

## Configuration

Before running the chatbot, you need to set up your API key:

1. Run the script:
```shell
python edi.py
```
2. Enter your Poe API key when prompted (it should be 43 characters long).
3. Select a model from the list provided.

The configuration will be saved in `~/.config/edi/config.json`.

## Usage

1. Start the chatbot by running the script:
```shell
python edi.py
```
2. Follow the prompts to enter your input.
3. Use Ctrl-D or leave a blank line to signal the end of input.
4. To exit the chat session, press Ctrl-D on a blank input line or end with a blank line.

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

# How EDI Was Written

EDI can be written using EDI.
For fun and the sake of good education, please read "Reflections on Trusting Trust" by Ken Thompson. 

# Contributing

This project was written to get familiar with the Poe API.
Feel free to submit pull requests for improvements or bug fixes.

# License

This project is licensed under the MIT License.
