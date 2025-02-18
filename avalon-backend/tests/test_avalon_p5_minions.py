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


def play_round_1(players, room_id, team_leader, players_role):
    """ Play round 1 """
    minion_1 = ''
    minion_1_int = -1
    minion_2 = ''
    minion_2_int = -1

    for index, role in enumerate(players_role):
        if role == 'minion' and not minion_1:
            minion_1 = 'player-' + str(index + 1)
            minion_1_int = index
        else:
            minion_2 = 'player-' + str(index + 1)
            minion_2_int = index

    team_leader.emit(constants.PICK_PLAYER, {'player': minion_1})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [minion_1]
        }

    team_leader.emit(constants.PICK_PLAYER, {'player': minion_2})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [minion_1, minion_2]
        }

    team_leader.emit(constants.CONFIRM_TEAM)

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_VOTE_TEAM,
            'uuid': room_id,
            'picked_players': [minion_1, minion_2]
        }

    players[0].emit(constants.VOTE_TEAM, {'vote': True})
    players[1].emit(constants.VOTE_TEAM, {'vote': False})
    players[2].emit(constants.VOTE_TEAM, {'vote': True})
    players[3].emit(constants.VOTE_TEAM, {'vote': False})
    players[4].emit(constants.VOTE_TEAM, {'vote': True})

    new_leader_obj = None

    for index, player in enumerate(players):
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert 'team_leader' in received[0]['args'][0]
        data = received[0]['args'][0]
        new_leader = data['team_leader']
        assert data['state'] == constants.STATE_QUEST
        assert data['players_yes'] == ['player-1', 'player-3', 'player-5']
        assert data['players_no'] == ['player-2', 'player-4']

        if ('player-' + str(index + 1)) == new_leader:
            new_leader_obj = player

    players[minion_1_int].emit(constants.PERFORM_QUEST, {'vote': False})
    players[minion_2_int].emit(constants.PERFORM_QUEST, {'vote': True})

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

    return new_leader_obj


def play_round_2(players, room_id, team_leader, players_role):
    """ Play round 1 """
    minion_1 = ''
    minion_1_int = -1
    minion_2 = ''
    minion_2_int = -1
    servant = ''
    servant_int = -1

    for index, role in enumerate(players_role):
        if role == 'minion' and not minion_1:
            minion_1 = 'player-' + str(index + 1)
            minion_1_int = index
        elif role == 'minion' and not minion_2:
            minion_2 = 'player-' + str(index + 1)
            minion_2_int = index
        elif role == 'servant' and not servant:
            servant = 'player-' + str(index + 1)
            servant_int = index

    team_leader.emit(constants.PICK_PLAYER, {'player': minion_1})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [minion_1]
        }

    team_leader.emit(constants.PICK_PLAYER, {'player': minion_2})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [minion_1, minion_2]
        }

    team_leader.emit(constants.PICK_PLAYER, {'player': servant})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [minion_1, minion_2, servant]
        }

    team_leader.emit(constants.CONFIRM_TEAM)

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_VOTE_TEAM,
            'uuid': room_id,
            'picked_players': [minion_1, minion_2, servant]
        }

    players[0].emit(constants.VOTE_TEAM, {'vote': True})
    players[1].emit(constants.VOTE_TEAM, {'vote': False})
    players[2].emit(constants.VOTE_TEAM, {'vote': True})
    players[3].emit(constants.VOTE_TEAM, {'vote': False})
    players[4].emit(constants.VOTE_TEAM, {'vote': True})

    new_leader_obj = None

    for index, player in enumerate(players):
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert 'team_leader' in received[0]['args'][0]
        data = received[0]['args'][0]
        new_leader = data['team_leader']
        assert data['state'] == constants.STATE_QUEST
        assert data['players_yes'] == ['player-1', 'player-3', 'player-5']
        assert data['players_no'] == ['player-2', 'player-4']

        if ('player-' + str(index + 1)) == new_leader:
            new_leader_obj = player

    players[minion_1_int].emit(constants.PERFORM_QUEST, {'vote': False})
    players[minion_2_int].emit(constants.PERFORM_QUEST, {'vote': False})
    players[servant_int].emit(constants.PERFORM_QUEST, {'vote': True})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [],
            'quests': [False, False, None, None, None],
            'failed': 2
        }

    return new_leader_obj


def play_round_3(players, room_id, team_leader, players_role):
    """ Play round 1 """
    minion_1 = ''
    minion_1_int = -1
    minion_2 = ''
    minion_2_int = -1

    for index, role in enumerate(players_role):
        if role == 'minion' and not minion_1:
            minion_1 = 'player-' + str(index + 1)
            minion_1_int = index
        else:
            minion_2 = 'player-' + str(index + 1)
            minion_2_int = index

    team_leader.emit(constants.PICK_PLAYER, {'player': minion_1})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [minion_1]
        }

    team_leader.emit(constants.PICK_PLAYER, {'player': minion_2})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [minion_1, minion_2]
        }

    team_leader.emit(constants.CONFIRM_TEAM)

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_VOTE_TEAM,
            'uuid': room_id,
            'picked_players': [minion_1, minion_2]
        }

    players[0].emit(constants.VOTE_TEAM, {'vote': True})
    players[1].emit(constants.VOTE_TEAM, {'vote': False})
    players[2].emit(constants.VOTE_TEAM, {'vote': True})
    players[3].emit(constants.VOTE_TEAM, {'vote': False})
    players[4].emit(constants.VOTE_TEAM, {'vote': True})

    new_leader_obj = None

    for index, player in enumerate(players):
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert 'team_leader' in received[0]['args'][0]
        data = received[0]['args'][0]
        new_leader = data['team_leader']
        assert data['state'] == constants.STATE_QUEST
        assert data['players_yes'] == ['player-1', 'player-3', 'player-5']
        assert data['players_no'] == ['player-2', 'player-4']

        if ('player-' + str(index + 1)) == new_leader:
            new_leader_obj = player

    players[minion_1_int].emit(constants.PERFORM_QUEST, {'vote': False})
    players[minion_2_int].emit(constants.PERFORM_QUEST, {'vote': True})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [],
            'quests': [False, False, False, None, None],
            'failed': 1
        }

        assert received[1]['name'] == constants.GAME_LISTENER
        data = received[1]['args'][0]
        assert data['state'] == constants.STATE_FINISHED
        assert data['uuid'] == room_id
        assert data['humans_victory'] is False

    return new_leader_obj


def test_start_vanilla_game():
    """ Test to see if we can start a normal game with 5 people """
    players = create_players()
    room_id = start_room(players)
    team_leader, players_role = start_game(players, room_id)

    team_leader = play_round_1(players, room_id, team_leader, players_role)
    team_leader = play_round_2(players, room_id, team_leader, players_role)
    team_leader = play_round_3(players, room_id, team_leader, players_role)

    for player in players:
        player.disconnect()
