import os
import uuid
import asyncio
from datetime import datetime
import pytest
from landy.utils.qna_database import QnADatabase

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
                'The meaning of life is subjective and varies among individuals'
                '.'
            ),
            'question_timestamp': datetime.now(),
            'commit_hash': 'a1b2c3d4',
            'commit_hash_timestamp': datetime.now()
        }

        # Insert example data into the qna_results table
        await db.insert_data('qna_results', qna_results_data)

        # Example data for qna_feedback table
        qna_feedback_data = {
            'feedback_uuid': uuid.uuid4(),
            'question_uuid': qna_results_data['question_uuid'],
            'feedback_timestamp': datetime.now(),
            'is_positive': True,
            'feedback_commentary': 'Great answer!'
        }

        # Insert example data into the qna_feedback table
        await db.insert_data('qna_feedback', qna_feedback_data)

        # Fetch the inserted data from qna_feedback
        _query = 'SELECT * FROM qna_feedback WHERE feedback_uuid = $1'
        result = await db.connection.fetchrow(
            _query,
            qna_feedback_data['feedback_uuid']
        )
        assert result['feedback_uuid'] == qna_feedback_data['feedback_uuid']
        assert result['question_uuid'] == qna_feedback_data['question_uuid']
        assert result['is_positive'] == qna_feedback_data['is_positive']
        assert result['feedback_commentary'] \
            == qna_feedback_data['feedback_commentary']

        # Delete test row from qna_feedback
        _arg = f"feedback_uuid = '{qna_feedback_data['feedback_uuid']}'"
        await db.delete_data('qna_feedback', _arg)

        # Check if the row was deleted from qna_feedback
        _query = 'SELECT * FROM qna_feedback WHERE feedback_uuid = $1'
        result = await db.connection.fetchrow(
            _query,
            qna_feedback_data['feedback_uuid']
        )
        assert result == None

        # Delete test row from qna_results
        _arg = f"question_uuid = '{qna_results_data['question_uuid']}'"
        await db.delete_data('qna_results', _arg)

        # Check if the row was deleted from qna_results
        _query = 'SELECT * FROM qna_results WHERE question_uuid = $1'
        result = await db.connection.fetchrow(
            _query,
            qna_results_data['question_uuid']
        )
        assert result == None
