from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired

class Game(FlaskForm):
    image = FileField('image', validators = [FileRequired(), FileAllowed(['jpg'])])
    link = StringField('link', validators = [DataRequired()])
    max_players = IntegerField('max_players', validators = [DataRequired()])
    min_players = IntegerField('min_players', validators = [DataRequired()])
    name = StringField('name', validators = [DataRequired()])
    owner = StringField('owner', validators = [DataRequired()])