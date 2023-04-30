import os
import pandas as pd
from discord.ext import commands
from discord import Intents
from utils.lc_handler import LangChainHandler
from utils.logger import Logger, decolor_discord_logging


# Set up logging
logger = Logger(__name__).get_logger()
decolor_discord_logging()

# Set up the Discord bot
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command()
async def ask(ctx, *, question):
    global posts
    global lc
    
    # Create a LangChainHandler instance
    lc = LangChainHandler()
    # Set-up data
    df = pd.read_csv('seria/data/input_blogs.csv')
    posts = [row[0] for row in df.values]
    # Get the answer for the query based on the documents
    answer = lc.ask_doc_based_question(posts, question)

    # Send the answer back to the user
    await ctx.send(answer)


if __name__ == '__main__':
    bot.run(os.environ['DISCORD_API_TOKEN'])
