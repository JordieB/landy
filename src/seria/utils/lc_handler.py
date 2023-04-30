import os
from typing import List
from langchain.llms import OpenAI
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import Chroma
from langchain import PromptTemplate
from .text_preprocessor import TextPreprocessor

class LangChainHandler:
    """
    A class for handling the LangChain library components.
    """
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.text_splitter = TokenTextSplitter()
        self.embedder = OpenAIEmbeddings()
        self.llm = OpenAI(temperature=0.9,
                          model_name='text-davinci-003')
        self.template = '===\nContext: {doc}\n===\n\nQ: {question}\nA:'
        
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
        return self.docs

    def create_chroma_db(self, docs: List[Document], embeddings) -> Chroma:
        """
        Create a Chroma database from the list of Document objects and embeddings.

        Args:
            docs (List[Document]): A list of Document objects.
            embeddings: Embeddings to be used in Chroma.

        Returns:
            Chroma: A Chroma database.
        """
        self.db = Chroma.from_documents(docs, embeddings)
        return self.db

    def _build_template(self) -> None:
        """
        Build a PromptTemplate using the template string.
        """
        self.template = PromptTemplate(template=self.template,
                                       input_variables=['question', 'doc'])

    def ask_doc_based_question(self, texts: List[str], query: str) -> str:
        """
        Ask a question based on a list of input texts and a query.

        Args:
            texts (List[str]): A list of input texts.
            query (str): The query to be asked.

        Returns:
            str: The answer to the query based on the input texts.
        """
        self.process_texts(texts)
        self.create_chroma_db(self.docs, self.embedder)
        self._build_template()
        result_docs = self.db.similarity_search(query)
        most_relevant_doc = result_docs[0].page_content
        prompt = self.template.format(question=query, doc=most_relevant_doc)
        doc_based_answer = self.llm(prompt)

        return doc_based_answer

if __name__ == '__main__':
    lc_handler = LangChainHandler()
    