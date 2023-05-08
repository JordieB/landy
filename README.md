# Landy, A DFO Discord Bot

This is a Discord bot that uses LangChain and vector stores to answer questions about the popular video game Dungeon Fighter Online.

## Installation

1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Create a `.env` file in the root directory with your Discord bot token as well as your OpenAI API token to use GPT3 to help answer questions. These tokens should be in the following format `DISCORD_API_TOKEN=your_bot_token_here`.
4. Run the bot using `python bot.py`.

## Testing

This project uses pytest for testing. To run the tests, run the following command in the root directory of the project:

```bash
pytest
```

This will run all the tests in the tests directory and provide output indicating whether they passed or failed. If any tests fail, feel free to file an issue/pull request with details via adding the verbose flag with the following command:

```bash
pytest -vv
```

## Usage
The bot listens for commands that begin with `!`. Currently, the only command that is available is !ask. You can ask the bot a question about Dungeon Fighter Online by typing `/ask <question_here>` in a Discord text channel that the bot has access to.

The bot will search for the answer to your question in a pre-defined set of documents related to Dungeon Fighter Online. It will then use LangChain to generate an answer based on the most relevant document.

## Re-Scrape
There's a spider included that scrapes DFOArchive. Feel free to re-run it to grab any recent blog posts: just make sure to add the new documents to your Chroma DB. You can reference the `src/landy/utils/lc_handler.py` file for a bit more info.

```bash
scrapy runspider -O results.json scraper/spiders/speeder.py 2> errors.log
```

## Contributing
We welcome contributions from the community! If you find a bug, have an idea for a new feature, or want to improve the existing codebase, please submit a pull request.

## License
This project is licensed under the MIT License. Please see the LICENSE file for more information.
