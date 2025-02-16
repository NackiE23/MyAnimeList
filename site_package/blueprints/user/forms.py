from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, DataRequired, EqualTo, ValidationError, Email

from site_package.models.user import User


class RegisterForm(FlaskForm):
    def validate_email(self, email_to_check):
        email = User.query.filter_by(email=email_to_check.data).first()
        if email:
            raise ValidationError("User with this email already exists!")

    name = StringField(label="Name", validators=[Length(min=2, max=60), DataRequired()])
    email = StringField(label="Email", validators=[Email(), DataRequired()])
    password1 = PasswordField(label="Password", validators=[DataRequired()])
    password2 = PasswordField(label="Confirm Password", validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField(label="Sign up")


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[Email(), DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Log in")
