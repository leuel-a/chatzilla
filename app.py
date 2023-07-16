#!/usr/bin/python3
"""Defines the entry point of my application"""
from chatzilla import app, socketio

if __name__ == '__main__':
    socketio.run(app)
