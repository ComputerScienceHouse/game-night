from pymongo import InsertOne, MongoClient, UpdateOne
from os import environ
from boto3 import client
from re import compile, escape, IGNORECASE, sub
from flask import abort, request, session
from uuid import uuid4
from functools import wraps
from game_night.game import Game

try:
    _game_night = MongoClient('mongodb://{}:{}@{}/{}'.format(environ['MONGODB_USER'], environ['MONGODB_PASSWORD'], environ.get('MONGODB_HOST', 'localhost'), environ['MONGODB_DATABASE'])).game_night
except:
    _game_night = MongoClient().game_night
_api_keys = _game_night.api_keys
_gamemasters = _game_night.gamemasters
_games = _game_night.games

_s3 = client('s3', aws_access_key_id = environ['S3_KEY'], aws_secret_access_key = environ['S3_SECRET'])

def _create_filters():
    filters = {}
    max_players = request.args.get('max_players')
    if max_players:
        try:
            filters['max_players'] = int(max_players)
        except:
            filters['max_players'] = -1
    min_players = request.args.get('min_players')
    if min_players:
        try:
            filters['min_players'] = int(min_players)
        except:
            filters['min_players'] = -1
    name = request.args.get('name')
    if name:
        try:
            filters['name'] = compile(name, IGNORECASE)
        except:
            filters['name'] = compile(escape(name), IGNORECASE)
    owner = request.args.get('owner')
    if owner:
        filters['owner'] = owner
    players = request.args.get('players')
    if players:
        try:
            players = int(players)
            filters['$and'] = [{'min_players': {'$lte': players}}, {'max_players': {'$gte': players}}]
        except:
            filters['$and'] = [{'min_players': {'$lte': -1}}, {'max_players': {'$gte': -1}}]
    submitter = request.args.get('submitter')
    if submitter:
        filters['submitter'] = submitter
    return filters

def delete_game(name):
    if _games.delete_one({'name': name}).deleted_count:
        try:
            id = list(_games.find().sort([('_id', -1)]).limit(10))[-1]['_id']
            _games.update_many({'_id': {'$gte': id}}, {'$set': {'new': True}})
        except:
            pass
        _s3.delete_object(Bucket = environ['S3_BUCKET'], Key = name + '.jpg')
        return True
    return False

def game_exists(name):
    return _games.count({'name': compile(f'^{escape(name)}$', IGNORECASE)})

def generate_api_key(write = False):
    uuid = str(uuid4())
    _api_keys.insert_one({'key': uuid, 'write': write})
    return uuid

def get_count():
    return _games.count(_create_filters())

def get_game(name):
    return _games.find_one({'name': name})

def get_games():
    return _games.find(_create_filters(), {'_id': False}).sort([('sort_name', 1)])

def get_newest_games():
    filters = _create_filters()
    filters['new'] = True
    return _games.find(filters, {'_id' : False}).sort([('_id', -1)])

def get_owners(all = False):
    owners = _games.distinct('owner') if all else _games.distinct('owner', _create_filters())
    owners.sort()
    return owners

def get_players():
    try:
        return _games.aggregate([{'$group': {'_id': False, 'max': {'$max': '$max_players'}, 'min': {'$min': '$min_players'}}}]).next()
    except:
        return None

def get_random_games(sample_size):
    return _games.aggregate([{'$match': _create_filters()}, {'$sample': {'size': sample_size}}, {'$project': {'_id': False}}])

def get_submissions():
    filters = _create_filters()
    filters['submitter'] = session['userinfo']['preferred_username']
    return _games.find(filters, {'_id': False}).sort([('sort_name', 1)])

def _insert_game(game):
    requests = [InsertOne(game)]
    games = list(_games.find().sort([('_id', -1)]).limit(10))
    if len(games) == 10:
        requests.append(UpdateOne({'_id': games[-1]['_id']}, {'$unset': {'new': 1}}))
    _games.bulk_write(requests)

def is_gamemaster():
    return _gamemasters.count({'username': session['userinfo']['preferred_username']})

def _prepare_game(game):
    del game['image']
    game['new'] = True
    game['sort_name'] = sub('(A|(An)|(The)) ', '', game['name'])
    game['submitter'] = session['userinfo']['preferred_username']

def require_gamemaster(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if is_gamemaster():
            return function(*args, **kwargs)
        abort(403)
    return wrapper

def require_read_key(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            if not _api_keys.count({'key': request.headers['Authorization'][7:]}):
                abort(403)
        except:
            abort(403)
        return function(*args, **kwargs)
    return wrapper

def require_write_key(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            if not _api_keys.find_one({'key': request.headers['Authorization'][7:]})['write']:
                abort(403)
        except:
            abort(403)
        return function(*args, **kwargs)
    return wrapper

def submit_game():
    game = Game()
    if game.validate():
        game = game.data
        _s3.upload_fileobj(game['image'], environ['S3_BUCKET'], game['name'] + '.jpg', ExtraArgs = {'ContentType': game['image'].content_type})
        _prepare_game(game)
        _insert_game(game)
        return True
    return game, next(iter(game.errors.values()))[0]