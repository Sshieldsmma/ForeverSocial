from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Post
from app import db
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from ..models import User, Post, FriendRequest
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
            new_post = Post(id=Post.query.count() + 1, content=content, user=current_user, date_posted=datetime.now(timezone.utc))
            db.session.add(new_post)
            db.session.commit()
            flash('Post created successfully!')
            return redirect(url_for('main.index'))

    return redirect(url_for('main.index'))

@main.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post, user=current_user)

''' @main.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('post.get_posts')) '''

@main.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('posts.view_post', post_id=post_id))

@main.route('/comment/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    comment = request.form.get('comment')
    post = Post.query.get_or_404(post_id)
    if post.comments:
        post.comments += f'\n{comment}'
    else:
        post.comments = comment
    db.session.commit()
    return redirect(url_for('post.get_post'))


@main.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        pending_requests = FriendRequest.query.filter_by(receiver_id=current_user.id, status='pending').all()
    else:
        pending_requests = []
    return dict(pending_requests=pending_requests)


@main.route('/search')
def search():
    query = request.args.get('query')

    if not query:
        return render_template('search_results.html', posts=[], users=[])
    
    users = User.query.filter(
        (User.first_name.ilike(f'%{query}%')) |
        (User.last_name.ilike(f'%{query}%')) |
        (User.username.ilike(f'%{query}%'))
    ).all()

    posts = Post.query.filter(Post.content.ilike(f"%{query}%")).all()


    return render_template('search_results.html', posts=posts, users=users, query=query, user=current_user)

