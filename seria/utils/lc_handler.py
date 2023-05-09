import os
import asyncio
from typing import List
from uuid import uuid4
from datetime import datetime

# Importing necessary modules from the langchain and seria libraries.
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import Chroma
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from seria.utils.logger import CustomLogger
from seria.utils.qna_database import QnADatabase

# Instantiating the logger
logger = CustomLogger(__name__)


class LangChainHandler:
    """
    A class for handling the LangChain library components.
    """

    def __init__(self):
        # Creating instances of TokenTextSplitter, OpenAIEmbeddings and
        # ChatOpenAI
        self.text_splitter = TokenTextSplitter(chunk_size=6500)
        self.embedder = OpenAIEmbeddings()
        self.chat = ChatOpenAI(temperature=0.9, model_name="gpt-4")

        # Define the system and human message templates
        self.system_template_str = (
            "SYSTEM: You are a helpful AI question answerer. Please answer "
            ...
            "{doc}\n"
            "```\n"
        )
        self.human_template_str = "Q: {question}"

        # Building the chat template and getting the Chroma DB
        asyncio.run(self._build_templates())
        asyncio.run(self._get_chroma_db())

        # Instantiate the QnADatabase with the environment variable 'DB_URI'
        self.qna_db = QnADatabase(os.environ.get("DB_URI"))

    async def _build_templates(self):
        """
        Build a PromptTemplate using the template string.
        """
        # Creating message templates from the system and human template strings
        sys_template = SystemMessagePromptTemplate.from_template(
            self.system_template_str)
        hum_template = HumanMessagePromptTemplate.from_template(
            self.human_template_str)
        # Creating a chat template from the system and human message templates
        self.chat_template = ChatPromptTemplate.from_messages([sys_template,
                                                               hum_template])

    async def _get_chroma_db(self):
        """
        Create a Chroma database if it does not already exist, or load an
        existing one.
        """
        # Constructing the directory path for the Chroma DB
        script_dir = os.path.dirname(os.path.abspath(__file__))
        persist_directory = os.path.join(script_dir, "..", "..", "..", "db")
        # Creating a Chroma instance with the directory and the embedder
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

        # Querying the Chroma DB for documents similar to the query
        result_docs = await asyncio.to_thread(self.db.similarity_search, query)
        # Getting the most relevant document
        most_relevant_doc = result_docs[0].page_content
        logger.debug('Found most relevant document from vecstore')

        # Formatting the chat prompt with the question and the most relevant
        # document
        prompt = self.chat_template.format_prompt(
            question=query,
            doc=most_relevant_doc)
        msgs = prompt.to_messages()
        logger.debug('Asking LLM for doc-based answer...')
        
        # Sending the prompt to the chat model and getting the answer
        answer = await asyncio.to_thread(self.chat, msgs)
        answer = answer.content
        logger.info(f'LLM answered "{query}": "{answer}"')
        
        # Collecting question data, including the ID, timestamp, commit hash, 
        # and commit timestamp
        question_id = str(uuid4())
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        current_commit_hash = self.qna_db._get_current_commit_hash()
        current_commit_timestamp = self.qna_db._get_current_commit_timestamp()
        question_data = {
            'id': question_id,
            'query': query,
            'answer': answer,
            'timestamp': timestamp,
            'commit_hash': current_commit_hash,
            'commit_timestamp': current_commit_timestamp
        }
        # Inserting the question data into the QnADatabase
        async with self.qna_db:
            await self.qna_db.create_tables()
            await self.qna_db.insert_data('qna_results', question_data)
        logger.debug('Question data inserted into the database')
        
        # Returning the answer
        return answer
