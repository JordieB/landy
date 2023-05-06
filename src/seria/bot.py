import os
import json
from dotenv import load_dotenv
import discord
from discord import Intents, ApplicationContext, Interaction, Embed
from discord.ext import commands
from discord.ui import Modal, View, InputText, button
from utils.lc_handler import LangChainHandler
from utils.logger import CustomLogger
from datetime import datetime


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
data_file = os.path.join(script_dir, '..', '..', 'data', 'interim',
                         'blogs.json')
# Load the data from a json file
with open(data_file, 'r') as f:
    data = json.load(f)
# Grab just the blog posts data in a 2d array
posts = [post for post in data['blog'].values()]

# Create a LangChainHandler instance
LC = LangChainHandler()

# Set-up feedback modal for downvotes
class ThumbsDownFeedbackModal(Modal):
    """
    A modal that is used to gather feedback from users who have marked the
    answer as "thumbs down."
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label='Feedback? Resource links welcome!',
                                style=discord.InputTextStyle.long))

    async def callback(self, interaction: Interaction):
        """
        The callback function for the ThumbsDownFeedbackModal.

        When a user submits feedback, this function sends a message to the user
        to let them knowc their feedback has been received.

        Args:
            interaction (Interaction): The user interaction that triggered the
                                       modal.
        """
        embed = Embed(title="Thank you for your feedback!")
        embed.add_field(name="We'll take a look at the following...",
                        value=self.children[0].value)
        await interaction.response.send_message(embeds=[embed])

# Set-up button view for upvoting and downvoting
class FeedbackView(View):
    """
    A view that is shown to the user after a query has been answered.

    This view allows the user to provide feedback on the answer they received.
    """
    @button(style=discord.ButtonStyle.green, emoji="👍")
    async def up_button_callback(self,
                                 button: button,
                                 interaction: Interaction):
        """
        The callback function for the "thumbs up" button.

        When a user clicks the "thumbs up" button, this function sends a
        message to the user to let them know their feedback has been received.

        Args:
            button: The button object.
            interaction (Interaction): The user interaction that triggered the
                                       view.
        """
        await interaction.response.send_message("Thank you for the feedback!",
                                                ephemeral=True)
        
    @button(style=discord.ButtonStyle.red, emoji="👎")
    async def down_button_callback(self,
                                   button: button,
                                   interaction: Interaction):
        """
        The callback function for the "thumbs down" button.

        When a user clicks the "thumbs down" button, this function displays the
        ThumbsDownFeedbackModal.

        Args:
            button: The button object.
            interaction (Interaction): The user interaction that triggered the
                                       view.
        """
        await interaction.response.send_modal(
            ThumbsDownFeedbackModal(title='ThumbsDownFeedbackModal'))

# Log when a bot is ready
@bot.event
async def on_ready():
    """
    An event that is triggered when the bot is ready.

    This function logs that the bot is ready and online.
    """
    logger.info(f"{bot.user} is ready and online!")

# Ask command
@bot.slash_command(description='Ask Seria a DFO-related question')
async def ask(ctx: ApplicationContext, *, question: str):
    """
    The function that handles the "ask" command.

    When a user enters a query, this function processes the query and returns an
    answer. It also shows the user a FeedbackView, which allows them to provide
    feedback on the answer they received.

    Args:
        ctx (ApplicationContext): The context of the command.
        question (str): The query that the user entered.
    """
    global posts
    global LC
    
    # Show user bot is thinking
    await ctx.defer(ephemeral=False)
    
    
    # Get the answer for the query based on the documents
    answer = LC.ask_doc_based_question(posts, question)

    # Send the answer back to the user
    follow_up_text = (f'Q: {question}\n\n{answer}\n\nPlease give this answer '
                      f'feedback with the buttons below!')
    await ctx.send_followup(follow_up_text,
                            ephemeral=False,
                            view=FeedbackView(timeout=None))

# Ask command error handler
@ask.error
async def ask_error(ctx, error):
    """
    Error handler for the 'ask' command.

    If an exception occurs during the execution of the 'ask' command,
    this function sends a message to the user with a link to create a new
    issue on GitHub and includes the error message.

    Args:
        ctx: The context of the command.
        error: The error raised during the execution of the 'ask' command.
    """
    # Logs the error
    logger.error(error, exc_info=True)
    
    # Returns a call to action to user
    if isinstance(error, commands.CommandInvokeError):
        now_tsstr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_message = (
            f"An error occurred while processing your question. Please create a"
            f" new issue at https://github.com/JordieB/seria/issues/new with"
            f"the following details:\n\n @ {now_tsstr} I encountered \n\n"
            f"```python\n{error}\n```"
        )
        await ctx.send(error_message)
    else:
        # Log the error message instead of the full traceback
        logger.error(f"An error occurred: {error}")

# Run bot
if __name__ == '__main__':
    bot.run(os.environ['DISCORD_API_TOKEN'])
