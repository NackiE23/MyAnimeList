from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, DateField, FileField, SubmitField
from wtforms.validators import DataRequired


class AnimeModelForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    alternative_name = StringField(label="Alternative name")
    description = TextAreaField(label="Description")
    grade = IntegerField(label="Grade")
    release = DateField(label="Release", validators=[DataRequired()])
    img = FileField(label="Image")
    submit = SubmitField(label="Create an anime info")
