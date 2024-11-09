from init import db
from datetime import datetime
from flask_wtf import FlaskForm
from flask import flash, session
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from flask_login import UserMixin
from init import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from models.usersettings import load_settings
import uuid

# the actual model for the user
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True,nullable=False)
    user_email = db.Column(db.String(128),unique=True,nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_secret = db.Column(db.String(16), unique=True,nullable=True,default=lambda: str(uuid.uuid4()))
    authenticated=False

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return authenticated

    def is_active(self):
        return True  # Assuming all users are active

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id)) 
    print(f'Loading User: {user}')   
    user.lastlogin = datetime.utcnow()
    user.authenticated=True
    db.session.add(user)
    db.session.commit()
    session['username'] = user.username
    session['user_id'] = user.id
    session['user_secret'] = user.user_secret
    load_settings()
    print(f'Session.user_id={session.get("user_id")}')
    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401

def find_user_by_secret(secret):
    return User.query.filter_by(user_secret==secret).first()

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean)

    def __init__(self, user_id, success):
        self.user_id = user_id
        self.success = success

# allows a user to login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],render_kw={"placeholder": "your username"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "your password"})    
    keep_logged_in = BooleanField('Keep Logged In')    
    def validate_password(self, field):
        user = User.query.filter_by(username=self.username.data).first()
        if user is None or not check_password_hash(user.password_hash, field.data):
            flash('Username or password are wrong', 'fail')
            raise ValidationError('Invalid username or password')            
            if user:
                if request.form.get('keep_logged_in'):
                    session.permanent = True
                db.session.add(LoginAttempt(user.id,False))
                db.session.commit()
        session['username']=user.username

# allows a new user to register
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],render_kw={"placeholder": "your username"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "your password"})
    confirm_password = PasswordField('Confirm', validators=[DataRequired(), EqualTo('password')],render_kw={"placeholder": "Repeat your password"})
    user_email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"placeholder": "your email"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Name already taken')

    def validate_user_email(self, user_email):
        user = User.query.filter_by(user_email=user_email.data).first()
        if user:
            raise ValidationError('Email already taken')

class PasswordChangeForm(FlaskForm):
    password = PasswordField('Old Password', validators=[DataRequired()],render_kw={"placeholder": "your old password"})    
    newpassword = PasswordField('New Password', validators=[DataRequired()],render_kw={"placeholder": "your new password"})
    confirm_newpassword = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('newpassword')],render_kw={"placeholder": "confirm new password"})

    def validate_password(self,field):
        user = User.query.filter_by(id=session.get('user_id')).first()
        if not check_password_hash(user.password_hash, field.data):
            raise ValidationError('Invalid password')        