"""
    Socket io events for game events
"""
import random
from flask import request
from flask_socketio import emit
from . import socketio, constants, CLIENTS, ROOMS, PLAYER_SPLIT, QUEST_AMOUNT


@socketio.on(constants.START_SETUP)
def on_start_setup():
    """ Set up the game """
    starting_client = CLIENTS[request.sid]
    room_object = ROOMS[starting_client.room_id]

    if room_object.state != constants.LOBBY:
        emit(
            constants.SYS_MESSAGE,
            {'error': 'You can only start the game from the lobby screen!'}
        )
        return

    if len(room_object.players) < 5:
        emit(
            constants.SYS_MESSAGE,
            {'error': 'You need a minimum of 5 players to start a game!'}
        )
        return

    room_object.state = constants.STATE_SETUP

    emit(
        constants.GAME_LISTENER,
        {'state': constants.STATE_SETUP, 'uuid': room_object.uuid},
        room=room_object.uuid
    )


@socketio.on(constants.START_GAME)
def on_start_game(data=None):
    """ Start the game """
    starting_client = CLIENTS[request.sid]
    room_object = ROOMS[starting_client.room_id]

    if room_object.state != constants.STATE_SETUP:
        emit(constants.SYS_MESSAGE, {'error': 'You are not on the setup page!'})
        return

    room_object.state = constants.START_GAME

    player_count = len(room_object.players)
    evil_count = PLAYER_SPLIT[player_count][0]

    shuffled_players = room_object.players[:]
    random.shuffle(shuffled_players)

    for i in range(0, player_count):
        if i < evil_count:
            player_room = shuffled_players[i].sid
            room_object.roles[shuffled_players[i].sid] = constants.MINION
            emit(
                constants.GAME_LISTENER,
                {
                    'state': constants.STATE_BEGIN,
                    'uuid': room_object.uuid,
                    'role': constants.MINION
                },
                room=player_room
            )
        else:
            player_room = shuffled_players[i].sid
            room_object.roles[shuffled_players[i].sid] = constants.SERVANT
            emit(
                constants.GAME_LISTENER,
                {
                    'state': constants.STATE_BEGIN,
                    'uuid': room_object.uuid,
                    'role': constants.SERVANT
                },
                room=player_room
            )


@socketio.on(constants.ACCEPT_ROLE)
def on_accept_role():
    """ Accept the role """
    client_object = CLIENTS[request.sid]
    room_object = ROOMS[client_object.room_id]

    if client_object in room_object.players_accepted:
        emit(constants.SYS_MESSAGE, {'error': 'You already elected to start the game!'})
        return

    room_object.add_accepted_player(client_object)

    if len(room_object.players) == len(room_object.players_accepted):
        room_object.players_accepted = []
        room_object.state = constants.STATE_DAY
        room_object.quest_leader = random.randint(0, len(room_object.players))
        emit(
            constants.GAME_LISTENER,
            {
                'state': constants.STATE_DAY,
                'uuid': room_object.uuid,
                'team_leader': room_object.get_quest_leader_name()
            },
            room=room_object.uuid
        )
    else:
        emit(
            constants.GAME_LISTENER,
            {
                'state': constants.STATE_BEGIN,
                'uuid': room_object.uuid,
                'players_accepted': room_object.get_accepted_player_names()
            },
            room=room_object.uuid
        )


@socketio.on(constants.PICK_PLAYER)
def on_pick_player(data):
    """ Pick a player to join the quest """
    client_object = CLIENTS[request.sid]
    room_object = ROOMS[client_object.room_id]

    if client_object != room_object.players[room_object.quest_leader]:
        emit(constants.SYS_MESSAGE, {'error': 'You are not the team leader!'})
        return

    for player in room_object.players:
        if data['player'] == player.name:
            if player in room_object.quest_team:
                emit(constants.SYS_MESSAGE, {'error': 'Player is already selected!'})
                return
            room_object.quest_team.append(player)
            break

    emit(
        constants.GAME_LISTENER,
        {
            'state': constants.STATE_DAY,
            'uuid': room_object.uuid,
            'picked_players': room_object.get_quest_team_names()
        },
        room=room_object.uuid
    )


@socketio.on(constants.UNPICK_PLAYER)
def on_unpick_player(data):
    """ Unpick a player from the quest team """
    client_object = CLIENTS[request.sid]
    room_object = ROOMS[client_object.room_id]

    if client_object != room_object.players[room_object.quest_leader]:
        emit(constants.SYS_MESSAGE, {'error': 'You are not the team leader!'})
        return

    for player in room_object.players:
        if data['player'] == player.name:
            room_object.quest_team.remove(player)

            emit(
                constants.GAME_LISTENER,
                {
                    'state': constants.STATE_DAY,
                    'uuid': room_object.uuid,
                    'picked_players': room_object.get_quest_team_names()
                },
                room=room_object.uuid
            )
            return

    emit(constants.SYS_MESSAGE, {'error': 'Player is not a part of the quest team!'})


@socketio.on(constants.CONFIRM_TEAM)
def on_confirm_team():
    """ Confirm the team """
    client_object = CLIENTS[request.sid]
    room_object = ROOMS[client_object.room_id]

    if client_object != room_object.players[room_object.quest_leader]:
        emit(constants.SYS_MESSAGE, {'error': 'You are not the team leader!'})
        return

    minimum_players = QUEST_AMOUNT[len(room_object.players)][room_object.quest_day]

    if len(room_object.quest_team) != minimum_players:
        emit(constants.SYS_MESSAGE, {
            'error': f'You need to select exactly {minimum_players} players'
        })
        return

    emit(
        constants.GAME_LISTENER,
        {
            'state': constants.STATE_VOTE_TEAM,
            'uuid': room_object.uuid,
            'picked_players': room_object.get_quest_team_names()
        },
        room=room_object.uuid
    )


@socketio.on(constants.VOTE_TEAM)
def on_vote_team(data):
    """ Vote on whether or not to confirm the team """
    client_object = CLIENTS[request.sid]
    room_object = ROOMS[client_object.room_id]

    if client_object in room_object.players_accepted:
        emit(constants.SYS_MESSAGE, {'error': 'You already voted!'})
        return

    room_object.players_accepted.append((request.sid, data['vote']))

    if len(room_object.players_accepted) == len(room_object.players):
        players_yes = []
        players_no = []
        for (pid, vote) in room_object.players_accepted:
            if vote:
                players_yes.append(CLIENTS[pid].name)
            else:
                players_no.append(CLIENTS[pid].name)

        room_object.players_accepted = []
        room_object.quest_leader = (room_object.quest_leader + 1) % len(room_object.players)

        if len(players_yes) > len(players_no):
            room_object.state = constants.STATE_QUEST
        else:
            room_object.quest_team = []
            room_object.state = constants.STATE_DAY

        emit(
            constants.GAME_LISTENER,
            {
                'state': room_object.state,
                'uuid': room_object.uuid,
                'day': room_object.quest_day,
                'players_yes': players_yes,
                'players_no': players_no,
                'picked_players': room_object.get_quest_team_names(),
                'team_leader': room_object.get_quest_leader_name()
            },
            room=room_object.uuid
        )


@socketio.on(constants.PERFORM_QUEST)
def on_perform_quest(data):
    """ Go on the quest and either fail it or succeed it """
    client_object = CLIENTS[request.sid]
    room_object = ROOMS[client_object.room_id]

    # First determine if the player is minion or servant
    if room_object.roles[request.sid] != 'minion' and not data['vote']:
        emit(constants.SYS_MESSAGE, {'error': 'Only minions can fail a quest!'})
        return

    room_object.players_accepted.append((request.sid, data['vote']))

    if len(room_object.players_accepted) == len(room_object.quest_team):
        failed = 0
        max_fail = 1

        if room_object.quest_day == 3 and len(room_object.quest_team) >= 7:
            max_fail = 2

        for (_, vote) in room_object.players_accepted:
            if not vote:
                failed += 1

        room_object.players_accepted = []
        room_object.quest_team = []
        room_object.state = constants.STATE_DAY

        if failed >= max_fail:
            room_object.advance_quest(False)
        else:
            room_object.advance_quest(True)

        emit(
            constants.GAME_LISTENER,
            {
                'state': room_object.state,
                'uuid': room_object.uuid,
                'picked_players': room_object.get_quest_team_names(),
                'quests': room_object.quests,
                'failed': failed
            },
            room=room_object.uuid
        )

        check_game(room_object)


def check_game(room_object):
    """ Check if a room has completed a game """
    quest_success = sum(q is True for q in room_object.quests)
    quest_fail = sum(q is False for q in room_object.quests)

    parsed_roles = {}
    for key_sid in room_object.roles:
        name = CLIENTS[key_sid].name
        parsed_roles[name] = room_object.roles[key_sid]

    if quest_success == 3:
        room_object.state = constants.STATE_FINISHED
        emit(
            constants.GAME_LISTENER,
            {
                'state': constants.STATE_FINISHED,
                'uuid': room_object.uuid,
                'roles': parsed_roles,
                'humans_victory': True
            },
            room=room_object.uuid
        )
    elif quest_fail == 3:
        room_object.state = constants.STATE_FINISHED
        emit(
            constants.GAME_LISTENER,
            {
                'state': constants.STATE_FINISHED,
                'uuid': room_object.uuid,
                'roles': parsed_roles,
                'humans_victory': False
            },
            room=room_object.uuid
        )
