from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, DateField, FileField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    description = TextAreaField(label="Description")
    submit = SubmitField()


class MediaForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    alternative_name = StringField(label="Alternative name")
    description = TextAreaField(label="Description")
    grade = IntegerField(label="Grade")
    release = DateField(label="Release", validators=[DataRequired()])
    img = FileField(label="Image")
    submit = SubmitField(label="Save")
