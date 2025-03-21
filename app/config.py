import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

basedir = os.path.abspath(os.path.dirname(__file__))

instance_path = os.path.join(basedir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', "default_secret_key")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(instance_path, 'site.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(instance_path, 'site.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(instance_path, 'site.db')}"

#class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
   # SQLALCHEMY_DATABASE_URI = os.getenv('PRODUCTION_DATABASE_URL', 'MySQL')

config_options = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    #'production': ProductionConfig
}
