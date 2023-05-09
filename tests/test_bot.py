import os
from unittest.mock import AsyncMock, MagicMock

import pytest
import discord
import discord.ext.test as dpytest
import discord.ext.commands as commands

from seria.bot import ask, FeedbackView, ThumbsDownFeedbackModal
from seria.utils.lc_handler import LangChainHandler

LC = LangChainHandler()

# Example question
EXAMPLE_QUESTION = "What is the best class in Dungeon Fighter Online?"

# Mock for Interaction
interaction_mock = MagicMock(spec=discord.Interaction)

# Mock for ApplicationContext
application_context_mock = MagicMock(spec=discord.ApplicationContext)
application_context_mock.user = "TestUser"

# Define bot fixture
@pytest.fixture
async def bot():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = commands.Bot(command_prefix="!", intents=intents)
    b.add_cog(LC)
    await b._async_setup_hook()  # setup the loop
    dpytest.configure(b)
    return b

@pytest.mark.asyncio
async def test_ask_command(bot):
    # Mock the LangChainHandler instance
    LC.ask_doc_based_question = AsyncMock(return_value="Answer")

    # Run the ask command with the test bot
    await dpytest.message(f"/ask {EXAMPLE_QUESTION}")

    # Check if the ask command was executed and if LC.ask_doc_based_question
    # was called
    assert LC.ask_doc_based_question.called
    LC.ask_doc_based_question.assert_called_with(EXAMPLE_QUESTION)

@pytest.mark.asyncio
async def test_feedback_view_buttons(bot):
    feedback_view = FeedbackView()

    # Test up_button_callback
    await feedback_view.up_button_callback(None, interaction_mock)
    interaction_mock.response.send_message.assert_called_with(
        "Glad it was helpful!", ephemeral=False)

    # Test down_button_callback
    await feedback_view.down_button_callback(None, interaction_mock)
    interaction_mock.response.send_modal.assert_called_with(
        ThumbsDownFeedbackModal(title='ThumbsDownFeedbackModal'))

@pytest.mark.asyncio
async def test_thumbs_down_feedback_modal_callback(bot):
    feedback_modal = ThumbsDownFeedbackModal(title="Test Title")
    feedback_modal.children = [MagicMock(value="Feedback message")]

    await feedback_modal.callback(interaction_mock)

    embed = discord.Embed(title="Thank you for your feedback!")
    embed.add_field(name="We'll take a look at the following...",
                    value=feedback_modal.children[0].value)

    interaction_mock.response.send_message.assert_called_with(embeds=[embed])
