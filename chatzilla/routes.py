#!/usr/bin/python3
"""The definition of the routes will be made here"""
import secrets
import os
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image

from chatzilla import app, db, bcrypt
from chatzilla.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreateRoomForm
from chatzilla.models import User, Room, RoomMessage


@app.route('/', strict_slashes=False)
@app.route('/home', strict_slashes=False)
def home():
    if current_user.is_authenticated:
        return redirect(url_for('user_page'))
    return render_template('home.html')


@app.route('/register', strict_slashes=False, methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('home')

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')


@app.route('/login', strict_slashes=False, methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('home')

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('user_page')
        flash("Login unsuccessful please check email or password!", 'danger')
    return render_template('login.html', form=form, title='Login')


@app.route('/logout', strict_slashes=False)
def logout():
    logout_user()
    return redirect('home')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    # Resize the image to save space
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/account', strict_slashes=False, methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('You account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/user_page', strict_slashes=False)
def user_page():
    return render_template('user_page.html', title=f'Welcome Back')


@app.route('/rooms', strict_slashes=False, methods=['GET', 'POST'])
@login_required
def rooms():
    create_room_form = CreateRoomForm()
    all_rooms = Room.query.all()
    print('Here', create_room_form.validate_on_submit())
    if create_room_form.validate_on_submit():
        print('Reached Here')
        room = Room(
            name=create_room_form.room_name.data,
            u_id=current_user.id,
            description=create_room_form.room_description.data
        )
        db.session.add(room)
        db.session.commit()
        flash(f'Room {create_room_form.room_name.data} has been created!', 'success')
        return redirect(url_for('rooms'))
    return render_template('rooms.html', title='Rooms', create_form=create_room_form, rooms=all_rooms)


@app.route('/validate_room/<string:room_name>', strict_slashes=False, methods=['POST'])
def validate_room(room_name):
    room = Room.query.filter_by(name=room_name).first()
    if room:
        return jsonify({'value': True})
    return jsonify({'value': False})


@app.route('/api/messages/<string:name>', strict_slashes=False, methods=['GET'])
def get_room(name):
    # Get room id based on the room name
    room = Room.query.filter_by(name=name).first()
    # Get all messages in the room from RoomMessage table that have id equal to the room id and order by time
    messages = RoomMessage.query.filter_by(room_id=room.id).order_by(RoomMessage.created_at).all()
    # Create a list of dictionaries with the message and the user that sent it
    messages_list = []
    for message in messages:
        messages_list.append({'message': message.content, 'username': message.user.username})
    return jsonify({'messages': messages_list})


@app.route('/api/rooms/<int:u_id>', strict_slashes=False, methods=['GET'])
def my_rooms(u_id):
    # Get all rooms that the user is in
    rooms = Room.query.filter_by(u_id=u_id).all()
    # Create a list of dictionaries with the room name and the room id
    return render_template('my_rooms.html', rooms=rooms)


@app.route('/discover', strict_slashes=False, methods=['GET', 'POST'])
@login_required
def discover():
    users = User.query.all()
    return render_template('discover.html', title='Discover People', users=users)
