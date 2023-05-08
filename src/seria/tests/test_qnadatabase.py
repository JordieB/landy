import os
import uuid
import asyncio
from datetime import datetime
import pytest
from qna_database import QnADatabase

# Replace with your PostgreSQL connection details
DB_URI = os.environ.get('DB_URI')

@pytest.mark.asyncio
async def test_qna_database():
    async with QnADatabase(DB_URI) as db:
        # Create necessary tables
        await db.create_tables()

        # Example data for insertion
        qna_results_data = {
            'question_uuid': uuid.uuid4(),
            'question': 'What is the meaning of life?',
            'answer': (
                'The meaning of life is subjective and varies among individual'
                's.'
            ),
            'question_timestamp': datetime.now(),
            'commit_hash': 'a1b2c3d4',
            'commit_hash_timestamp': datetime.now()
        }

        # Insert example data into the qna_results table
        await db.insert_data('qna_results', qna_results_data)

        # Fetch the inserted data
        _query ='SELECT * FROM qna_results WHERE question_uuid = $1'
        result = await db.connection.fetchrow(_query,
                                              qna_results_data['question_uuid'])
        assert result['question_uuid'] == qna_results_data['question_uuid']
        assert result['question'] == qna_results_data['question']
        assert result['answer'] == qna_results_data['answer']

        # Delete test row
        _arg = f"question_uuid = '{qna_results_data['question_uuid']}'"
        await db.delete_data('qna_results', _arg)

        # Check if the row was deleted
        _query = 'SELECT * FROM qna_results WHERE question_uuid = $1'
        result = await db.connection.fetchrow(_query,
                                              qna_results_data['question_uuid'])
        assert result == None
