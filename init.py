import datetime

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import flask_login
import secrets
import os
from dotenv import load_dotenv, dotenv_values

styles = ['light','dark']
domains = ['pieper.dev','delusions.de', 'workreloaded.com', 'driving-development.de']
categories = ['default', 'admin', 'invoices', 'media', 'development', 'food', 'games', 'health', 'honey', 'offline', 'personal', 'shopping', 'service', 'spam', 'tools', 'social', 'software', 'travel', 'work', 'writing', 'throwaway']
settings_list = ['favorite_domain', 'personal_email']
load_dotenv()
db = SQLAlchemy()
login_manager = flask_login.LoginManager()


def create_app():
    app = Flask(__name__)    
    login_manager.init_app(app)
    if os.environ.get('MODE')=='development' :
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        print('-------> running in development mode <---------')
        env_vars = dotenv_values('.env')
        #for key, value in env_vars.items():
        #    print(f"env: {key}: {value}")
    else:         
        db_user = os.environ.get('MYSQL_DATABASE_USER','default_user')
        db_password = os.environ.get('MYSQL_DATABASE_PASSWORD','default_pass')
        database = os.environ.get('MYSQL_DATABASE_DB','default_db')
        db_host = os.environ.get('MYSQL_DATABASE_HOST','db')
        db_port =  os.environ.get('MYSQL_DATABASE_PORT',3306)
        database_url = f'mysql://{db_user}:{db_password}@{db_host}:{db_port}/{database}'
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print(f'running in production mode with database_url={database_url}')

    secret_key =  os.environ.get('SECRET_KEY')
    if secret_key:
        app.config['SECRET_KEY'] = secret_key
    else:
        #for local testing:
        app.config['SECRET_KEY']='replaceme'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=64)
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE='None',
    )


    from routes.auth import auth_bp
    from routes.settings import settings_bp
    from routes.tools import tools_bp
    from routes.links import link_bp
    from routes.tags import tag_bp
    from routes.social import social_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(link_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(social_bp)

    print(app.url_map)

    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    return app

