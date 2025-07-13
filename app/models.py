from app import db, bcrypt, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone



friends_table = db.Table(
    'friends',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):  
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    bio = db.Column(db.Text, nullable=True, default="Hi")
    profile_picture = db.Column(db.String(255), default='/static/default_profile.png')
        
    friends = db.relationship(
        'User',
        secondary=friends_table,
        primaryjoin=(friends_table.c.user_id == id),
        secondaryjoin=(friends_table.c.friend_id == id),
        backref=db.backref('friend_list', lazy='dynamic'),
        lazy='dynamic'
    )

    def add_friend(self, user):
        if not self.is_friends_with(user):
            self.friends.append(user)

    def remove_friend(self, user):
        if self.is_friends_with(user):
            self.friends.remove(user)

    def is_friends_with(self, user):
        return self.friends.filter(friends_table.c.friend_id == user.id).count() > 0

    def __repr__(self):
        return f"<User {self.username}>"
    
    def age(self):
        today = datetime.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.Column(db.Integer, default=0, nullable=False)
    comments = db.Column(db.Text, nullable=True)  
    views = db.Column(db.Integer, default=0)  
    
    comments = db.relationship('Comment', backref='post', lazy=True)
    user = db.relationship('User', backref='posts', lazy=True) 

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    user = db.relationship('User', backref='comments')


class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')


    def __repr__(self):
        return f"<FriendRequest {self.sender_id} -> {self.receiver_id}, Status: {self.status}>"


class Reel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Text, nullable=True)
    thumbnail_art = db.Column(db.String(255), nullable=True)  # URL to the thumbnail image
    audio_url = db.Column(db.String(255), nullable=True)  # URL to the audio file
    tags = db.Column(db.String(255), nullable=True)  
    duration = db.Column(db.Integer, nullable=True)  

    user = db.relationship('User', backref='reels', lazy=True)

    def __repr__(self):
        return f"<Reel {self.id}, User: {self.user_id}, Caption: {self.caption}>"


from app import login_manager  

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
