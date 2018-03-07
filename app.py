from flask import Flask, jsonify, request
from pymongo import MongoClient
from re import compile, IGNORECASE
from random import choice

app = Flask(__name__)
app.url_map.strict_slashes = False

games = MongoClient().game_night.games

@app.route('/api', methods = ['GET'])
def all():
    return jsonify(list(get_games()))

def get_games():
    filters = {}
    try:
        filters['name'] = compile(request.args.get('name'), IGNORECASE)
    except:
        pass
    try:
        players = int(request.args.get('players'))
        filters['$where'] = '{0} >= this.min_players && {0} <= this.max_players'.format(players)
    except:
        pass
    return games.find(filters, {'_id': False}).sort([('sortName', 1)])

@app.route('/api/random', methods = ['GET'])
def random():
    return jsonify(choice(list(get_games())))
