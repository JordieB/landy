from text_preprocessor import TextPreprocessor
import time

# Check if the script is being run as the main module
if '__main__' == __name__:
    # Retrieve OpenAI API key from secrets
    openai_api_key = dbutils.secrets.get(scope='api_tokens', key='openai')
    os.environ['OPENAI_API_KEY'] = openai_api_key

    # Initialize required components
    preprocessor = TextPreprocessor()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    embeddings = OpenAIEmbeddings()
    llm = OpenAI(temperature=0.9, model_name='text-davinci-003')

    # Create a LangChainHandler instance
    lc = LangChainHandler(preprocessor, text_splitter, embeddings, llm)

    # Extract docs from _sqldf
    posts = [row[0] for row in _sqldf.collect()]

    # Define the query to be asked
    query = 'How should I gear my character after I reach level 110?'

    # Get the answer for the query based on the documents
    answer = lc.ask_doc_based_question(posts, query)

    # Print the answer
    print(answer)
