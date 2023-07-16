#!/usr/bin/python3
"""Defines the class structures for my application"""
from datetime import datetime

from chatzilla import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get((int(user_id)))


class User(db.Model, UserMixin):
    """Defines the model for the Users in the database"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Room(db.Model):
    """Defines models for Rooms in the database"""
    u_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow().strftime('%y-%m-%d'))
    user = db.relationship('User', backref=db.backref('rooms', lazy=True))


class RoomMessage(db.Model):
    """Defines the models for RoomMessage in the Database"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    room = db.relationship('Room', backref=db.backref('messages', lazy=True))
    user = db.relationship('User', backref=db.backref('messages', lazy=True))
