# Discord GPT-4 Assistant Bot

This is a simple Discord bot that uses the OpenAI GPT-4 API to generate responses to user messages. The bot can respond to messages when mentioned or when the `!ask` command is used. It also allows for managing the bot's persona using the `!persona` command.

## Requirements

- Python 3.8+
- discord.py
- openai
- python-dotenv

## Setup

1. Clone this repository.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Set up a new Discord bot and retrieve its token. You can follow [this guide](https://discordpy.readthedocs.io/en/stable/discord.html) if you need help.
4. Set up an OpenAI account and retrieve your API key.
5. Create a `.env` file in the project directory from the `.env-sample` provided and replace the api keys.

6. Run the bot using `python bot.py`.

## Usage

- Send a message mentioning the bot or use the `!ask` command to ask a question or provide input to the bot.
- Use the `!persona` command to display the current bot persona.
- Use the `!persona your_new_persona` command to change the bot persona.
