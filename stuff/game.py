from flask import session
from wtforms.validators import DataRequired, Regexp, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, StringField
from urllib.request import urlopen

def _validate_link(form, field):
    try:
        urlopen(field.data)
    except:
        raise ValidationError('URL is unreachable')

def _validate_name(form, field):
    from stuff.database import game_exists
    if game_exists(field.data):
        raise ValidationError(f'"{field.data}" already exists')

def _validate_owner(form, field):
    from stuff.database import is_quartermaster
    if not is_quartermaster(session['userinfo']['preferred_username']) and field.data not in ['CSH', session['userinfo']['preferred_username']]:
        raise ValidationError('Only quartermasters can enter any owner')

class Game(FlaskForm):

    image = FileField('image', validators = [
        FileRequired(), FileAllowed(['jpg'])
    ])
    link = StringField('link', validators = [DataRequired()])
    name = StringField('name', validators = [DataRequired(), _validate_name])
    owner = StringField('owner', validators = [DataRequired(), _validate_owner])
    info = StringField('info', validators = [DataRequired()])

    def __init__(self, submitter = None):
        if submitter:
            super().__init__(
                link = '', 
                info = '',
                name = '',
                owner = submitter
            )
        else:
            super().__init__()

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        return True
