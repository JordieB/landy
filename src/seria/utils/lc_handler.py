import os
import asyncio
from typing import List
from uuid import uuid4
from datetime import datetime

from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import Chroma
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from .text_preprocessor import TextPreprocessor
from .logger import CustomLogger
from .qnadatabase import QnADatabase

logger = CustomLogger(__name__)


class LangChainHandler:
    """
    A class for handling the LangChain library components.
    """

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.text_splitter = TokenTextSplitter(chunk_size=6500)
        self.embedder = OpenAIEmbeddings()
        self.chat = ChatOpenAI(temperature=0.9, model_name="gpt-4")

        self.system_template_str = (
            "SYSTEM: You are a helpful AI question answerer. Please answer 
            "questions while satisfying the following requirements:\n"
            "* You will think carefully about your answers\n"
            "* You will only answer questions regarding the game Dungeon "
            "Fighter Online Global (aka DFOG, DFO, Dungeon Fighter Online)\n"
            "* Your answers will be concise\n"
            "* Your will attempt to incorporate any relevant context that is "
            "provided within the pair of triple backticks\n"
            "* If you are unclear about what the user is asking, please ask "
            "for clarification\n\n"
            "Context:\n"
            "```\n"
            "{doc}\n"
            "```\n"
        )
        self.human_template_str = "Q: {question}"

        asyncio.run(self._build_templates())
        asyncio.run(self._get_chroma_db())

        db_uri = os.environ.get("DB_URI")
        self.qna_db = QnADatabase(db_uri)

    async def _build_templates(self):
        """
        Build a PromptTemplate using the template string.
        """
        sys_template = SystemMessagePromptTemplate.from_template(
            self.system_template_str)
        hum_template = HumanMessagePromptTemplate.from_template(
            self.human_template_str)
        self.chat_template = ChatPromptTemplate.from_messages([sys_template,
                                                               hum_template])

    async def _get_chroma_db(self):
        """
        Create a Chroma database if it does not already exist, or load an
        existing one.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        persist_directory = os.path.join(script_dir, "..", "..", "..", "db")
        self.db = Chroma(persist_directory=persist_directory,
                         embedding_function=self.embedder)
        logger.info("Existing DB loaded")

    @logger.log_execution_time
    async def ask_doc_based_question(self, query: str) -> str:
        """
        Ask a question based on a list of input texts
                and a query.

        Args:
            query (str): The query to be asked.

        Returns:
            str: The answer to the query based on the input texts.
        """

        # Query the vecstore (return async iterator to help access list)
        result_docs = await asyncio.to_thread(self.db.similarity_search, query)
        most_relevant_doc = result_docs[0].page_content
        logger.debug('Found most relevant document from vecstore')

        # Format the message
        prompt = self.chat_template.format_prompt(
            question=query,
            doc=most_relevant_doc)
        msgs = prompt.to_messages()
        logger.debug('Asking LLM for doc-based answer...')
        
        # Send prompt
        answer = await asyncio.to_thread(self.chat, msgs)
        answer = answer.content
        logger.info(f'LLM answered "{query}": "{answer}"')
        
        # Collecting question data
        question_id = str(uuid4())
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        current_commit_hash = self._get_current_commit_hash()
        current_commit_timestamp = self._get_current_commit_timestamp()
        question_data = {
            'id': question_id,
            'query': query,
            'answer': answer,
            'timestamp': timestamp,
            'commit_hash': current_commit_hash,
            'commit_timestamp': current_commit_timestamp
        }
        # Send question data to the QnADatabase
        async with self.qna_db:
            await self.qna_db.create_tables()
            await self.qna_db.insert_data('qna_results', question_data)
        logger.debug('Question data inserted into the database')
        
        return answer
