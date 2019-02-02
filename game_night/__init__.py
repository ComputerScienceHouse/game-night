from flask import *
from os import environ
from flaskext.markdown import Markdown
from flask_pyoidc.provider_configuration import *
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from boto3 import client
from game_night.auth import require_gamemaster, require_read_key
from game_night.database import *
from game_night.game import Game

app = Flask(__name__)
app.config.update(
    PREFERRED_URL_SCHEME = environ.get('URL_SCHEME', 'https'),
    SECRET_KEY = environ['SECRET_KEY'], SERVER_NAME = environ['SERVER_NAME'],
    WTF_CSRF_ENABLED = False
)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
app.url_map.strict_slashes = False

Markdown(app)

_config = ProviderConfiguration(
    environ['OIDC_ISSUER'],
    client_metadata = ClientMetadata(
        environ['OIDC_CLIENT_ID'], environ['OIDC_CLIENT_SECRET']
    )
)
_auth = OIDCAuthentication({'default': _config}, app)

_s3 = client(
    's3', aws_access_key_id = environ['S3_KEY'],
    aws_secret_access_key = environ['S3_SECRET'],
    endpoint_url = environ['S3_ENDPOINT']
)

@app.route('/api')
@require_read_key
def api():
    return jsonify(list(get_games(request.args)))

@app.route('/api/count')
@require_read_key
def api_count():
    return jsonify(get_count(request.args))

@app.route('/api/key', methods = ['GET', 'POST'])
@require_gamemaster
def api_key():
    return jsonify(generate_api_key())

@app.route('/api/newest')
@require_read_key
def api_newest():
    return jsonify(list(get_newest_games(request.args)))

@app.route('/api/owners')
@require_read_key
def api_owners():
    return jsonify(get_owners(request.args))

@app.route('/api/random')
@app.route('/api/random/<int:sample_size>')
@require_read_key
def api_random(sample_size = 1):
    sample = list(get_random_games(request.args, sample_size))
    return jsonify(sample[0] if len(sample) == 1 else sample)

@app.route('/delete/<game_name>', methods = ['GET', 'POST'])
@_auth.oidc_auth('default')
@require_gamemaster
def delete(game_name):
    if not delete_game(game_name):
        abort(404)
    _s3.delete_object(Bucket = environ['S3_BUCKET'], Key = game_name + '.jpg')
    return redirect('/')

def _get_template_variables():
    return {
        'gamemaster': is_gamemaster(session['userinfo']['preferred_username']),
        'owners': get_owners(), 'players': get_players(),
        's3_url': f'{environ["S3_ENDPOINT"]}/{environ["S3_BUCKET"]}'
    }

@app.route('/')
@_auth.oidc_auth('default')
def index():
    return render_template(
        'index.html', games = get_games(request.args),
        **_get_template_variables()
    )

@app.route('/random')
@_auth.oidc_auth('default')
def random():
    return render_template(
        'index.html', games = get_random_games(request.args, 1),
        **_get_template_variables()
    )

@app.route('/rules/<game_name>')
@_auth.oidc_auth('default')
def rules(game_name):
    game = get_game(game_name)
    if not game:
        abort(404)
    return render_template(
        'rules.html', game = game, **_get_template_variables()
    )

@app.route('/submissions')
@_auth.oidc_auth('default')
def submissions():
    return render_template(
        'submissions.html',
        games = get_submissions(
            request.args,
            session['userinfo']['preferred_username']
        ), **_get_template_variables()
    )

@app.route('/submit', methods = ['GET', 'POST'])
@_auth.oidc_auth('default')
def submit():
    if request.method == 'GET':
        return render_template(
            'submit.html',
            form = Game(session['userinfo']['preferred_username']),
            game_names = get_game_names(), **_get_template_variables()
        )
    game = Game()
    if not game.validate():
        return render_template(
            'submit.html',
            error = next(iter(game.errors.values()))[0], form = game,
            game_names = get_game_names(), **_get_template_variables()
        )
    game = game.data
    _s3.upload_fileobj(
        game['image'], environ['S3_BUCKET'], game['name'] + '.jpg',
        ExtraArgs = {
            'ACL': 'public-read', 'ContentType': game['image'].content_type
        }
    )
    insert_game(game, session['userinfo']['preferred_username'])
    return redirect('/')