from flask import Blueprint


from app.routes.auth import auth
from app.routes.main import main
from app.routes.users import users
from app.routes.reels import reels
from app.routes.messages import messages

blueprints = [auth, main, users, reels, messages]


