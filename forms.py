
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email

class SignUpForm(FlaskForm):
    email = EmailField("Email",validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Create Account")

class LogInForm( FlaskForm):
    email = EmailField("Email",validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Log In")

class MessageForm( FlaskForm):
    message = TextAreaField("Message",validators=[DataRequired()],render_kw={"placeholder": "Send chat...","class": "my-textarea","id":"myTextArea"})
    submit = SubmitField("Send")


class UpdateProfileForm(FlaskForm):
    profile_picture = StringField("Profile Picture Link:", validators=[DataRequired()])
    submit = SubmitField("Update Profile")