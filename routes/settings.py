from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from flask_wtf import FlaskForm
from flask_login import login_required
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length


from init import db, domains, settings_list, styles
from models.usersettings import UserSetting, store_setting,load_settings
from models.user import User,PasswordChangeForm

settings_bp = Blueprint('settings', __name__)


class SettingsForm(FlaskForm):        
    favorite_domain = SelectField('Favorite Domain',validators=[DataRequired()], choices=[(domain, domain) for domain in domains])    
    style = SelectField('Site Style',validators=[DataRequired()], choices=[(style, style) for style in styles])    
    personal_email = StringField('Personal Email', validators=[Email()])
    share_token = StringField('Sharing Token', validators=[Length(max=64)])
 

@login_required
@settings_bp.route('/settings/password',methods=['GET', 'POST'])
def change_password():
    user = User.query.filter_by(username=session.get('username')).first()
    form = PasswordChangeForm()
    if request.method == 'POST' and form.validate():
        user.password=form.newpassword.data
        db.session.add(user)
        db.session.commit()
        flash('You changed your password successfully!','success')

    return render_template('base-form.html',form=form, title='Change Password')

@login_required
@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings():    
    user = User.query.filter_by(username=session.get('username')).first()            
    form = SettingsForm()
 
    if request.method == 'POST':
        # Process the form data for a POST request
        if form.validate():                       
            store_setting(user.id,'favorite_domain',form.favorite_domain.data)
            store_setting(user.id,'style',form.style.data)
            user.user_email = form.personal_email.data
            user.user_secret = form.share_token.data
            db.session.flush()            
            db.session.commit()
            flash('Your settings have been updated', 'success')        
            load_settings()
            return redirect(url_for('settings.settings'))
    else:
        settings = load_settings()
        if settings.get('favorite_domain'):
            form.favorite_domain.data = settings['favorite_domain']        
        form.personal_email.data = user.user_email
        form.share_token.data=user.user_secret
        if  settings.get('style'):
            form.style.data = settings['style']

    
    return render_template('base-form.html', form=form, title="Settings",submit_label='Change Settings')

