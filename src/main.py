from text_preprocessor import TextPreprocessor
from pandas import 

if __name__ == '__main__':
    openai.api_key = os.environ['OPENAPI_API_KEY']

    # Load data and preprocess text
    df = pd.read_csv('./data/input_blogs.csv')
    preprocessor = TextPreprocessor()
    df.loc[:, "text"] = df.loc[:, "blog"].apply(preprocessor.preprocess)

    long_text = df['text'][35]
    max_tokens_per_chunk = 3000
    question = "Can you send me high-quality question-answer pairs based on the text?"

    token_counter = TokenCounter()
    text_splitter = TextSplitter(token_counter, max_tokens_per_chunk)
    text_summarizer = TextSummarizer()
    question_asker = QuestionAsker()

    text_processor = TextProcessor(text_splitter, text_summarizer, question_asker)
    answer = text_processor.summarize_and_ask_question(long_text, question)

    print(answer)