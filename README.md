# Seria, A DFO Discord Bot

This is a Discord bot that uses LangChain and vector stores to answer questions about the popular video game Dungeon Fighter Online.

## Installation

1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Create a `.env` file in the root directory with your Discord bot token. This should be in the format `DISCORD_API_TOKEN=your_bot_token_here`.
4. Run the bot using `python bot.py`.

## Usage

The bot listens for commands that begin with `!`. Currently, the only command that is available is `!ask`. You can ask the bot a question about Dungeon Fighter Online by typing `!ask <your question here>` in a Discord text channel that the bot has access to. 

The bot will search for the answer to your question in a pre-defined set of documents related to Dungeon Fighter Online. It will then use LangChain to generate an answer based on the most relevant document.

## Contributing

We welcome contributions from the community! If you find a bug, have an idea for a new feature, or want to improve the existing codebase, please submit a pull request.

## License

This project is licensed under the MIT License. Please see the LICENSE file for more information.
