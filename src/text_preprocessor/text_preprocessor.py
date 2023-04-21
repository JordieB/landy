import os
import re
import string
import pandas as pd
import openai
from bs4 import BeautifulSoup
from functools import reduce
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from unicodedata import normalize

class TextPreprocessor:
    """
    Class for preprocessing text using a sequence of defined text processing steps.
    """
    def __init__(self):
        # Define preprocessing steps
        self.steps = [
            self.convert_to_lowercase,
            self.remove_html_tags,
            self.remove_urls,
            self.norm_unicode_data,
            self.tokenize,
            self.remove_punctuation,
            self.remove_stopwords,
            self.lemmatize,
            self.tokens_to_text,
        ]

    def preprocess(self, text):
        """
        Apply the preprocessing steps to the given text.
        
        Args:
            text (str): The input text to preprocess.

        Returns:
            str: The preprocessed text.
        """
        return reduce(lambda result, step: step(result), self.steps, text)

    @staticmethod
    def convert_to_lowercase(text):
        """
        Convert text to lowercase.

        Args:
            text (str): Input text.

        Returns:
            str: Lowercased text.
        """
        return text.lower()

    @staticmethod
    def remove_html_tags(text):
        """
        Remove HTML tags from text.

        Args:
            text (str): Input text.

        Returns:
            str: Text without HTML tags.
        """
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text()

    @staticmethod
    def remove_urls(text):
        """
        Remove URLs from text.

        Args:
            text (str): Input text.

        Returns:
            str: Text without URLs.
        """
        return re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

    @staticmethod
    def norm_unicode_data(text):
        """
        Normalize unicode data in text.

        Args:
            text (str): Input text.

        Returns:
            str: Text with normalized unicode data.
        """
        return normalize("NFKD", text)

    @staticmethod
    def tokenize(text):
        """
        Tokenize text into words.

        Args:
            text (str): Input text.

        Returns:
            list: A list of tokens.
        """
        return word_tokenize(text)

    @staticmethod
    def remove_punctuation(tokens):
        """
        Remove punctuation from a list of tokens.

        Args:
            tokens (list): A list of tokens.

        Returns:
            list: A list of tokens without punctuation.
        """
        return [token for token in tokens if token not in string.punctuation]

    @staticmethod
    def remove_stopwords(tokens):
        """
        Remove stopwords from a list of tokens.

        Args:
            tokens (list): A list of tokens.

        Returns:
            list: A list of tokens without stopwords.
        """
        stop_words = set(stopwords.words("english"))
        return [token for token in tokens if token not in stop_words]

    @staticmethod
    def lemmatize(tokens):
        """
        Lemmatize tokens in a list of tokens.

        Args:
            tokens (list): A list of tokens.

        Returns:
            list: A list of lemmatized tokens.
        """
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(token) for token in tokens]

    @staticmethod
    def tokens_to_text(tokens):
        """
        Return the tokens back to a single string.

        Args:
            tokens (list): A list of tokens.

        Returns:
            str: The combined tokens as a single string.
        """
        return " ".join(tokens)