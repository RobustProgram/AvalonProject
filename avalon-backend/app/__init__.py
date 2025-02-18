""" This module sets up the server itself """
import os
from flask import Flask
from flask_socketio import SocketIO

ROOMS = {}
CLIENTS = {}

# The split of (evil, good) with the player count
PLAYER_SPLIT = {
    5: (2, 3),
    6: (2, 4),
    7: (3, 4),
    8: (3, 5),
    9: (3, 6),
    10: (4, 6)
}

# The number of players needed for a quest based on player count
QUEST_AMOUNT = {
    5: (2, 3, 2, 3, 3),
    6: (2, 3, 4, 3, 4),
    7: (2, 3, 3, 4, 4),
    8: (3, 4, 4, 5, 5),
    9: (3, 4, 4, 5, 5),
    10: (3, 4, 4, 5, 5)
}


def create_app(test_config=None):
    """ Create the flask application """
    flask_app = Flask(__name__, instance_relative_config=True)
    flask_app.config.from_mapping(
        SECRET_KEY='app',
        DATABASE=os.path.join(flask_app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        flask_app.config.from_pyfile('config.py', silent=True)
    else:
        flask_app.config.from_mapping(test_config)

    try:
        os.makedirs(flask_app.instance_path)
    except OSError:
        pass

    return flask_app


app = create_app()
socketio = SocketIO(app, cors_allowed_origins='*')


from . import events, game_events
