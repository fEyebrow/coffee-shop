import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def drinks():
    drinks = Drink.query.all()
    shortDrinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': shortDrinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinksDetail(payload):
    drinks = Drink.query.all()
    longDrinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': longDrinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    print('payload', payload)

    body = request.get_json()
    req_title = body.get('title')
    req_recipe = json.dumps(body.get('recipe'))

    drink = Drink(title=req_title, recipe=req_recipe)
    drink.insert()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    if not drink_id:
        abort(404)

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)

    body = request.get_json()
    req_title = body.get('title')
    req_recipe = json.dumps(body.get('recipe'))

    drink.title = req_title
    drink.recipe = req_recipe
    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    if not drink_id:
        abort(404)

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'drinks': drink_id
    })


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_find(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def not_auth(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": error.description
    }), 401

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'bad request.'
    }), 400

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": 'Forbidden.'
    }), 403

@app.errorhandler(AuthError)
def autherror_handler(e):
    return jsonify({
        "message": e.error['description']
    }), e.status_code