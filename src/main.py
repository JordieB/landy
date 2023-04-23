from text_preprocessor import TextPreprocessor
import time

if __name__ == '__main__':
    openai.api_key = os.environ['OPENAPI_API_KEY']

    # Load data and preprocess text
    df = pd.read_csv('/Workspace/Repos/jordie.belle@proton.me/dfo_chatbot/data/input_blogs.csv')
    preprocessor = TextPreprocessor()
    df.loc[:, "text"] = df.loc[:, "blog"].apply(preprocessor.preprocess)

    # long_text = df['text'][35]
    max_tokens_per_chunk = 3000
    question = "Can you send me high-quality question-answer pairs based on the text?"

    token_counter = TokenCounter()
    text_splitter = TextSplitter(token_counter, max_tokens_per_chunk)
    text_summarizer = TextSummarizer()
    question_asker = QuestionAsker()

    # answers = []
    df_rows = df.loc[231:,:].iterrows()
    retry_delay = 5 * 60
    max_retries = 5

    for index, row in df_rows:
        text_processor = TextProcessor(text_splitter, text_summarizer, question_asker)
        try:
            answer = text_processor.summarize_and_ask_question(row['text'], question)
            answers.append(answer)
        except Exception as e:
            error_message = str(e)
            if "That model is currently overloaded with other requests" in error_message:
                # Retry after waiting some time
                for attempt in range(1, max_retries + 1):
                    time.sleep(retry_delay)
                    try:
                        answer = text_processor.summarize_and_ask_question(row['text'], question)
                        answers.append(answer)
                    except Exception as e:
                        raise Exception(f'At {index}, {e}')
            else:
                raise Exception(f'At {index}, {e}')
