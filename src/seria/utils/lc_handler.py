import os
import logging
from typing import List
from langchain.llms import OpenAI
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import Chroma
from langchain import PromptTemplate
from .text_preprocessor import TextPreprocessor
from .logger import CustomLogger


logger = CustomLogger('LangChainHandler')
ddb_logger = logging.getLogger('langchain')
ddb_logger = logging.getLogger('chromadb')
ddb_logger = logging.getLogger('duckdb')
ddb_logger.setLevel(logging.ERROR)

class LangChainHandler:
    """
    A class for handling the LangChain library components.
    """
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        # default chunk_size = 4k
        self.text_splitter = TokenTextSplitter(chunk_size=3000)  
        self.embedder = OpenAIEmbeddings()
        self.llm = OpenAI(temperature=0.9,
                          model_name='text-davinci-003')
        self.template = ('===\nContext: {doc}\n===\n\nSYSTEM: This question '
                         'will be about the game Dungeon Fighter Online, also '
                         'known as DFO or DFOG or Dungeon Fighter Online Global'
                         '. Please use this information and the context above '
                         'to answer the following question.\n\nQ: {question}\n'
                         '\nA: ')
    
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
        return self.docs

    def create_chroma_db(self,
                         docs: List[str],
                         persist_directory: str = 'db') -> Chroma:
        """
        Create a Chroma database if it does not already exist, or load an
        existing one.
        
        Args:
            docs (List[str]): A list of documents.
            persist_directory (str, optional): The directory to store the
                                               database on disk. Defaults to
                                               'db'.
        Returns:
            Chroma: A Chroma database.
        """
        # logger.log('Attempt to load an existing DB...')
        # If index already exists:
        if os.path.isdir(persist_directory + '/index'):
            logger.debug('Chroma DB found...')
            self.db = Chroma(persist_directory=persist_directory,
                             embedding_function=self.embedder)
            logger.debug('Using pre-existing Chroma DB')
        # Else, make one from documents
        else:
            self.db = Chroma.from_documents(documents=docs,
                                            embedding=self.embedder,
                                            persist_directory=persist_directory)
            self.db.persist()

        return self.db

    def _build_template(self) -> None:
        """
        Build a PromptTemplate using the template string.
        """
        self.template = PromptTemplate(template=self.template,
                                       input_variables=['question', 'doc'])

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
        self.process_texts(texts)
        self.create_chroma_db(self.docs)
        self._build_template()
        result_docs = self.db.similarity_search(query)
        logger.debug('Found most relevant document from vecstore')
        most_relevant_doc = result_docs[0].page_content
        prompt = self.template.format(question=query, doc=most_relevant_doc)
        logger.debug('Asking LLM for doc-based answer...')
        doc_based_answer = self.llm(prompt)
        logger.debug('LLM has answered the user\'s question')

        return doc_based_answer

if __name__ == '__main__':
    lc_handler = LangChainHandler()
    