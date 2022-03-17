import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from dotenv import load_dotenv

load_dotenv()

database_user = os.getenv('DB_USER')
database_passwrd = os.getenv('DB_PASSWORD')
database_host = 'localhost:5432'


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            database_user, database_passwrd, database_host, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_paginate_questions(self):
        """Tests question pagination success"""
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

    def test_delete_question(self):
        res = self.client().delete('/questions/23')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_delete_question(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_search_questions(self):
        res = self.client().post("/questions/search",
                                 json={"searchTerm": "organ"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_insert_question(self):
        new_question = {
            'question': 'Test question',
            'answer': 'Test answer',
            'difficulty': 1,
            'category': 1
        }
        questions_before = len(Question.query.all())
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)
        questions_after = len(Question.query.all())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        # compare length before and after insertion
        self.assertEqual(questions_after, questions_before + 1)


# -------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

    def test_422_request_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_422_question_not_found(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    def test_500_search_question_no_searchterm(self):
        res = self.client().post("/questions/search")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], "Internal server error")

    def test_500_search_question(self):
        res = self.client().post("/questions/search?page=10")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], "Internal server error")

    def test_422_add_new_question(self):
        post_data = {
            'question': 'Test question',
            'answer': 'Test answer',
            'category': 5
        }
        res = self.client().post('/questions', json=post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_422_add_new_question(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
