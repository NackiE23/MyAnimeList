from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    description = TextAreaField(label="Description")
    submit = SubmitField()
