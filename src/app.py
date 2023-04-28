import os
from discord.ext import commands
from utils.lc_handler import LangChainHandler

# Set up logging
logger = Logger(__name__).get_logger()

# Retrieve  Discord API token from secrets
discord_api_token = os.environ['DISCORD_API_TOKEN']

# Create a LangChainHandler instance
lc = LangChainHandler()

# Set up the Discord bot
bot = commands.Bot(command_prefix='!')

# Set-up data
df = pd.read_csv('../data/input_blogs.csv')
posts = [row[0] for row in df.values]

@bot.command()
async def ask(ctx, *, question):
    global posts
    global lc

    # Get the answer for the query based on the documents
    answer = lc.ask_doc_based_question(posts, question)

    # Send the answer back to the user
    await ctx.send(answer)


if __name__ == '__main__':
    bot.run(discord_api_token)
