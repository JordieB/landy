import os
import json
import uuid
import traceback
from datetime import datetime
from dotenv import load_dotenv

import discord
from discord import Intents, ApplicationContext, Interaction, Embed
from discord.ext import commands
from discord.ui import Modal, View, InputText, button

from landy.utils.lc_handler import LangChainHandler
from landy.utils.logger import CustomLogger
from landy.utils.qna_database import QnADatabase


# Load environment variables from .env file
load_dotenv()

# Set-up logger
logger = CustomLogger(__name__)

# Set up the bot
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)

# Create a LangChainHandler instance
LC = LangChainHandler()

# Create QnADatabase instance
DB_URI = os.environ.get('DB_URI')

# Set-up feedback modal for downvotes
class ThumbsDownFeedbackModal(Modal):
    """
    A modal that is used to gather feedback from users who have marked the
    answer as "thumbs down."
    """
    def __init__(self, question_uuid, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.question_uuid = question_uuid
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
        # Record feedback in DB
        feedback_data = {
            'feedback_uuid': str(uuid.uuid4()),
            'question_uuid': self.question_uuid,
            'feedback_timestamp': datetime.utcnow(),
            'is_positive': False,
            'feedback_commentary': self.children[0].value
        }
        async with QnADatabase(DB_URI) as db:
            await db.insert_data('qna_feedback', feedback_data)
        logger.info(f'Question {self.question_uuid} provided negative feedback')
        
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
    def __init__(self, question_uuid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question_uuid = question_uuid

    @button(style=discord.ButtonStyle.green, emoji="👍")
    async def up_button_callback(self, button, interaction: Interaction):
        """
        The callback function for the "thumbs up" button.

        When a user clicks the "thumbs up" button, this function sends a
        message to the user to let them know their feedback has been received.

        Args:
            button: The button object.
            interaction (Interaction): The user interaction that triggered the
                                       view.
        """
        # Record feedback in DB
        feedback_data = {
            'feedback_uuid': str(uuid.uuid4()),
            'question_uuid': self.question_uuid,
            'feedback_timestamp': datetime.utcnow(),
            'is_positive': True,
            'feedback_commentary': None
        }
        async with QnADatabase(DB_URI) as db:
            await db.insert_data('qna_feedback', feedback_data)
        logger.info(f'Question {self.question_uuid} provided positive feedback')
        
        # Thank user for feedback
        await interaction.response.send_message(
            "Thanks, glad it was helpful!",
            ephemeral=False
        )
        
    @button(style=discord.ButtonStyle.red, emoji="👎")
    async def down_button_callback(self,
                                   button,
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
            ThumbsDownFeedbackModal(title='ThumbsDownFeedbackModal',
                                    question_uuid=self.question_uuid))

# Log when a bot is ready
@bot.event
async def on_ready():
    """
    An event that is triggered when the bot is ready.

    This function logs that the bot is ready and online.
    """
    logger.info(f"{bot.user} is ready and online!")

# Ask command
@bot.slash_command(description='Ask Landy a DFO-related question')
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
    global LC
    
    # Show user bot is thinking
    await ctx.defer(ephemeral=False)
    
    # Get the answer for the query based on the documents
    
    question_uuid = str(uuid.uuid4())
    logger.info((
        f'Starting to answer question {question_uuid} from {ctx.user}: '
        f'"{question}"'
    ))
    answer = await LC.ask_doc_based_question(question, question_uuid)

    # Send the answer back to the user
    follow_up_text = (f'> Q: {question}\n\nAnswer below:\n\n{answer}\n\n'
                      f'*Please give this answer feedback with the buttons'
                      f' below!*')
    await ctx.send_followup(follow_up_text,
                            ephemeral=False,
                            view=FeedbackView(question_uuid=question_uuid,
                                              timeout=None))

# Ask command error handler
@ask.error
async def ask_error(ctx: discord.ApplicationContext, error):
    """
    Error handler for the 'ask' command.

    If an exception occurs during the execution of the 'ask' command,
    this function sends a message to the user with a link to create a new
    issue on GitHub and includes the error message.

    Args:
        ctx: The context of the command.
        error: The error raised during the execution of the 'ask' command.
    """
    # Formats error
    full_error = traceback.format_exception(type(error), error,
                                            error.__traceback__)
    formatted_error_str = ''.join(full_error)
    # Logs the error
    logger.error(formatted_error_str)

    # Catch the discord.errors.NotFound exception and return/stop infinite defer
    if isinstance(error, discord.errors.NotFound):
        return

    # Returns a call to action to user
    now_tsstr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_message = (
        f"You broke it >:[ good job.\n\nPlease create a new issue at "
        f"https://github.com/JordieB/seria/issues/new with the following detail"
        f"s:\n\n```The '{ctx.command.qualified_name}' command with args "
        f"{ctx.selected_options} @ {now_tsstr} gave {ctx.user} the following "
        f"error:\n\n{error}```"
    )
    await ctx.send_followup(error_message)

# Run bot
if __name__ == '__main__':
    bot.run(os.environ['DISCORD_API_TOKEN'])
