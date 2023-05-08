import pytest
from ..utils.lc_handler import LangChainHandler

# Create a pytest fixture for the LangChainHandler instance
@pytest.fixture
async def lang_chain_handler():
    """
    A pytest fixture that creates a LangChainHandler instance for testing.
    """
    handler = LangChainHandler()
    yield handler

# Test if the LangChainHandler builds templates correctly
@pytest.mark.asyncio
async def test_build_templates(lang_chain_handler):
    """
    Test if the LangChainHandler's chat_template is not None and if the
    number of messages in the template is 2.
    """
    assert lang_chain_handler.chat_template is not None
    assert len(lang_chain_handler.chat_template.messages) == 2

# Test if the LangChainHandler can get ChromaDB
@pytest.mark.asyncio
async def test_get_chroma_db(lang_chain_handler):
    """
    Test if the LangChainHandler's db attribute is not None and if the
    db.persist_directory ends with "db".
    """
    assert lang_chain_handler.db is not None
    assert lang_chain_handler.db.persist_directory.endswith("db")

# Test if the LangChainHandler can answer document-based questions
@pytest.mark.asyncio
async def test_ask_doc_based_question(lang_chain_handler):
    """
    Test if the LangChainHandler's ask_doc_based_question function returns a
    non-empty string as an answer to a given query.
    """
    query = "What is the best class in Dungeon Fighter Online?"
    answer = await lang_chain_handler.ask_doc_based_question(query)
    
    assert answer is not None
    assert isinstance(answer, str)
    assert len(answer) > 0
