from pymongo import MongoClient
from re import compile, IGNORECASE

games = MongoClient().game_night.games

def create_filters(request):
    filters = {}
    try:
        filters['name'] = compile(request.args['name'], IGNORECASE)
    except:
        pass
    try:
        players = int(request.args['players'])
        filters['$and'] = [{'min_players': {'$lte': players}}, {'max_players': {'$gte': players}}]
    except:
        pass
    return filters

def get_count(request):
    return games.count(create_filters(request))

def get_games(request):
    return games.find(create_filters(request), {'_id': False}).sort([('sort_name', 1)])

def get_players():
    return games.aggregate([{'$group': {'_id': False, 'max': {'$max': '$max_players'}, 'min': {'$min': '$min_players'}}}]).next()

def get_random_game(request):
    return games.aggregate([{'$match': create_filters(request)}, {'$sample': {'size': 1}}, {'$project': {'_id': False}}]).next()