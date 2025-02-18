"""
    Test the game itself.
"""
from flask_socketio import SocketIOTestClient
from app import socketio, app
from app import constants

FLASK_TEST_CLIENT = app.test_client()


def create_players():
    """ Create the players for the test """
    p_1 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    p_2 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    p_3 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    p_4 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    p_5 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    return [p_1, p_2, p_3, p_4, p_5]


def start_room(players):
    """ Start the room """
    p_1 = players[0]
    p_1.emit(constants.CREATE_ROOM, {'name': 'player-1'})
    received = p_1.get_received()
    room_id = received[1]['args'][0]['uuid']

    for index, player in enumerate(players):
        if player == p_1:
            continue
        player.emit(constants.JOIN_ROOM, {'name': 'player-' + str(index + 1), 'uuid': room_id})

    # Clean out the cache
    for player in players:
        player.get_received()

    return room_id


def start_game(players, room_id):
    """ Start the game with the setup """
    # Game starts
    p_1 = players[0]
    p_2 = players[1]
    p_1.emit(constants.START_SETUP)

    received = p_1.get_received()
    assert received[0]['name'] == constants.GAME_LISTENER
    assert received[0]['args'][0] == {'state': constants.STATE_SETUP, 'uuid': room_id}

    # Test it with one other player. We can assume that this 1 player will represent the others
    received = p_2.get_received()
    assert received[0]['name'] == constants.GAME_LISTENER
    assert received[0]['args'][0] == {'state': constants.STATE_SETUP, 'uuid': room_id}

    # Clean out the cache
    for player in players:
        player.get_received()

    # Start with vanilla gameplay
    p_1.emit(constants.START_GAME, {'special_characters': []})

    players_role = []

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert 'role' in received[0]['args'][0]
        role = received[0]['args'][0]['role']
        assert received[0]['args'][0] == {
            'state': constants.STATE_BEGIN,
            'uuid': room_id, 'role': role
        }
        players_role.append(role)

    # Should not exceed the maximum amount
    assert players_role.count(constants.MINION) == 2

    for i in range(0, len(players) - 1):
        players[i].emit(constants.ACCEPT_ROLE)

    for player in players:
        player.get_received()

    players[-1].emit(constants.ACCEPT_ROLE)

    for index, player in enumerate(players):
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert 'team_leader' in received[0]['args'][0]
        team_leader_name = received[0]['args'][0]['team_leader']
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'team_leader': team_leader_name
        }

        if ('player-' + str(index + 1)) == team_leader_name:
            team_leader = player

    return (team_leader, players_role)


def test_round_non_minion_fail():
    """ Test a round where a servant tries to fail """
    players = create_players()
    room_id = start_room(players)
    team_leader, players_role = start_game(players, room_id)

    minion = ''
    minion_int = -1
    servant = ''
    servant_int = -1

    for index, role in enumerate(players_role):
        if role == 'minion' and not minion:
            minion = 'player-' + str(index + 1)
            minion_int = index
        elif role == 'servant' and not servant:
            servant = 'player-' + str(index + 1)
            servant_int = index

    team_leader.emit(constants.PICK_PLAYER, {'player': minion})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [minion]
        }

    team_leader.emit(constants.PICK_PLAYER, {'player': servant})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [minion, servant]
        }

    team_leader.emit(constants.CONFIRM_TEAM)

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_VOTE_TEAM,
            'uuid': room_id,
            'picked_players': [minion, servant]
        }

    players[0].emit(constants.VOTE_TEAM, {'vote': True})
    players[1].emit(constants.VOTE_TEAM, {'vote': False})
    players[2].emit(constants.VOTE_TEAM, {'vote': True})
    players[3].emit(constants.VOTE_TEAM, {'vote': False})
    players[4].emit(constants.VOTE_TEAM, {'vote': True})

    for index, player in enumerate(players):
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert 'team_leader' in received[0]['args'][0]
        data = received[0]['args'][0]
        assert 'team_leader' in data
        assert data['state'] == constants.STATE_QUEST
        assert data['players_yes'] == ['player-1', 'player-3', 'player-5']
        assert data['players_no'] == ['player-2', 'player-4']

    players[minion_int].emit(constants.PERFORM_QUEST, {'vote': False})
    players[servant_int].emit(constants.PERFORM_QUEST, {'vote': False})

    received = players[servant_int].get_received()
    assert received[0]['name'] == constants.SYS_MESSAGE
    assert received[0]['args'][0] == {
        'error': 'Only minions can fail a quest!'
    }

    players[servant_int].emit(constants.PERFORM_QUEST, {'vote': True})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [],
            'quests': [False, None, None, None, None],
            'failed': 1
        }

    for player in players:
        player.disconnect()


def test_round_fake_team_leader():
    """ Play with a fake leader """
    players = create_players()
    room_id = start_room(players)
    team_leader, _ = start_game(players, room_id)
    # Test if a fake leader can pick players
    for player in players:
        if player != team_leader:
            fake_leader = player
            break

    fake_leader.emit(constants.PICK_PLAYER, {'player': 'player-1'})

    received = fake_leader.get_received()
    assert received[0]['name'] == constants.SYS_MESSAGE
    assert received[0]['args'][0] == {
        'error': 'You are not the team leader!'
    }

    # Test if a fake leader can confirm the team
    team_leader.emit(constants.PICK_PLAYER, {'player': 'player-1'})
    team_leader.emit(constants.PICK_PLAYER, {'player': 'player-2'})
    team_leader.emit(constants.PICK_PLAYER, {'player': 'player-3'})

    # Clean cache, this functionality has already been test before
    for player in players:
        player.get_received()

    fake_leader.emit(constants.CONFIRM_TEAM)

    received = fake_leader.get_received()
    assert received[0]['name'] == constants.SYS_MESSAGE
    assert received[0]['args'][0] == {
        'error': 'You are not the team leader!'
    }

    for player in players:
        player.disconnect()


def test_round_double_dip():
    """ Test to see if it will prevent a player from being picked twice """
    players = create_players()
    room_id = start_room(players)
    team_leader, _ = start_game(players, room_id)

    team_leader.emit(constants.PICK_PLAYER, {'player': 'player-1'})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': ['player-1']
        }

    team_leader.emit(constants.PICK_PLAYER, {'player': 'player-1'})

    received = team_leader.get_received()
    assert received[0]['name'] == constants.SYS_MESSAGE
    assert received[0]['args'][0] == {
        'error': 'Player is already selected!'
    }

    for player in players:
        player.disconnect()


def test_start_not_enough_players():
    """ Not enough players are available to start the game """
    p_1 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    p_2 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    p_3 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
    p_4 = SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)

    p_1.emit(constants.CREATE_ROOM, {'name': 'p1'})
    received = p_1.get_received()
    room_id = received[1]['args'][0]['uuid']

    p_2.emit(constants.JOIN_ROOM, {'name': 'p2', 'uuid': room_id})
    p_3.emit(constants.JOIN_ROOM, {'name': 'p3', 'uuid': room_id})
    p_4.emit(constants.JOIN_ROOM, {'name': 'p4', 'uuid': room_id})
    p_1.get_received()  # Clean out the cache

    p_1.emit(constants.START_SETUP)

    received = p_1.get_received()
    assert received[0]['name'] == constants.SYS_MESSAGE
    data = received[0]['args'][0]
    assert data['error'] == 'You need a minimum of 5 players to start a game!'

    p_1.disconnect()
    p_2.disconnect()
    p_3.disconnect()
    p_4.disconnect()
