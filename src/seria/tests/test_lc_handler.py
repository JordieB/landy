import nose.tools as nt
from ..utils.lc_handler import LangChainHandler

def test_ask_doc_based_question_runs_without_error():
    """
    Test whether the ask_doc_based_question function runs without erroring out.
    """
    lc_handler = LangChainHandler()
    texts = ['Some example text.', 'Some more example text.']
    query = 'What is an example?'
    try:
        result = lc_handler.ask_doc_based_question(texts, query)
    except Exception as e:
        # If there was a Python exception, print it and fail the test
        print(e)
        nt.assert_false(True)