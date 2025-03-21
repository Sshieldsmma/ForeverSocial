from flask import Blueprint


from app.routes.auth import auth
from app.routes.main import main
from app.routes.users import users


blueprints = [auth, main, users]


