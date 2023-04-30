import os
import pandas as pd
from discord.ext import commands
from discord import Intents
from utils.lc_handler import LangChainHandler
from utils.logger import DiscordLogger


# Set up custom logging for the discord.py library
discord_logger = DiscordLogger()

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
    bot.run(os.environ['DISCORD_API_TOKEN'], log_handler=discord_logger.handler)
