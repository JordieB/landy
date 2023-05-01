import os
import traceback
import pandas as pd
from discord.ext import commands
from discord import Intents
from utils.lc_handler import LangChainHandler
from utils.logger import CustomLogger


# Set up custom logging for the discord.py library
discord_logger = CustomLogger('discord')

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

@ask.error
async def ask_error(ctx, error):
    """
    Error handler for the 'ask' command.

    If an exception occurs during the execution of the 'ask' command,
    this function sends a message to the user with a link to create a new
    issue on GitHub and includes the traceback of the error.

    Args:
        ctx: The context of the command.
        error: The error raised during the execution of the 'ask' command.
    """
    if isinstance(error, commands.CommandInvokeError):
        original_error = error.original
        trace = ''.join(traceback.format_exception(
            type(original_error), original_error, original_error.__traceback__))
        error_message = (
            f"An error occurred while processing your request. "
            f"Please create a new issue at https://github.com/JordieB/seria/issues/new with the following details:\n\n"
            f"```python\n{trace}\n```"
        )
        await ctx.send(error_message)


if __name__ == '__main__':
    bot.run(os.environ['DISCORD_API_TOKEN'],
            log_handler=discord_logger.handler)
