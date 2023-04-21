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

class GPT3:
    """
    Class for interacting with GPT-3 to generate and extract question and answer pairs.
    """

    @staticmethod
    def extract_qna(response_text):
        """
        Extract question and answer pairs from the response text.

        Args:
            response_text (str): The text generated by GPT-3.

        Returns:
            list: A list of dictionaries containing question and answer pairs.
        """
        # Compile regex patterns to match questions and answers in the text
        question_pattern = re.compile(r"Q\d+:.*?(?=\nA\d+:|$)", re.DOTALL)
        answer_pattern = re.compile(r"A\d+:.*?(?=\nQ\d+:|$)", re.DOTALL)

        # Find all questions and answers using the regex patterns
        questions = question_pattern.findall(response_text)
        answers = answer_pattern.findall(response_text)

        # Create a list of dictionaries containing question and answer pairs
        qna_pairs = [
            {
                "question": question[4:].replace("\n", " ").strip(),
                "answer": answer[4:].replace("\n", " ").strip(),
            }
            for question, answer in zip(questions, answers)
        ]

        return qna_pairs

    @staticmethod
    def complete_prompt(prompt, output_csv="qna_pairs.csv"):
        """
        Generate a GPT-3 response based on the given prompt and extract question and answer pairs.

        Args:
            prompt (str): The input prompt for GPT-3.
            output_csv (str, optional): The filename to save the extracted question and answer pairs. Defaults to "qna_pairs.csv".

        Returns:
            pd.DataFrame: A DataFrame containing the extracted question and answer pairs.
        """
        try:
            # Create a GPT-3 completion request with the specified parameters
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.7,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )

            # Extract the generated text from the GPT-3 response
            generated_text = response["choices"][0]["text"]

            # Extract question and answer pairs from the generated text
            qna_pairs = GPT3.extract_qna(generated_text)

            # Convert the extracted question and answer pairs to a DataFrame
            df = pd.DataFrame(qna_pairs)

            # Save the question and answer pairs to the specified CSV file
            if not os.path.exists(output_csv):
                df.to_csv(output_csv, mode="w", index=False, header=True)
            else:
                df.to_csv(output_csv, mode="a", index=False, header=False)

            return df

        except Exception as e:
            print(f"Error generating response and extracting QnA pairs: {e}")
            return pd.DataFrame()
