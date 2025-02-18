"""
    Socket events for rooms.
    Handles joining, leaving rooms. Also handles room commands such as kicking
"""
import uuid
from flask import request
from flask_socketio import emit, join_room, leave_room
from . import socketio, constants, CLIENTS, ROOMS
from .client import Client
from .room import EMPTY_ROOM, Room
from .util import data_required, get_name


@socketio.on("connect")
def on_connect():
    """ When you first establish a connection to the server """
    emit(
        constants.SYS_MESSAGE,
        {"message": "Welcome, you are now connected to the server!"},
    )


@socketio.on("disconnect")
def on_disconnect():
    """ Remove the user from the room and update everyone in the room """
    try:
        client_object = CLIENTS[request.sid]
    except KeyError:
        # This just means they are disconnecting from the server from the lobby screen
        return

    room_object = ROOMS[client_object.room_id]
    room_object.remove_player_using_sid(request.sid)

    leave_room(client_object.room_id)

    del CLIENTS[request.sid]

    emit(
        constants.ROOM_LISTENER,
        room_object.get_room_data_for_client(),
        room=client_object.room_id,
        include_self=False,
    )


@socketio.on(constants.CREATE_ROOM)
def create_room(data=None):
    """ When you create room on the server """
    if request.sid in CLIENTS:
        emit(constants.SYS_MESSAGE, {"error": "You are already in a room."})
        return

    name = get_name(data)

    room_id = str(uuid.uuid4())

    join_room(room_id)

    client_object = Client(name, request.sid)
    client_object.assign_room(room_id)
    CLIENTS[request.sid] = client_object

    room_object = Room(room_id, client_object)
    ROOMS[room_id] = room_object

    client_data = room_object.get_room_data_for_client()
    client_data["my_name"] = name

    emit(constants.CREATE_ROOM_LISTENER, client_data)


@socketio.on(constants.JOIN_ROOM)
@data_required("You can not join a room without sending data.")
def join_avalon(data=None):
    """ Join a room """
    if request.sid in CLIENTS:
        emit(constants.SYS_MESSAGE, {"error": "You are already in a room."})
        return

    name = get_name(data)

    if "uuid" in data:
        room_id = data["uuid"]

        if room_id in ROOMS:
            join_room(room_id)

            client_object = Client(name, request.sid)
            client_object.assign_room(room_id)
            CLIENTS[request.sid] = client_object

            room_object = ROOMS[room_id]
            room_object.add_player(client_object)

            client_data = room_object.get_room_data_for_client()

            emit(constants.ROOM_LISTENER, client_data, room=room_id, include_self=False)

            client_data["my_name"] = name

            emit(constants.ROOM_LISTENER, client_data)
        else:
            emit(
                constants.SYS_MESSAGE,
                {"error": "You can not join a room that does not exist."},
            )
    else:
        emit(constants.SYS_MESSAGE, {"error": "You did not supply a uuid."})


@socketio.on(constants.LEAVE_ROOM)
def leave_avalon():
    """ Leaving a room """
    try:
        room_id = CLIENTS[request.sid].room_id
    except KeyError:
        emit(
            constants.SYS_MESSAGE,
            {"error": "You need to join a room first in order to leave."},
        )
        return

    if room_id in ROOMS:
        room_object = ROOMS[room_id]
        room_object.remove_player_using_sid(request.sid)

        leave_room(room_id)

        del CLIENTS[request.sid]

        emit(
            constants.ROOM_LISTENER,
            room_object.get_room_data_for_client(),
            room=room_id,
        )
        emit(constants.ROOM_LISTENER, EMPTY_ROOM, room=request.sid)


@socketio.on(constants.KICK_PLAYER)
@data_required("You can not kick a player without sending data.")
def kick_player(data):
    """ Kicking a player from a room """
    try:
        name = data["name"]
    except KeyError:
        emit(
            constants.SYS_MESSAGE,
            {"error": "You need to provide the name of a person to kick."},
        )
        return

    kicked_sid = None
    for sid in CLIENTS:
        if CLIENTS[sid].name == name:
            kicked_sid = sid
            break

    if kicked_sid:
        CLIENTS[kicked_sid].kick += 1
        room_id = CLIENTS[kicked_sid].room_id
        room_object = ROOMS[room_id]

        if kicked_sid == room_object.host:
            emit(constants.SYS_MESSAGE, {"error": "You can not kick the host!"})
            return

        if CLIENTS[kicked_sid].kick >= int(float(len(room_object.players) / 2) + 0.5):
            room_object.remove_player_using_sid(kicked_sid)
            leave_room(room_id, sid=kicked_sid)
            del CLIENTS[kicked_sid]

            emit(
                constants.ROOM_LISTENER,
                room_object.get_room_data_for_client(),
                skip_sid=kicked_sid,
                room=room_id,
            )
            emit(constants.ROOM_LISTENER, EMPTY_ROOM, room=kicked_sid)
    else:
        emit(
            constants.SYS_MESSAGE, {"error": "The person you provided does not exist."}
        )
