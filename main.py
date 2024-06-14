from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from forms import SignUpForm, LogInForm, MessageForm, UpdateProfileForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo
import json

app = Flask(__name__,template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
app.config['SECRET_KEY'] = 'futurebelongstothehus'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), index=True, unique=True)
    email = db.Column(db.String(80),index = True, unique = True)
    password = db.Column(db.String(50), index = False, unique = False)
    profile_picture = db.Column(db.String(1000), index=True, unique=False)
    messages = db.relationship('Message',backref='owner',lazy='dynamic')


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text,index = True, unique = False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


@app.route('/')
@app.route('/home')
def index():
    if current_user.is_authenticated:
        return render_template("index.html",user=current_user)
    return render_template("index.html")


@app.route('/sign_up',methods=["GET","POST"])
def sign_up():
    sign_up_form = SignUpForm()

    if sign_up_form.validate_on_submit():
        if not User.query.filter_by(email=sign_up_form.email.data).first():
            newUser = User(email = sign_up_form.email.data,username=sign_up_form.username.data,password = generate_password_hash(sign_up_form.password.data),profile_picture="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png")
            db.session.add(newUser)
            db.session.commit()
            flash("Account Created")
            return redirect(url_for("index"))
        else:
            flash("Creation failed: email already in use")
            return redirect(url_for("sign_up"))
    return render_template("sign_up.html", template_form=sign_up_form)


@app.route('/log_in',methods=["GET","POST"])
def log_in():
    log_in_form = LogInForm(csrf_enabled=False)
    if current_user.is_authenticated:
        flash("Already logged in!")
        return redirect(url_for('index', _external=True))
    if log_in_form.validate_on_submit():
        findUser = User.query.filter_by(email = log_in_form.email.data).first()
        if findUser and check_password_hash(findUser.password, log_in_form.password.data):
            flash("Logged in!")
            login_user(findUser)
            return redirect(url_for('index', _external=True))
        else:
            flash("Incorrect login information")
            return redirect(url_for('log_in', _external=True))
    return render_template("log_in.html", template_form=log_in_form)


@app.route('/profile', methods=["GET","POST"])
@login_required
def profile():
    update_profile_form = UpdateProfileForm(csrf_enabled=False)
    if update_profile_form.validate_on_submit():
        jsonForm = json.dumps(update_profile_form.data)
        return redirect(url_for('update_profile',form=jsonForm,_external=True))
    return render_template('profile.html',template_form=update_profile_form)


@app.route('/logout', methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index',_external=True))


@app.route('/chat',methods=["GET","POST"])
@login_required
def chat():
    message_form = MessageForm(csrf_enabled=False)
    if message_form.validate_on_submit():
        new_message = Message(text=message_form.message.data,user_id=current_user.id)
        db.session.add(new_message)
        db.session.commit()
    messages = Message.query.all()
    return render_template('chat.html',template_form=message_form, all_messages=messages)


@app.route('/update_profile',methods=["GET","POST"])
@login_required
def update_profile():
    update_profile_form = json.loads(request.args.get('form', None))
    current_user.profile_picture = update_profile_form["profile_picture"]
    db.session.commit()
    flash("Profile Updated")
    return redirect(url_for('profile',_external=True))