#!/usr/bin/python3
from flask_login import current_user
from flask_socketio import emit

from chatzilla.extensions import socketio


@socketio.on('connect')
def handle_connect():
    print(f'Client {current_user.username} Connected')


@socketio.on('new-message')
def handle_send_message(message, room):
    from chatzilla import db
    from chatzilla.models import Room, RoomMessage
    current_room = Room.query.filter_by(name=room).first()
    new_message = RoomMessage(content=message, room_id=current_room.id, user_id=current_user.id)
    db.session.add(new_message)
    db.session.commit()
    emit('chat', {'message': message, 'user': current_user.username}, broadcast=True)
