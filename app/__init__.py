# Description: This file is the entry point of the application. It creates the app and registers the blueprints. It also loads the configuration from the config file.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from app.config import config_options, Config
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
bcrypt =  Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
migrate = Migrate(db)

def create_app():
    app = Flask(__name__)   

    app.config.from_object(config_options[os.getenv('FLASK_ENV', 'development')])

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db) 

    with app.app_context():
        db.create_all()

    from app import models

    from app.routes import blueprints 
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app