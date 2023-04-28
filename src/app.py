import discord
from dotenv import load_dotenv
import os
from lang_chain_handler import LangChainHandler
from text_preprocessor import TextPreprocessor
from utils.discord_helper import DiscordHelper
from utils.logger import Logger

load_dotenv()  # Load environment variables from .env file

# Set up logging
logger = Logger(__name__).get_logger()

# Set up Discord client
client = discord.Client()

# Set up TextPreprocessor
preprocessor = TextPreprocessor()

# Set up LangChainHandler
lc_handler = LangChainHandler(preprocessor)

# Set up DiscordHelper
discord_helper = DiscordHelper(client, lc_handler)


@client.event
async def on_ready():
    logger.info(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Pass message to DiscordHelper to handle
    response = await discord_helper.handle_message(message)

    if response:
        await message.channel.send(response)


if __name__ == '__main__':
    client.run(os.getenv('DISCORD_TOKEN'))
