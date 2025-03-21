from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Post
from app import db
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        posts = Post.query.all()
    else:
        flash('Please login to view posts')
        posts = []
    return render_template('index.html', posts=posts, user=current_user)

@main.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        content = request.form.get('content')

        if not  content:
            flash('Content required!')
        else:
            new_post = Post(content=content, user=current_user, date_posted=datetime.now(timezone.utc))                
            db.session.add(new_post)
            db.session.commit()
            flash('Post created successfully!')
            return redirect(url_for('main.index'))

    return redirect(url_for('main.index'))


