import sys
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def get_categories():
    categories = Category.query.all()
    dict_categories = {}
    for category in categories:
        dict_categories[category.id] = category.type

    # abort if no categories
    if (len(dict_categories) == 0):
        abort(404)

    return dict_categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    # -----------------------------------------------------------------------------
    # ---------------- GET CATEGORIES ---------------------------------------------
    # -----------------------------------------------------------------------------

    @app.route("/categories")
    def retrieve_categories():
        dict_categories = get_categories()

        return jsonify({
            "success": True,
            "categories": dict_categories
        })

    # -----------------------------------------------------------------------------
    # ---------------- GET QUESTIONS ----------------------------------------------
    # -----------------------------------------------------------------------------

    @ app.route("/questions")
    def retrieve_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            dict_categories = get_categories()

            if len(current_questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories': dict_categories,
                'current_category': None,
            })
        except:
            print(sys.exc_info())
            db.session.rollback()
            abort(422)

        finally:
            db.session.close()

    # -----------------------------------------------------------------------------
    # ---------------- DELETE A QUESTION ------------------------------------------
    # -----------------------------------------------------------------------------

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except:
            abort(422)

    # -----------------------------------------------------------------------------
    # ---------------- CREATE A NEW QUESTION --------------------------------------
    # -----------------------------------------------------------------------------

    @app.route('/questions', methods=['POST'])
    def add_question():
        try:
            body = request.get_json()

            if not ('question' in body and 'answer' in body and
                    'difficulty' in body and 'category' in body):
                abort(404)

            question = body.get('question', None)
            answer = body.get('answer', None)
            difficulty = body.get('difficulty', None)
            category = body.get('category', None)
            new_question = Question(
                question=question, answer=answer, category=category, difficulty=difficulty)
            new_question.insert()

            # get all questions and paginate
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': new_question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except BaseException:
            abort(422)

    # -----------------------------------------------------------------------------
    # ---------------- SEARCH QUESTIONS -------------------------------------------
    # -----------------------------------------------------------------------------

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        try:
            if search_term:
                selection = Question.query.filter(Question.question.ilike
                                                  (f'%{search_term}%')).all()
            else:
                abort(400)

            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions':  current_questions,
                'total_questions': len(selection),
                'current_category': None
            })
        except:
            abort(422)

    # -----------------------------------------------------------------------------
    # ---------------- GET A QUESTION FROM A CATEGORY -----------------------------
    # -----------------------------------------------------------------------------

    @ app.route("/categories/<int:category_id>/questions")
    def get_questions_by_categories(category_id):
        category = Category.query.filter_by(id=category_id).one_or_none()
        try:
            # get questions with category_id
            selection = Question.query.order_by(
                Question.id).filter_by(category=category_id).all()
            current_questions = paginate_questions(request, selection)

            if len(current_questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'current_category': category.type,
            })
        except:
            print(sys.exc_info())
            db.session.rollback()
            abort(500)

        finally:
            db.session.close()

    # -----------------------------------------------------------------------------
    # ---------------- GET QUESTIONS TO PLAY QUIZ ---------------------------------
    # -----------------------------------------------------------------------------

    @app.route("/quizzes", methods=['POST'])
    def generate_quiz_question():
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        try:
            if quiz_category:
                if quiz_category['id'] == 0:  # when ALL categories are selected
                    selection = Question.query.filter(
                        Question.id.notin_(previous_questions)).all()
                else:
                    selection = Question.query.filter_by(category=quiz_category['id']).filter(
                        Question.id.notin_(previous_questions)).all()

                length_question = len(selection)
                if length_question > 0:
                    result = {
                        "success": True,
                        "question": Question.format(
                            selection[random.randrange(
                                0,
                                length_question
                            )]
                        )
                    }
                else:
                    result = {
                        "success": True,
                        "question": None
                    }
                return jsonify(result)
        except:
            print(sys.exc_info())
            db.session.rollback()
            abort(404)
        finally:
            db.session.close()

    # -----------------------------------------------------------------------------
    # ---------------- ERROR HANDLERS ---------------------------------------------
    # -----------------------------------------------------------------------------

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}), 404)

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422,
                    "message": "unprocessable"}), 422
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify({"success": False, "error": 400, "message": "bad request"}), 400)

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"success": False, 'error': 500, "message": "Internal server error"}), 500

    return app
