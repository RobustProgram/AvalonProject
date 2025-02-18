"""
    Test the game itself.
"""
from app import constants
from . import PlayGameManager


def round_1(game):
    """ Play the first round of the game """
    room_id = game.room_id
    players = game.players

    # First vote, we want player 2 and 3
    game.quest_add_player('player-2')
    game.quest_add_player('player-3')
    game.quest_confirm_team(['player-2', 'player-3'])

    # No one agrees
    game.quest_vote_team('player-1', False)
    game.quest_vote_team('player-2', False)
    game.quest_vote_team('player-3', False)
    game.quest_vote_team('player-4', False)
    game.quest_vote_team('player-5', False)

    for index, player in enumerate(players):
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert 'team_leader' in received[0]['args'][0]
        new_leader = received[0]['args'][0]['team_leader']
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'day': 0,
            'players_yes': [],
            'players_no': ['player-1', 'player-2', 'player-3', 'player-4', 'player-5'],
            'picked_players': [],
            'team_leader': new_leader
        }
        if ('player-' + str(index + 1)) == new_leader:
            game.update_leader(player)

    # Second pick round, we choose player 3 and 5
    game.quest_add_player('player-3')
    game.quest_add_player('player-5')
    game.quest_confirm_team(['player-3', 'player-5'])

    # Slight agreement, but not unanimous
    game.quest_vote_team('player-1', True)
    game.quest_vote_team('player-2', True)
    game.quest_vote_team('player-3', False)
    game.quest_vote_team('player-4', False)
    game.quest_vote_team('player-5', False)

    for index, player in enumerate(players):
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert 'team_leader' in received[0]['args'][0]
        new_leader = received[0]['args'][0]['team_leader']
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'day': 0,
            'players_yes': ['player-1', 'player-2'],
            'players_no': ['player-3', 'player-4', 'player-5'],
            'picked_players': [],
            'team_leader': new_leader
        }
        if ('player-' + str(index + 1)) == new_leader:
            game.update_leader(player)

    # Third pick round, we choose player 4 and 5
    game.quest_add_player('player-4')
    game.quest_add_player('player-5')
    game.quest_confirm_team(['player-4', 'player-5'])

    # Everyone agrees
    game.quest_vote_team('player-1', True)
    game.quest_vote_team('player-2', True)
    game.quest_vote_team('player-3', True)
    game.quest_vote_team('player-4', True)
    game.quest_vote_team('player-5', True)

    for index, player in enumerate(players):
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert 'team_leader' in received[0]['args'][0]
        data = received[0]['args'][0]
        new_leader = data['team_leader']
        assert data['state'] == constants.STATE_QUEST
        assert data['players_yes'] == ['player-1', 'player-2', 'player-3', 'player-4', 'player-5']
        assert data['players_no'] == []

        if ('player-' + str(index + 1)) == new_leader:
            game.update_leader(player)

    game.quest_succeed_mission('player-4', True)
    game.quest_succeed_mission('player-5', True)

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
    """
        Play the second round of the game. We can be more confident that the functions work from
        the first run
    """
    room_id = game.room_id
    players = game.players

    game.quest_add_player('player-2')
    game.quest_add_player('player-3')
    game.quest_add_player('player-4')
    game.quest_confirm_team(['player-2', 'player-3', 'player-4'])

    game.quest_vote_team('player-1', True)
    game.quest_vote_team('player-2', True)
    game.quest_vote_team('player-3', False)
    game.quest_vote_team('player-4', False)
    game.quest_vote_team('player-5', False)

    game.clean_votes()

    game.quest_add_player('player-3')
    game.quest_add_player('player-4')
    game.quest_add_player('player-5')
    game.quest_confirm_team(['player-3', 'player-4', 'player-5'])

    game.quest_vote_team('player-1', True)
    game.quest_vote_team('player-2', True)
    game.quest_vote_team('player-3', False)
    game.quest_vote_team('player-4', False)
    game.quest_vote_team('player-5', False)

    game.clean_votes()

    # Rig it to put in at both minions and fail it
    minions = game.get_minions()
    servants = game.get_servants()
    game.quest_add_player(minions[0])
    game.quest_add_player(minions[1])
    game.quest_add_player(servants[0])
    game.quest_confirm_team([minions[0], minions[1], servants[0]])

    game.quest_vote_team('player-1', True)
    game.quest_vote_team('player-2', True)
    game.quest_vote_team('player-3', True)
    game.quest_vote_team('player-4', True)
    game.quest_vote_team('player-5', True)

    game.clean_votes()

    game.quest_succeed_mission(minions[0], True)
    game.quest_succeed_mission(minions[1], False)
    game.quest_succeed_mission(servants[0], True)

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [],
            'quests': [True, False, None, None, None],
            'failed': 1
        }


def round_3(game):
    """ Play the third round of the game """
    room_id = game.room_id
    players = game.players

    # First vote, we want player 2 and 3
    game.quest_add_player('player-2')
    game.quest_add_player('player-3')
    game.quest_confirm_team(['player-2', 'player-3'])

    # No one agrees
    game.quest_vote_team('player-1', False)
    game.quest_vote_team('player-2', False)
    game.quest_vote_team('player-3', False)
    game.quest_vote_team('player-4', False)
    game.quest_vote_team('player-5', False)

    game.clean_votes()

    # Second pick round, we choose player 3 and 5
    game.quest_add_player('player-3')
    game.quest_add_player('player-5')
    game.quest_confirm_team(['player-3', 'player-5'])

    # Slight agreement, but not unanimous
    game.quest_vote_team('player-1', True)
    game.quest_vote_team('player-2', True)
    game.quest_vote_team('player-3', False)
    game.quest_vote_team('player-4', False)
    game.quest_vote_team('player-5', False)

    game.clean_votes()

    # Third pick round, we choose player 4 and 5
    game.quest_add_player('player-4')
    game.quest_add_player('player-5')
    game.quest_confirm_team(['player-4', 'player-5'])

    # Everyone agrees
    game.quest_vote_team('player-1', True)
    game.quest_vote_team('player-2', True)
    game.quest_vote_team('player-3', True)
    game.quest_vote_team('player-4', True)
    game.quest_vote_team('player-5', True)

    game.clean_votes()

    game.quest_succeed_mission('player-4', True)
    game.quest_succeed_mission('player-5', True)

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'picked_players': [],
            'quests': [True, False, True, None, None],
            'failed': 0
        }


def round_4(game):
    """ Finish it off with a 4th round """
    room_id = game.room_id
    players = game.players

    game.quest_add_player('player-2')
    game.quest_add_player('player-3')
    game.quest_add_player('player-4')
    game.quest_confirm_team(['player-2', 'player-3', 'player-4'])

    game.clean_votes()

    game.quest_succeed_mission('player-2', True)
    game.quest_succeed_mission('player-3', True)
    game.quest_succeed_mission('player-4', True)

    for player in players:
        received = player.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {
            'state': constants.STATE_DAY,
            'uuid': room_id,
            'quest_status': True,
            'failed': 0
        }

        assert received[1]['name'] == constants.GAME_LISTENER
        assert received[1]['args'][0] == {
            'state': constants.STATE_FINISHED,
            'uuid': room_id,
            'humans_victory': True
        }


def test_start_vanilla_game():
    """ This test will play a more complex game with multiple failures """
    game = PlayGameManager(5)

    round_1(game)
    round_2(game)
    round_3(game)

    game.disconnect()
