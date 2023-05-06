import os
import logging
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
        # default chunk_size = 4k
        self.text_splitter = TokenTextSplitter(chunk_size=31000)  
        self.embedder = OpenAIEmbeddings()
        self.chat = ChatOpenAI(temperature=0, model_name='gpt-4-32k')
        # Template building
        self.system_template_str = '''
        SYSTEM: You are a helpful AI question answerer. You will answer user
        questions about a video game called Dungeon Fighter Online Global (aka
        Dungeon Fighter Online, DFO, DFOG) while satisfying the following
        requirements:
        * You will think carefully about your answers
        * Your answers will be concise
        * Your answers will also incoprorate any relevant context from the text
        provided within the pair of triple backticks.
        * Please do not answer any questions that are not related to DFOG.
        * If you are unclear about what the user is asking, please ask for 
        clarification from the user.
        * If your final answer is longer than a paragraph, please provide a clearly
        labeled summary at the beginning of your answer.
        
        Context:
        ```
        {doc}
        ```
        '''
        self.human_template_str = 'Q: {question}'
        self._build_templates()

    def _build_templates(self) -> None:
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
    def process_texts(self, texts: List[str]) -> List[str]:
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

    def get_chroma_db(self,
                      texts: List[str],
                      persist_directory: str = 'db') -> Chroma:
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
        logger.debug('Attempt to load an existing DB...')
        # If index already exists:
        if os.path.isdir(persist_directory + '/index'):
            logger.info('Chroma DB found...')
            self.db = Chroma(persist_directory=persist_directory,
                             embedding_function=self.embedder)
            logger.debug('Using pre-existing Chroma DB...')
        # Else, make one from texts
        else:
            logger.info('Creating a new persistant DB...')
            self.process_texts(texts)
            self.db = Chroma.from_documents(documents=self.docs,
                                            embedding=self.embedder,
                                            persist_directory=persist_directory)
            self.db.persist()

        logger.info('DB loaded')
        return self.db

    @logger.log_execution_time
    def ask_doc_based_question(self, texts: List[str], query: str) -> str:
        """
        Ask a question based on a list of input texts and a query.

        Args:
            texts (List[str]): A list of input texts.
            query (str): The query to be asked.

        Returns:
            str: The answer to the query based on the input texts.
        """
        logger.info('Starting to answer a question from a user...')
        self.get_chroma_db(texts)  # and make new db if necessary

        result_docs = self.db.similarity_search(query)
        most_relevant_doc = result_docs[0].page_content
        logger.debug('Found most relevant document from vecstore')

        prompt = self.chat_template.format_prompt(
            question=query,
            doc=most_relevant_doc)
        msgs = prompt.to_messages()
        logger.debug('Asking LLM for doc-based answer...')

        doc_based_answer = self.chat(msgs)
        logger.debug('LLM has answered the user\'s question')

        return doc_based_answer
