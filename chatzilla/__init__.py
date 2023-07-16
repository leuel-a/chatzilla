#!/usr/bin/python3
"""This is the instantiation of the current flask application"""
from urllib.parse import quote, quote_plus

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from chatzilla.events import socketio

app = Flask(__name__)
socketio.init_app(app)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'af282fd8286c31655583c614976cbe8b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:%s@localhost:3306/chatzilla' % quote_plus('LeuelA$1993')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from chatzilla import routes, models
