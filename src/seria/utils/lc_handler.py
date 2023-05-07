import os
import re
import logging
import asyncio
import aiohttp
from typing import List
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import Chroma
from langchain import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from .text_preprocessor import TextPreprocessor
from .logger import CustomLogger


logger = CustomLogger(__name__)

class LangChainHandler:
    """
    A class for handling the LangChain library components.
    """
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.text_splitter = TokenTextSplitter(chunk_size=6500)
        self.embedder = OpenAIEmbeddings()
        self.chat = ChatOpenAI(temperature=0.9, model_name='gpt-4')
        # Template building
        self.system_template_str = '''
        SYSTEM: You are a helpful AI question answerer. Please answer questions
        while satisfying the following requirements:
        * You will think carefully about your answers
        * You will only answer questions regarding the game Dungeon Fighter
        Online Global (aka DFOG, DFO, Dungeon Fighter Online)
        * Your answers will be concise
        * Your answers will also incoprorate any relevant context from the text
        provided within the pair of triple backticks
        * If you are unclear about what the user is asking, please ask for 
        clarification
        
        Context:
        ```
        {doc}
        ```
        '''
        self.human_template_str = 'Q: {question}'
        
        # Build
        asyncio.run(self._build_templates())
        asyncio.run(self._get_chroma_db())

    async def _build_templates(self):
        """
        Build a PromptTemplate using the template string.
        """

        sys_template = SystemMessagePromptTemplate.from_template(
            self.system_template_str
        )
        hum_template = HumanMessagePromptTemplate.from_template(
            self.human_template_str
        )
        templates = [sys_template, hum_template]
        self.chat_template = ChatPromptTemplate.from_messages(templates)
    
    @logger.log_execution_time
    async def process_texts(self, texts: List[str]):
        """
        Process texts using the preprocessor and text_splitter.

        Args:
            texts (List[str]): A list of input texts.

        Returns:
            List[str]: A list of processed texts.
        """
        processed_texts = [self.preprocessor.preprocess(text) for text in texts]
        self.docs = self.text_splitter.create_documents(processed_texts)
        self.docs = self.text_splitter.split_documents(self.docs)
        logger.debug('Texts finished processing')

    async def _get_chroma_db(self):
        """
        Create a Chroma database if it does not already exist, or load an
        existing one.
        
        Args:
            texts (List[str]): A list of documents.
            persist_directory (str, optional): The directory to store the
                                               database on disk. Defaults to
                                               'db'.
        Returns:
            Chroma: A Chroma database.
        """
        # Get the absolute path of the directory containing the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        persist_directory = os.path.join(script_dir, '..', '..', '..', 'db')
        self.db = Chroma(persist_directory=persist_directory,
                         embedding_function=self.embedder)
        logger.info('Existing DB loaded')

    @logger.log_execution_time
    async def ask_doc_based_question(self, query: str) -> str:
        """
        Ask a question based on a list of input texts and a query.

        Args:
            texts (List[str]): A list of input texts.
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
        # answer_match = re.search('"(.*)" additional_kwargs', answer.content)
        # answer = answer_match.group(1)
        logger.info(f'LLM answered "{query}": "{answer}"')

        return answer
