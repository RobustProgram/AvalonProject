"""
    Test the game itself.
"""
from app import constants
from . import PlayGameManager


def round_1(game: PlayGameManager):
    """ Play the first round of the game """
    room_id = game.room_id
    players = game.players
    minions = game.get_minions()
    servants = game.get_servants()

    game.quest_add_player(minions[0])
    game.quest_add_player(servants[0])
    game.quest_add_player(servants[1])
    game.quest_confirm_team([minions[0], servants[0], servants[1]])

    game.quest_vote_team("player-1", True)
    game.quest_vote_team("player-2", False)
    game.quest_vote_team("player-3", True)
    game.quest_vote_team("player-4", False)
    game.quest_vote_team("player-5", True)
    game.quest_vote_team("player-6", True)
    game.quest_vote_team("player-7", False)
    game.quest_vote_team("player-8", True)

    for index, player in enumerate(players):
        received = player.get_received()
        assert received[0]["name"] == constants.GAME_LISTENER
        assert "team_leader" in received[0]["args"][0]
        data = received[0]["args"][0]
        new_leader = data["team_leader"]
        assert data["state"] == constants.STATE_QUEST
        assert data["players_yes"] == [
            "player-1",
            "player-3",
            "player-5",
            "player-6",
            "player-8",
        ]
        assert data["players_no"] == ["player-2", "player-4", "player-7"]

        if ("player-" + str(index + 1)) == new_leader:
            game.update_leader(player)

    game.quest_succeed_mission(minions[0], False)
    game.quest_succeed_mission(servants[0], True)
    game.quest_succeed_mission(servants[1], True)

    for player in players:
        received = player.get_received()
        assert received[0]["name"] == constants.GAME_LISTENER
        assert received[0]["args"][0] == {
            "state": constants.STATE_DAY,
            "uuid": room_id,
            "picked_players": [],
            "quests": [False, None, None, None, None],
            "failed": 1,
        }


def test_start_vanilla_game():
    """ Test to see if we can start a normal game with 8 people """
    game = PlayGameManager(8)

    round_1(game)

    game.disconnect()
