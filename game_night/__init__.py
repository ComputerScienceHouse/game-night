from flask import abort, Flask, jsonify, redirect, render_template
from os import environ
from flaskext.markdown import Markdown
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from game_night.database import *

app = Flask(__name__)
_config = {
    'PREFERRED_URL_SCHEME': environ.get('GAME_NIGHT_URL_SCHEME', 'https'),
    'SECRET_KEY': environ['GAME_NIGHT_SECRET_KEY'],
    'SERVER_NAME': environ['GAME_NIGHT_SERVER_NAME'],
    'WTF_CSRF_ENABLED': False
}
app.config.update(_config)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
app.url_map.strict_slashes = False

Markdown(app)

_client_info = {
    'client_id': environ['GAME_NIGHT_CLIENT_ID'],
    'client_secret': environ['GAME_NIGHT_CLIENT_SECRET']
}
_auth = OIDCAuthentication(app, client_registration_info = _client_info, issuer = environ['GAME_NIGHT_ISSUER'])

@app.route('/api')
@require_read_key
def api():
    return jsonify(list(get_games()))

@app.route('/api/count')
@require_read_key
def api_count():
    return jsonify(get_count())

@app.route('/api/key', methods = ['GET', 'POST'])
@app.route('/api/key/write', defaults = {'write': True}, methods = ['GET', 'POST'])
@require_gamemaster
def api_key(write = False):
    return jsonify(generate_api_key(write))

@app.route('/api/owners')
@require_read_key
def api_owners():
    return jsonify(get_owners())

@app.route('/api/random')
@app.route('/api/random/<int:sample_size>')
@require_read_key
def api_random(sample_size = 1):
    sample = list(get_random_games(sample_size))
    return jsonify(sample[0] if len(sample) == 1 else sample)

@app.route('/')
@_auth.oidc_auth
def index():
    return render_template('index.html', bucket = environ['GAME_NIGHT_S3_BUCKET'], games = get_games(), gamemaster = is_gamemaster(), players = get_players())

@app.route('/random')
@_auth.oidc_auth
def random():
    return render_template('index.html', bucket = environ['GAME_NIGHT_S3_BUCKET'], games = get_random_games(1), gamemaster = is_gamemaster(), players = get_players())

@app.route('/rules/<game_name>')
@_auth.oidc_auth
def rules(game_name):
    game = get_game(game_name)
    if game is None:
        abort(404)
    return render_template('rules.html', bucket = environ['GAME_NIGHT_S3_BUCKET'], game = game, gamemaster = is_gamemaster(), players = get_players())

@app.route('/submissions')
@_auth.oidc_auth
def submissions():
    gamemaster = is_gamemaster()
    return render_template('submissions.html', bucket = environ['GAME_NIGHT_S3_BUCKET'], gamemaster = gamemaster, games = get_submissions(gamemaster), players = get_players())

@app.route('/submit', methods = ['GET', 'POST'])
@_auth.oidc_auth
@require_gamemaster
def submit():
    if request.method == 'GET':
        return render_template('submit.html', gamemaster = True, players = get_players())
    submit_game()
    return redirect('/')