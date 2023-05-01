import os
import json
import traceback
from dotenv import load_dotenv

import discord
from discord import Intents, ApplicationContext, Interaction, Embed
from discord.ext import commands
from discord.ui import Modal, View, InputText, button

from utils.lc_handler import LangChainHandler
from utils.logger import CustomLogger


# Load environment variables from .env file
load_dotenv()

# Set-up logger
logger = CustomLogger(__name__)

# Set up the bot
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)

# Get the absolute path of the directory containing the script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct a file path relative to the script's directory
data_file = os.path.join(script_dir, '..', '..', 'data', 'input_blogs.json')
# Load the data from a json file
with open(data_file, 'r') as f:
    data = json.load(f)
# Grab just the blog posts data in a 2d array
posts = [post for post in data['blog'].values()]

class ThumbsDownFeedbackModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label='Feedback? Resource links welcome!', style=discord.InputTextStyle.long))

    async def callback(self, interaction: Interaction):
        embed = Embed(title="Thank you for your feedback!")
        embed.add_field(name="We'll take a look at the following...", value=self.children[0].value)
        await interaction.response.send_message(embeds=[embed])

class FeedbackView(View):
    @button(style=discord.ButtonStyle.green, emoji="👍")
    async def up_button_callback(self, button, interaction: Interaction):
        await interaction.response.send_message("Thank you for the feedback!", ephemeral=True)
        
    @button(style=discord.ButtonStyle.red, emoji="👎")
    async def down_button_callback(self, button, interaction: Interaction):
        await interaction.response.send_modal(ThumbsDownFeedbackModal(title='ThumbsDownFeedbackModal'))

@bot.event
async def on_ready():
    logger.info(f"{bot.user} is ready and online!")

# Ask command
@bot.slash_command(description='Ask Seria a DFO-related question')
async def ask(ctx: ApplicationContext, *, question: str):
    global posts
    
    # Show user bot is thinking
    await ctx.defer(ephemeral=False)
    
    # Create a LangChainHandler instance
    lc = LangChainHandler()
    
    # Get the answer for the query based on the documents
    answer = lc.ask_doc_based_question(posts, question)

    # Send the answer back to the user
    follow_up_text = f'Q: {question}\n\nA: {answer}\n\nPlease give this answer feedback with the buttons below!'
    await ctx.send_followup(follow_up_text, ephemeral=False, view=FeedbackView())
    # await ctx.respond("Was the response helpful?", )

# Ask command error handler
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
    # Logs the error
    logger.error(error, exc_info=True)
    
    # Returns a call to action to user
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

# Run bot
if __name__ == '__main__':
    bot.run(os.environ['DISCORD_API_TOKEN'])
