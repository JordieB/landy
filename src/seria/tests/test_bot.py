import os
from unittest.mock import AsyncMock, MagicMock

import pytest
import discord
from discord.ext import test

from bot import bot, LC, ask, FeedbackView, ThumbsDownFeedbackModal

# Set up the test bot
test_bot = test.TestBot(bot)

# Example question
EXAMPLE_QUESTION = "What is the best class in Dungeon Fighter Online?"

# Mock for Interaction
interaction_mock = MagicMock(spec=discord.Interaction)

# Mock for ApplicationContext
application_context_mock = MagicMock(spec=discord.ApplicationContext)
application_context_mock.user = "TestUser"


@pytest.mark.asyncio
async def test_ask_command():
    # Mock the LangChainHandler instance
    LC.ask_doc_based_question = AsyncMock(return_value="Answer")

    # Run the ask command with the test bot
    await test_bot.invoke_command(f"/ask {EXAMPLE_QUESTION}")

    # Check if the ask command was executed and if LC.ask_doc_based_question
    # was called
    assert LC.ask_doc_based_question.called
    LC.ask_doc_based_question.assert_called_with(EXAMPLE_QUESTION)

@pytest.mark.asyncio
async def test_feedback_view_buttons():
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
async def test_thumbs_down_feedback_modal_callback():
    feedback_modal = ThumbsDownFeedbackModal()
    feedback_modal.children = [MagicMock(value="Feedback message")]

    await feedback_modal.callback(interaction_mock)

    embed = discord.Embed(title="Thank you for your feedback!")
    embed.add_field(name="We'll take a look at the following...",
                    value=feedback_modal.children[0].value)

    interaction_mock.response.send_message.assert_called_with(embeds=[embed])
