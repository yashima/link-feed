import flask, flask_login
from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime

from init import db
from models.user import User, LoginForm, RegistrationForm, LoginAttempt
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        flask_login.login_user(user)        
        return redirect(url_for('links.list'))

    return render_template('base-form.html', form=form,title="Login",submit_label='Login')

@auth_bp.route('/logout')
def logout():    
    logout_user()
    session.clear()    
    return redirect(url_for('.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    allow_registration = os.getenv('ALLOW_REGISTRATION', 'True')
    form = RegistrationForm()
    if allow_registration.lower() == 'true':
        if form.validate_on_submit():
            user = User(username=form.username.data)
            user.password = form.password.data
            user.user_email=form.user_email.data
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('.login'))
        else:
            print(form.errors)
    return render_template('register.html', form=form, allow_registration=allow_registration, submit_label='Register')




