from app import socketio
from flask_socketio import emit, join_room, leave_room
from flask import Blueprint, request, redirect, url_for, flash, render_template, query
from flask_login import login_required, current_user
from app.models import User, FriendRequest, db, Message


messages = Blueprint('messages', __name__)

@socketio.on('join')
def on_join(data):
    room = data('room')
    join_room(room)


@socketio.on('send_message')
def handle_send_message(data):
    room = data('room')
    message = data('message')
    sender = current_user

    u1, u2 = map(int, room.split('-'))
    receiver_id = u1 if sender.id == u2 else u2

    from app.models import Message
    msg = Message(
        sender_id=sender.id,
        receiver_id=receiver_id,
        message=message
    )
    db.session.add(msg)
    db.session.commit()

    emit('receive_message', {
        'message': message,
        'sender': sender.username
    }, to=room)



@messages.route('/messages/<int:user_id>')
@login_required
def messages (user_id):
    from app.models import user, Message
    user = User.query.get_or_404(user_id)

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id))  |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    return render_template('messages.html', user=user, messages=messages)

