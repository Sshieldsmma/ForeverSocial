from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, FriendRequest, friends_table
from werkzeug.utils import secure_filename
from datetime import datetime
import os
 
users = Blueprint('users', __name__)

UPLOAD_FOLDER = 'static/images/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@users.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@users.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.bio = request.form.get('bio')
        dob = request.form.get('date_of_birth')
        if dob:
            current_user.date_of_birth = datetime.strptime(dob, "%Y-%m-%d")
        
        
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)

                filename = f"{current_user.id}_{secure_filename(file.filename)}"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                User.profile_picture = filename
                
                
                if current_user.profile_picture:
                    old_file_path = os.path.join(UPLOAD_FOLDER, current_user.profile_picture)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('users.profile'))

    return render_template('edit_profile.html', user=current_user)


@users.route('/send_friend_request/<int:receiver_id>', methods=['POST'])
@login_required
def send_friend_request(receiver_id):
    receiver = User.query.get_or_404(receiver_id)
    if receiver == current_user:
        flash('You cannot send friend request to yourself!')
        return redirect(url_for('users.profile', user_id=receiver.id))   
    existing_request = FriendRequest.query.filter_by(sender_id=current_user.id, receiver_id=receiver.id, status='pending').first()
    if existing_request:
        flash('Friend request already sent!')
        return redirect(url_for('users.profile', user_id=receiver.id))

    friend_request = FriendRequest(sender_id=current_user.id, receiver_id=receiver.id)
    db.session.add(friend_request)
    db.session.commit()

    flash(f'Friend request sent to {receiver.username}!')
    return redirect(url_for('users.profile', user_id=receiver.id))


@users.route('/remove_friend/<int:friend_id>')
@login_required
def remove_friend(friend_id):
    friend = User.query.get(friend_id)
    if friend in current_user.friends:
        current_user.friends.remove(friend)
        db.session.commit()
        flash(f'You are no longer friends with {friend.username}')
    else:
        flash(f'You are not friends with {friend.username}')
    return redirect(url_for('users.profile', user_id=friend_id))



@users.route('/accept_friend_request/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    friend_request = FriendRequest.query.get_or_404(request_id)
    
    if friend_request.receiver_id != current_user.id:
        flash("You don't have permission to accept this request!")
        return redirect(url_for('users.profile', user_id=current_user.id))

    sender = User.query.get(friend_request.sender_id)
    if sender not in current_user.friends:
        current_user.friends.append(sender)
        sender.friends.append(current_user)
    
    friend_request.status = 'accepted'
    db.session.commit()
    flash(f'You are now friends with {sender.username}!')
    return redirect(url_for('users.profile', user_id=current_user.id))

    

@users.route('/decline_friend_request/<int:request_id>', methods=['POST'])
@login_required
def decline_friend_request(request_id):
    friend_request = FriendRequest.query.get_or_404(request_id)

    if friend_request.receiver_id != current_user.id:
        flash("You don't have permission to decline this request!")
        return redirect(url_for('users.profile', user_id=current_user.id))

    friend_request.status = 'declined'
    db.session.commit()
    flash("Friend request declined.")
    return redirect(url_for('users.profile', user_id=current_user.id))



@users.route('/cancel_friend_request/<int:request_id>', methods=['POST'])
@login_required
def cancel_friend_request(request_id):
    friend_request = FriendRequest.query.get_or_404(request_id)

    if friend_request.sender_id != current_user.id:
        flash("You don't have permission to cancel this request!")
        return redirect(url_for('users.profile', user_id=current_user.id))

    db.session.delete(friend_request)
    db.session.commit()
    flash("Friend request cancelled.")
    return redirect(url_for('users.profile', user_id=current_user.id))



@users.route('/friends_list/<int:user_id>')
@login_required
def friends_list(user_id):
    user = User.query.get_or_404(user_id)
    friends = user.friends
    return render_template('friends_list.html', user=user, friends=friends)
