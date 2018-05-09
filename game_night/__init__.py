from flask import abort, Flask, jsonify, render_template
from os import environ
from flaskext.markdown import Markdown
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from game_night.database import *

app = Flask(__name__)
config = {
    'PREFERRED_URL_SCHEME': environ.get('GAME_NIGHT_URL_SCHEME', 'https'),
    'SECRET_KEY': environ['GAME_NIGHT_SECRET_KEY'],
    'SERVER_NAME': environ['GAME_NIGHT_SERVER_NAME']
}
app.config.update(config)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
app.url_map.strict_slashes = False

Markdown(app)

client_info = {
    'client_id': environ['GAME_NIGHT_CLIENT_ID'],
    'client_secret': environ['GAME_NIGHT_CLIENT_SECRET']
}
auth = OIDCAuthentication(app, client_registration_info = client_info, issuer = environ['GAME_NIGHT_ISSUER'])

@app.route('/api')
@auth.oidc_auth
def api():
    return jsonify(list(get_games()))

@app.route('/api/count')
@auth.oidc_auth
def api_count():
    return jsonify(get_count())

@app.route('/api/owners')
@auth.oidc_auth
def api_owners():
    return jsonify(get_owners())

@app.route('/api/random')
@app.route('/api/random/<int:sample_size>')
@auth.oidc_auth
def api_random(sample_size = 1):
    sample = get_random_games(sample_size)
    return jsonify(sample if sample_size == 1 else list(sample))

@app.route('/')
@auth.oidc_auth
def index():
    return render_template('index.html', bucket = environ['GAME_NIGHT_S3_BUCKET'], games = get_games(), players = get_players())

@app.route('/random')
@auth.oidc_auth
def random():
    game = get_random_games(1)
    return render_template('index.html', bucket = environ['GAME_NIGHT_S3_BUCKET'], games = [] if game is None else [game], players = get_players())

@app.route('/rules/<game_name>')
@auth.oidc_auth
def rules(game_name):
    try:
        game = get_game(game_name)
        return render_template('rules.html', bucket = environ['GAME_NIGHT_S3_BUCKET'], game = game, players = get_players(), rules = game['rules'])
    except:
        abort(404)

@app.route('/submissions')
@auth.oidc_auth
def submissions():
    gamemaster = is_gamemaster()
    return render_template('submissions.html', bucket = environ['GAME_NIGHT_S3_BUCKET'], gamemaster = gamemaster, games = get_submissions(gamemaster), players = get_players())
