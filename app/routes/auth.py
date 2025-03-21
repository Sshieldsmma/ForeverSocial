from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import User, FriendRequest, friends_table
from app import db, bcrypt
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime


auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not email or not first_name or not last_name or not dob or not username or not password:
            flash('All fields are required')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Email already exists, try logging in')
            return redirect(url_for('auth.register'))
        elif len(password) < 8:
            flash('Password must be at least 8 characters')
            return redirect(url_for('auth.register'))
        else:
            new_user = User(email=email, username=username, password=hashed_password, date_of_birth=dob, first_name=first_name, last_name=last_name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created successfully')
            return redirect(url_for('main.index'))
    
    return render_template('register.html', user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            if bcrypt.check_password_hash(user.password, password):
                flash('Logged in successfully')
                login_user(user, remember=True)
                return redirect(url_for('main.index'))
            else:
                flash('Incorrect password, try again')
                return redirect(url_for('auth.login'))
        else:
            flash('Email does not exist, register now to get started')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()  
    return redirect(url_for('auth.login'))
