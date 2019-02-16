from re import compile, escape, I
from pymongo import InsertOne, MongoClient, UpdateOne
from os import environ
from uuid import uuid4
from functools import wraps

_sub_regex = compile('(A|(An)|(The)) ')

try:
    _database = MongoClient(
        f'mongodb://{environ["MONGODB_USER"]}:{environ["MONGODB_PASSWORD"]}@{environ.get("MONGODB_HOST", "localhost")}/{environ["MONGODB_DATABASE"]}',
        ssl = 'MONGODB_SSL' in environ
    )[environ['MONGODB_DATABASE']]
except:
    _database = MongoClient()['MONGODB_DATABASE']
_api_keys = _database.api_keys
_gamemasters = _database.gamemasters
_games = _database.games

def api_key_exists(key):
    return _api_keys.count({'key': key})

def _create_filters(arguments, **kwargs):
    filters = {}
    max_players = arguments.get('max_players')
    if max_players:
        try:
            filters['max_players'] = int(max_players)
        except:
            filters['max_players'] = -1
    min_players = arguments.get('min_players')
    if min_players:
        try:
            filters['min_players'] = int(min_players)
        except:
            filters['min_players'] = -1
    name = arguments.get('name')
    if name:
        try:
            filters['name'] = compile(name, I)
        except:
            filters['name'] = compile(escape(name), I)
    owner = arguments.get('owner')
    if owner:
        filters['owner'] = owner
    players = arguments.get('players')
    if players:
        try:
            players = int(players)
            filters['$and'] = [
                {'min_players': {'$lte': players}},
                {'max_players': {'$gte': players}}
            ]
        except:
            filters['$and'] = [
                {'min_players': {'$lte': -1}},
                {'max_players': {'$gte': -1}}
            ]
    submitter = arguments.get('submitter')
    if submitter:
        filters['submitter'] = submitter
    return dict(filters, **kwargs)

def _create_sort(arguments, **kwargs):
    try:
        return dict(
            {arguments['sort']: -1 if 'descending' in arguments else 1},
            **kwargs
        )
    except:
        return kwargs

def delete_game(name):
    if not _games.delete_one({'name': name}).deleted_count:
        return False
    try:
        id = list(_games.find().sort([('_id', -1)]).limit(10))[-1]['_id']
        _games.update_many({'_id': {'$gte': id}}, {'$set': {'new': True}})
    except:
        pass
    return True

def game_exists(name):
    return _games.count({'name': compile(f'^{escape(name)}$', I)})

def generate_api_key():
    uuid = str(uuid4())
    _api_keys.insert_one({'key': uuid})
    return uuid

def get_api_keys():
    return list(_api_keys.find())

def get_count(arguments):
    return _games.count(_create_filters(arguments))

def get_game(name):
    return _games.find_one({'name': name})

def get_game_names():
    return (game['name'] for game in _games.find({}, {
        '_id': False, 'name': True
    }).sort([('sort_name', 1)]))

def get_games(arguments):
    return _games.aggregate([
        {'$match': _create_filters(arguments)},
        {'$sort': _create_sort(arguments, sort_name = 1)},
        {'$project': {'_id': False}}
    ])

def get_newest_games(arguments):
    return _games.aggregate([
        {'$match': _create_filters(arguments, new = True)},
        {'$sort': _create_sort(arguments, _id = -1)},
        {'$project': {'_id': False}}
    ])

def get_owners(arguments = None):
    aggregation = [
        {'$group': {'_id': '$owner'}},
        {'$sort': {'_id': 1}},
    ]
    if arguments:
        aggregation = {'$match': _create_filters(arguments)} + aggregation
    return (game['_id'] for game in _games.aggregate(aggregation))

def get_players():
    try:
        return next(_games.aggregate([
            {'$group': {'_id': False, 'max': {'$max': '$max_players'}, 'min': {'$min': '$min_players'}}}
        ]))
    except:
        return None

def get_random_games(arguments, sample_size):
    return _games.aggregate([
        {'$match': _create_filters(arguments)},
        {'$sample': {'size': sample_size}},
        {'$project': {'_id': False}}
    ])

def get_submissions(arguments, submitter):
    return _games.aggregate([
        {'$match': _create_filters(arguments, submitter = submitter)},
        {'$sort': _create_sort(arguments, sort_name = 1)},
        {'$project': {'_id': False}}
    ])

def insert_game(game, submitter):
    if not game['expansion']:
        del game['expansion']
    del game['image']
    game['new'] = True
    game['sort_name'] = _sub_regex.sub('', game['name'])
    game['submitter'] = submitter
    requests = [InsertOne(game)]
    games = list(_games.find().sort([('_id', -1)]).limit(10))
    if len(games) == 10:
        requests.append(UpdateOne({'_id': games[-1]['_id']}, {
            '$unset': {'new': 1}
        }))
    _games.bulk_write(requests)

def is_gamemaster(username):
    return _gamemasters.count({'username': username})