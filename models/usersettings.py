from flask_wtf import FlaskForm
from flask import flash, session
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired
from datetime import datetime
from init import domains, db, settings_list

class UserSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<UserSetting name={}, value={}>'.format(self.name, self.value)

def load_settings():
    user_settings = UserSetting.query.filter_by(user_id=session.get('user_id')).all()
    settings = {}
    for setting in user_settings:
        session[setting.name] = setting.value
        settings[setting.name]= setting.value
    print(f'load_settings: {settings}')
    return settings

def store_setting(user_id,name,value):   
    setting = UserSetting.query.filter_by(user_id=user_id, name=name).first()
    if setting:
        print(f'Updating {setting} for user {user_id} with {value}')
        setting.value=value
    else:
        print(f'Storing new {setting} for user {user_id} with {value}' )
        setting = UserSetting()
        setting.user_id=user_id
        setting.name=name
        setting.value=value
        db.session.add(setting)        
    db.session.commit()

def lookup_setting(name):
    setting = UserSetting.query.filter_by(user_id=session.get('user_id'), name=name).first()
    return setting.value if setting else None