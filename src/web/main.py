"""
    main.py
    Author: Joel Gomez
    Date created: 2017/04/22
    Python Version 3.5.2

    Ghetto RESTful API with Flask for RecipeScouter.com
"""
import requests
import sys
import json
import shelve
from flask import Flask
from flask import request
from flask import Response
from flask import send_from_directory
from flask import url_for
from flask import jsonify
from flask import make_response
from flask import current_app
from flask import abort
from functools import update_wrapper
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

sys.path.insert(0, 'lib')
app = Flask(__name__)

api_url = 'http://food2fork.com/api/search'
api_key = ''
data_file = 'data.db'

try:
    with open('key.json') as key_file:
        api_key = json.load(key_file)['key']
except:
    print('Missing key.json file!\nkey.json:')
    print('{\n  "key" : "api_key_here"\n}')

users = { 
        'user1' : {
            'items': ['eggs', 'milk', 'cheese']
            }
        }

# initialize data file
with shelve.open(data_file) as db:
    try:
        if 'users' in db:
            users = db['users']
    except:
        db['users'] = users

# custom 404 error (resource not found)
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'no recipes found'}), 404)

# custom 400 error (bad request)
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'post attempt with invalid json data'}), 400)

# custom 401 error (unauthorized access)
@app.errorhandler(403)
def not_found(error):
    return make_response(jsonify({'error': 'post attempt with invalid json data'}), 403)

# main app route
@app.route('/')
def index():
    return 'Recipe Scouter'

# retrieve ingredients in inventory
@app.route('/<user>/items', methods=['GET'])
def get_ingredients(user):
    if user in users:
        return jsonify({'items': users[user]['items']})
    else:
        return jsonify({'error':'user not found'}), 404

# add/remote ingredients from inventory
@app.route('/<user>/items', methods=['POST'])
def add_ingredients(user):
    if user in users:
        if not request.json or \
                not 'items' in request.json or \
                not 'action' in request.json or \
                isinstance(request.json['items'], str):
            abort(400)
        post_items = request.json['items']
        if request.json['action'] == 'add':
            for item in post_items:
                if not item in users[user]['items']:
                    users[user]['items'].append(item)
        elif request.json['action'] == 'del':
            for item in post_items:
                if item in users[user]['items']:
                    users[user]['items'].remove(item)
        with shelve.open(data_file) as db:
            db['users'] = users
        return jsonify({'items': users[user]['items']}), 201
    else:
        return jsonify({'error':'user not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
