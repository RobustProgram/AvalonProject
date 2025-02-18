"""
    Test the game itself.
"""
from app import constants
from . import PlayGameManager


def round_1(game):
    """ Play the first round of the game """
    room_id = game.room_id
    players = game.players

    game.quest_add_player('player-2')
    game.quest_add_player('player-3')
    game.quest_confirm_team(['player-2', 'player-3'])

    game.quest_vote_team('player-1', True)
    game.quest_vote_team('player-2', False)
    game.quest_vote_team('player-3', True)
    game.quest_vote_team('player-4', False)
    game.quest_vote_team('player-5', True)

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
            game.update_leader(player)

    game.quest_succeed_mission('player-2', True)
    game.quest_succeed_mission('player-3', True)

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [],
            'quests': [True, None, None, None, None],
            'failed': 0
        }


def round_2(game):
    """ Play the second round of the game """
    room_id = game.room_id
    players = game.players

    game.quest_add_player('player-2')
    game.quest_add_player('player-3')
    game.quest_add_player('player-4')
    game.quest_confirm_team(['player-2', 'player-3', 'player-4'])

    game.quest_vote_team('player-1', True)
    game.quest_vote_team('player-2', True)
    game.quest_vote_team('player-3', True)
    game.quest_vote_team('player-4', False)
    game.quest_vote_team('player-5', True)

    for index, player in enumerate(players):
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert 'team_leader' in received[0]['args'][0]
        data = received[0]['args'][0]
        new_leader = data['team_leader']
        assert data['state'] == constants.STATE_QUEST
        assert data['players_yes'] == ['player-1', 'player-2', 'player-3', 'player-5']
        assert data['players_no'] == ['player-4']

        if ('player-' + str(index + 1)) == new_leader:
            game.update_leader(player)

    game.quest_succeed_mission('player-2', True)
    game.quest_succeed_mission('player-3', True)
    game.quest_succeed_mission('player-4', True)

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [],
            'quests': [True, True, None, None, None],
            'failed': 0
        }


def round_3(game):
    """ Play the third round """
    team_leader = game.team_leader
    room_id = game.room_id
    players = game.players

    game.quest_add_player('player-1')
    game.quest_add_player('player-4')
    game.quest_remove_player('player-1')
    game.quest_remove_player('player-4')
    game.quest_add_player('player-2')
    game.quest_add_player('player-3')

    team_leader.emit(constants.CONFIRM_TEAM)

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_VOTE_TEAM,
            'uuid': room_id,
            'picked_players': ['player-2', 'player-3']
        }

    players[0].emit(constants.VOTE_TEAM, {'vote': True})
    players[1].emit(constants.VOTE_TEAM, {'vote': False})
    players[2].emit(constants.VOTE_TEAM, {'vote': True})
    players[3].emit(constants.VOTE_TEAM, {'vote': False})
    players[4].emit(constants.VOTE_TEAM, {'vote': True})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert 'team_leader' in received[0]['args'][0]
        data = received[0]['args'][0]
        assert 'team_leader' in data
        assert data['state'] == constants.STATE_QUEST
        assert data['players_yes'] == ['player-1', 'player-3', 'player-5']
        assert data['players_no'] == ['player-2', 'player-4']

    players[1].emit(constants.PERFORM_QUEST, {'vote': True})
    players[2].emit(constants.PERFORM_QUEST, {'vote': True})

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [],
            'quests': [True, True, True, None, None],
            'failed': 0
        }

        assert received[1]['name'] == constants.GAME_LISTENER
        data = received[1]['args'][0]
        assert data['state'] == constants.STATE_FINISHED
        assert data['uuid'] == room_id
        assert data['humans_victory'] is True


def test_start_vanilla_game():
    """ Test to see if we can start a normal game with 5 people """
    game = PlayGameManager(5)

    round_1(game)
    round_2(game)
    round_3(game)

    game.disconnect()
