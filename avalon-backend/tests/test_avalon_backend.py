"""
    Test the socket connection.
    Note, get_received() seems to remove the saved events from the cache and return it to use.
    Hence, subsequent usage of the function will return fresh events
"""
from flask_socketio import SocketIOTestClient
from app import socketio, app
from app import constants

from app import ROOMS

FLASK_TEST_CLIENT = app.test_client()


def test_socketio():
    """ Perform a simple connection test """
    socketio_test_client = SocketIOTestClient(
        app, socketio, flask_test_client=FLASK_TEST_CLIENT
    )

    assert socketio_test_client.is_connected()

    received = socketio_test_client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.SYS_MESSAGE
    assert received[0]["args"][0] == {
        "message": "Welcome, you are now connected to the server!"
    }

    socketio_test_client.disconnect()


def test_join_leave_room():
    """
    Test to see if we are able to create a room. While we are at, test to see if we are able to
    join and leave it while alerting others.
    """
    create_client = SocketIOTestClient(
        app, socketio, flask_test_client=FLASK_TEST_CLIENT
    )
    join_client = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)

    # ## Confirm that all the test clients can join
    assert create_client.is_connected()
    assert join_client.is_connected()
    # Flush out the event cache as we already tested the welcome message
    create_client.get_received()
    join_client.get_received()

    # ## Create the room and test
    create_client.emit(constants.CREATE_ROOM)

    received = create_client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.CREATE_ROOM_LISTENER
    data = received[0]["args"][0]
    assert "uuid" in data
    assert "host" in data
    assert "players" in data
    assert data["players"] == [data["host"]]

    random_name = data["host"]
    set_name = "JoiningTest"

    # ## Now test joining with a given name
    join_client.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": set_name})

    # Check from the perspective of the joining person
    received = join_client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.ROOM_LISTENER
    data = received[0]["args"][0]
    assert data["host"] == random_name
    assert data["players"] == [random_name, set_name]

    # Check from the perspective of the host
    received = create_client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.ROOM_LISTENER
    data = received[0]["args"][0]
    assert data["host"] == random_name
    assert data["players"] == [random_name, set_name]
    assert "set_name" not in data

    # ## Now test leaving
    join_client.emit(constants.LEAVE_ROOM)
    join_client.get_received()

    # Check again from perspective of the host
    received = create_client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.ROOM_LISTENER
    data = received[0]["args"][0]
    assert data["players"] == [random_name]

    # ## Now test joining without giving a name
    join_client.emit(constants.JOIN_ROOM, {"uuid": data["uuid"]})

    # Check from the perspective of the joining person
    received = join_client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.ROOM_LISTENER
    data = received[0]["args"][0]
    assert data["host"] == random_name

    join_client.disconnect()
    create_client.disconnect()


def test_sudden_disconnect():
    """
    This is just to test a client suddenly disconnecting
    """
    create_client = SocketIOTestClient(
        app, socketio, flask_test_client=FLASK_TEST_CLIENT
    )
    join_client = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)

    # ## Confirm that all the test clients can join
    assert create_client.is_connected()
    assert join_client.is_connected()

    set_name = "MainTest"
    create_client.emit(constants.CREATE_ROOM, {"name": set_name})
    received = create_client.get_received()
    data = received[1]["args"][0]
    join_client.emit(constants.JOIN_ROOM, {"uuid": data["uuid"]})

    # Flush out the event cache as we already tested joining and creating
    create_client.get_received()
    join_client.get_received()

    # ## Force client to disconnect
    join_client.disconnect()

    # Check from perspective of the host
    received = create_client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.ROOM_LISTENER
    data = received[0]["args"][0]
    assert data["host"] == set_name
    assert data["players"] == [set_name]

    create_client.disconnect()


def test_invalid_leave():
    """ Attempt to leave when not in a room """
    client = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    assert client.is_connected()
    client.get_received()  # Clean the event cache

    client.emit(constants.LEAVE_ROOM)

    received = client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.SYS_MESSAGE
    data = received[0]["args"][0]
    assert data["error"] == "You need to join a room first in order to leave."

    client.disconnect()


def test_invalid_join():
    """ Attempt to join a room that does not exist """
    client = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    assert client.is_connected()
    client.get_received()  # Clean the event cache

    client.emit(constants.JOIN_ROOM, {"uuid": "bleh"})

    received = client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.SYS_MESSAGE
    data = received[0]["args"][0]
    assert data["error"] == "You can not join a room that does not exist."

    client.disconnect()


def test_invalid_no_data_join():
    """ Attempt to join a room without sending any data """
    client = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    assert client.is_connected()
    client.get_received()  # Clean the event cache

    client.emit(constants.JOIN_ROOM)

    received = client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.SYS_MESSAGE
    data = received[0]["args"][0]
    assert data["error"] == "You can not join a room without sending data."

    client.disconnect()


def test_invalid_malformed_data():
    """ Attempt to join a room by sending malformed data """
    client = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    assert client.is_connected()
    client.get_received()  # Clean the event cache

    client.emit(constants.JOIN_ROOM, {"test": "test"})

    received = client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.SYS_MESSAGE
    data = received[0]["args"][0]
    assert data["error"] == "You did not supply a uuid."

    client.disconnect()


def test_invalid_join_when_in_room():
    """ Attempt to join a room when already in a room """
    client = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    assert client.is_connected()
    client.get_received()  # Clean the event cache

    client.emit(constants.CREATE_ROOM, {"name": "test_account"})
    received = client.get_received()

    client.emit(constants.JOIN_ROOM, {"uuid": received[0]["args"][0]["uuid"]})

    received = client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.SYS_MESSAGE
    data = received[0]["args"][0]
    assert data["error"] == "You are already in a room."

    # While we are at it, let's also test creating a room
    # Note: We could two ways, either we just reject the request if in room, or we could forcely
    # remove the host and create a new room. However, this could complicate things so I decided
    # to just go with the first method

    client.emit(constants.CREATE_ROOM, {"name": "test_account"})
    received = client.get_received()
    assert len(received) == 1
    assert received[0]["name"] == constants.SYS_MESSAGE
    data = received[0]["args"][0]
    assert data["error"] == "You are already in a room."

    client.disconnect()


def test_kicking():
    """ We are going to test if all the clients can collectively kick a client """
    c_1 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_2 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_3 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_4 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_5 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)

    assert c_1.is_connected() and c_2.is_connected() and c_3.is_connected()
    assert c_4.is_connected() and c_5.is_connected()

    c_1.emit(constants.CREATE_ROOM, {"name": "client1"})
    data = c_1.get_received()[1]["args"][0]

    c_2.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client2"})
    c_3.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client3"})
    c_4.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client4"})
    c_5.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client5"})

    # Clear out the cache
    c_1.get_received()
    c_2.get_received()
    c_3.get_received()
    c_4.get_received()
    c_5.get_received()

    # Test trying to kick client 4
    c_2.emit(constants.KICK_PLAYER, {"name": "client4"})
    assert len(ROOMS[data["uuid"]].players) == 5

    c_3.emit(constants.KICK_PLAYER, {"name": "client4"})
    assert len(ROOMS[data["uuid"]].players) == 5

    c_5.emit(constants.KICK_PLAYER, {"name": "client4"})
    assert len(ROOMS[data["uuid"]].players) == 4

    player_str = []
    for player in ROOMS[data["uuid"]].players:
        if player.name == "client4":
            raise Exception("client4 was not kicked!")
        player_str.append(player.name)

    # All the clients should be notified as well
    received = c_1.get_received()
    assert received[0]["name"] == constants.ROOM_LISTENER
    data = received[0]["args"][0]
    assert data["players"] == player_str

    received = c_2.get_received()
    assert received[0]["name"] == constants.ROOM_LISTENER
    data = received[0]["args"][0]
    assert data["players"] == player_str

    received = c_3.get_received()
    assert received[0]["name"] == constants.ROOM_LISTENER
    data = received[0]["args"][0]
    assert data["players"] == player_str

    received = c_4.get_received()
    assert received[0]["name"] == constants.ROOM_LISTENER
    data = received[0]["args"][0]
    assert data["uuid"] == ""

    received = c_5.get_received()
    assert received[0]["name"] == constants.ROOM_LISTENER
    data = received[0]["args"][0]
    assert data["players"] == player_str

    c_1.disconnect()
    c_2.disconnect()
    c_3.disconnect()
    c_4.disconnect()
    c_5.disconnect()


def test_host_leaving():
    c_1 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_2 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_3 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_4 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_5 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)

    clients = [c_1, c_2, c_3, c_4, c_5]

    c_1.emit(constants.CREATE_ROOM, {"name": "client1"})
    data = c_1.get_received()[1]["args"][0]

    c_2.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client2"})
    c_3.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client3"})
    c_4.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client4"})
    c_5.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client5"})

    # Clear out the cache
    for client in clients:
        client.get_received()

    c_1.emit(constants.LEAVE_ROOM)

    received = c_1.get_received()
    assert received[0]["name"] == constants.ROOM_LISTENER
    assert received[0]["args"][0] == {
        "uuid": "",
        "players": [],
        "state": "",
        "host": "",
    }

    for i in range(1, len(clients)):
        client = clients[i]
        received = client.get_received()
        assert received[0]["name"] == constants.ROOM_LISTENER
        assert received[0]["args"][0]["host"] != "client1"
        assert received[0]["args"][0]["host"] != ""

    for client in clients:
        client.disconnect()


def test_host_disconnecting():
    c_1 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_2 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_3 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_4 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    c_5 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)

    clients = [c_1, c_2, c_3, c_4, c_5]

    c_1.emit(constants.CREATE_ROOM, {"name": "client1"})
    data = c_1.get_received()[1]["args"][0]

    c_2.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client2"})
    c_3.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client3"})
    c_4.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client4"})
    c_5.emit(constants.JOIN_ROOM, {"uuid": data["uuid"], "name": "client5"})

    # Clear out the cache
    for client in clients:
        client.get_received()

    c_1.disconnect()

    for i in range(1, len(clients)):
        client = clients[i]
        received = client.get_received()
        assert received[0]["name"] == constants.ROOM_LISTENER
        assert received[0]["args"][0]["host"] != "client1"
        assert received[0]["args"][0]["host"] != ""

        client.disconnect()
