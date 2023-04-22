import os
import openai
import tiktoken
from typing import List
from nltk.tokenize import sent_tokenize, word_tokenize

class TokenCounter:
    """
    A class to count tokens in a given text using tiktoken.
    """

    def count_tokens(self, text: str) -> int:
        """
        Count the tokens in a given text.

        Args:
            text (str): The input text.

        Returns:
            int: The total number of tokens in the text.
        """
        enc = tiktoken.encoding_for_model('gpt-3.5-turbo')
        tokens = enc.encode(text)
        return len(tokens)

class TextSplitter:
    """
    A class to split a long text into smaller chunks based on a token limit.
    """

    def __init__(self, token_counter: TokenCounter, max_tokens: int):
        """
        Initialize the TextSplitter with a token counter and a maximum token limit.

        Args:
            token_counter (TokenCounter): An instance of TokenCounter.
            max_tokens (int): The maximum number of tokens allowed in each chunk.
        """
        self.token_counter = token_counter
        self.max_tokens = max_tokens


    def split_text(self, text: str) -> List[str]:
        """
        Split the input text into smaller chunks based on the token limit.

        Args:
            text (str): The input text.

        Returns:
            List[str]: A list of text chunks.
        """
        # Tokenize the input text into sentences
        sentences = sent_tokenize(text)
        # Initialize an empty list to store the chunks
        chunks = []
        # Initialize an empty string to store the current chunk
        current_chunk = ''

        # Iterate over each sentence in the tokenized sentences
        for sentence in sentences:
            # Count the number of tokens in the sentence
            sentence_tokens = self.token_counter.count_tokens(sentence)

            # Check if the sentence tokens exceed the maximum allowed tokens
            if sentence_tokens > self.max_tokens:
                # Tokenize the input text
                tokens = word_tokenize(sentence)
                # Split tokens into chunks of 500 tokens each
                tokens_per_chunk = 500
                token_chunks = [' '.join(tokens[i:i + tokens_per_chunk]) for i in range(0, len(tokens), tokens_per_chunk)]
                # Add the token chunks to the chunks list
                chunks += token_chunks
                # Move to the next sentence
                continue

            # Count the number of tokens in the current chunk
            current_chunk_tokens = self.token_counter.count_tokens(current_chunk)

            # Check if adding the sentence tokens to the current chunk tokens stays below the max tokens
            if current_chunk_tokens + sentence_tokens < self.max_tokens:
                # Add a space to the current chunk if it is not empty
                if current_chunk:
                    current_chunk += ' '
                # Add the sentence to the current chunk
                current_chunk += sentence
            else:
                # If adding the sentence would exceed the max tokens, store the current chunk and reset it
                chunks.append(current_chunk)
                current_chunk = sentence

        # Append the last remaining chunk, if it exists
        if current_chunk:
            chunks.append(current_chunk)

        # Return the list of chunks
        return chunks



class TextSummarizer:
    """
    A class to summarize a given text chunk using OpenAI's GPT-3.
    """

    def summarize_chunk(self, chunk: str) -> str:
        """
        Summarize a text chunk using GPT-3.

        Args:
            chunk (str): The input text chunk.

        Returns:
            str: The summary of the text chunk.
        """
        prompt = [
            {"role": "system", "content": "You are an AI that summarizes text."},
            {"role": "user", "content": f"Summarize the following: {chunk}"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.5,
        )

        summary = response.choices[0].message.content.strip()
        return summary

class QuestionAsker:
    """
    A class to ask a question based on summarized text using OpenAI's GPT-3.
    """

    def ask_question_based_on_summaries(self, question: str, combined_summary: str) -> str:
        """
        Ask a question based on the combined summary of the input text.

        Args:
            question (str): The question to be asked.
            combined_summary (str): The combined summary of the input text.

        Returns:
            str: The answer to the question.
        """
        prompt = [
            {"role": "system", "content": ("You are an AI that provides answers based on"
                                           " summarized text.")},
            {"role": "user", "content": f"Here's the summary: {combined_summary}"},
            {"role": "user", "content": f"{question}"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )

        answer = response.choices[0].message.content.strip()
        return answer


class TextProcessor:
    """
    A class that processes a long text, summarizes it, and asks a question based on the summaries.
    """

    def __init__(self, text_splitter: TextSplitter, text_summarizer: TextSummarizer, question_asker: QuestionAsker):
        """
        Initialize the TextProcessor with instances of TextSplitter, TextSummarizer, and QuestionAsker.

        Args:
            text_splitter (TextSplitter): An instance of TextSplitter.
            text_summarizer (TextSummarizer): An instance of TextSummarizer.
            question_asker (QuestionAsker): An instance of QuestionAsker.
        """
        self.text_splitter = text_splitter
        self.text_summarizer = text_summarizer
        self.question_asker = question_asker

    def summarize_and_ask_question(self, text: str, question: str) -> str:
        """
        Summarize a long text, combine the summaries, and ask a question based on the combined summary.

        Args:
            text (str): The input text.
            question (str): The question to be asked.

        Returns:
            str: The answer to the question.
        """
        chunks = self.text_splitter.split_text(text)
        summaries = [self.text_summarizer.summarize_chunk(chunk) for chunk in chunks]
        combined_summary = ' '.join(summaries)


        answer = self.question_asker.ask_question_based_on_summaries(question, combined_summary)

        return answer
