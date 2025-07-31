from app import socketio
from flask import Blueprint, request, redirect, url_for, flash, render_template, query
from flask_login import login_required, current_user
from app.models import User, FriendRequest, db, Message


messages = Blueprint('messages', __name__)

@messages.route('/messages/<int:user_id>', methods=['GET','POST'])
@login_required
def forever_messages(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        msg = request.form.get('message')
        new_msg = Message(sender_id=current_user.id, receiver_id=user.id, message=msg)
        db.session.add(new_msg)
        db.session.commit()
    messages = query.filter(
        (Message.sender_id == current_user.id) & (Message.receiver_id == user.id) |
        (Message.sender_id == user.id) & (Message.receiver_id == current_user.id)
    ).order_by(Message.timestamp.asc()).all()
    return render_template('messages.html', user=user, messages=messages)