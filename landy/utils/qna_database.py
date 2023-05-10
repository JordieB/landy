import os
import uuid
import asyncio
import subprocess
from datetime import datetime
from typing import Union, Dict, List

import asyncpg

from landy.utils.logger import CustomLogger

logger = CustomLogger(__file__)

class QnADatabase:
    """
    QnADatabase class for managing and interacting with a Q&A database.
    """

    def __init__(self, db_uri: str):
        """
        Initialize the QnADatabase instance with a connection URI.

        Args:
            db_uri (str): The database connection URI.
        """
        self.db_uri = db_uri

    async def connect(self):
        """Connect to the database."""
        logger.debug("Connecting to the database")
        self.connection = await asyncpg.connect(self.db_uri)

    async def disconnect(self):
        """Disconnect from the database."""
        logger.debug("Disconnecting from the database")
        await self.connection.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

    async def _get_current_commit_hash(self):
        """
        Get the current commit hash of the repository.

        Returns:
            str: The current commit hash of the repository.
        """
        return await asyncio.to_thread(
            lambda: subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                cwd=os.path.dirname(os.path.abspath(__file__))).decode().strip()
        )

    async def _get_current_commit_timestamp(self):
        """
        Get the current commit timestamp of the repository.

        Returns:
            str: The current commit timestamp of the repository.
        """
        return await asyncio.to_thread(
            lambda: subprocess.check_output(
                ['git', 'log', '-1', '--format=%cd'],
                cwd=os.path.dirname(os.path.abspath(__file__))).decode().strip()
        )

    async def create_tables(self):
        """
        Create the necessary tables in the database if they don't exist.
        """
        logger.debug("Creating tables if not exists")
        async with self.connection.transaction():
            # Table for storing Q&A results
            await self.connection.execute('''
                CREATE TABLE IF NOT EXISTS qna_results (
                    question_uuid UUID PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    question_timestamp TIMESTAMPTZ NOT NULL,
                    commit_hash VARCHAR NOT NULL,
                    commit_hash_timestamp TIMESTAMPTZ NOT NULL
                );
            ''')

            # Table for storing user feedback on Q&A results
            await self.connection.execute('''
                CREATE TABLE IF NOT EXISTS qna_feedback (
                    feedback_uuid UUID PRIMARY KEY,
                    question_uuid UUID REFERENCES qna_results(question_uuid),
                    feedback_timestamp TIMESTAMPTZ NOT NULL,
                    is_positive BOOLEAN NOT NULL,
                    feedback_commentary TEXT
                );
            ''')

            # Table for storing logs related to Q&A results
            await self.connection.execute('''
                CREATE TABLE IF NOT EXISTS qna_logs (
                    log_uuid UUID PRIMARY KEY,
                    question_uuid UUID REFERENCES qna_results(question_uuid),
                    log_level VARCHAR NOT NULL,
                    log_timestamp TIMESTAMPTZ NOT NULL,
                    log_message TEXT NOT NULL,
                    log_module VARCHAR,
                    log_additional_data JSONB
                );
            ''')

    async def insert_data(self, table_name: str, data: Union[Dict, List[Dict]]):
        """
        Insert data into the specified table.

        Args:
            table_name (str): The name of the table to insert data into.
            data (Union[Dict, List[Dict]]): A dictionary or list of dictionaries
            containing the data to be inserted.
        """
        logger.debug(f"Inserting data into '{table_name}' table")
        if isinstance(data, dict):
            data = [data]  # Convert single row to a list containing one row

        columns = ', '.join(data[0].keys())
        values_placeholder = ', '.join([f'${i+1}' for i in range(len(data[0]))])
        row_placeholder = f'({values_placeholder})'
        all_values_placeholder = ', '.join([row_placeholder] * len(data))
        query = (
            f'INSERT INTO {table_name} ({columns}) VALUES '
            f'{all_values_placeholder};'
        )

        flattened_data = [value for row in data for value in row.values()]
        await self.connection.execute(query, *flattened_data)

    async def delete_data(self, table_name: str, condition: str):
        """
        Delete data from the specified table based on a given condition.

        Args:
            table_name (str): The name of the table to delete data from.
            condition (str): The condition for deleting rows from the table.
        """
        _msg = f"Deleting data from '{table_name}' table where {condition}"
        logger.debug(_msg)
        query = f'DELETE FROM {table_name} WHERE {condition};'
        await self.connection.execute(query)


async def main():
    # Replace with your PostgreSQL connection details
    db_uri = os.environ.get('DB_URI')

    async with QnADatabase(db_uri) as db:
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

        # Delete test row
        condition = f"question_uuid = '{qna_results_data['question_uuid']}'"
        await db.delete_data('qna_results', condition)
        
    logger.info("Database operations completed")


if __name__ == '__main__':
    asyncio.run(main())
