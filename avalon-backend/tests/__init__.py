""" Standardise gameplay testing """
from flask_socketio import SocketIOTestClient
from app import socketio, app, constants, CLIENTS, ROOMS, PLAYER_SPLIT


FLASK_TEST_CLIENT = app.test_client()


class PlayGameManager:
    """
        Game manager to play an avalon game so we can run tests
    """
    def __init__(self, num_players):
        self.team_leader = None

        self.num_players = num_players
        self.players = []

        self.create_players()
        self.start_room()
        self.start_game()

    def create_players(self):
        """ Create the players for the test """
        for i in range(0, self.num_players):
            self.players.append(
                SocketIOTestClient(app, socketio, flask_test_client=FLASK_TEST_CLIENT)
            )

    def start_room(self):
        """ Start the room """
        p_1 = self.players[0]
        p_1.emit(constants.CREATE_ROOM, {'name': 'player-1'})
        received = p_1.get_received()
        room_id = received[1]['args'][0]['uuid']

        for index, player in enumerate(self.players):
            if player == p_1:
                continue
            player.emit(constants.JOIN_ROOM, {'name': 'player-' + str(index + 1), 'uuid': room_id})

        # Clean out the cache
        for player in self.players:
            player.get_received()

        self.room_id = room_id

    def start_game(self):
        """ Start the game with the setup """
        # Game starts
        p_1 = self.players[0]
        p_2 = self.players[1]
        p_1.emit(constants.START_SETUP)

        received = p_1.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {'state': constants.STATE_SETUP, 'uuid': self.room_id}

        # Test it with one other player. We can assume that this 1 player will represent the others
        received = p_2.get_received()
        assert received[0]['name'] == constants.GAME_LISTENER
        assert received[0]['args'][0] == {'state': constants.STATE_SETUP, 'uuid': self.room_id}

        # Clean out the cache
        for player in self.players:
            player.get_received()

        # Start with vanilla gameplay
        p_1.emit(constants.START_GAME, {'special_characters': []})

        players_role = []

        for player in self.players:
            received = player.get_received()
            assert received[0]['name'] == constants.GAME_LISTENER
            assert 'role' in received[0]['args'][0]
            role = received[0]['args'][0]['role']
            assert received[0]['args'][0] == {
                'state': constants.STATE_BEGIN,
                'uuid': self.room_id, 'role': role
            }
            players_role.append(role)

        # Should not exceed the maximum amount
        assert players_role.count(constants.MINION) == PLAYER_SPLIT[self.num_players][0]

        for i in range(0, len(self.players) - 1):
            self.players[i].emit(constants.ACCEPT_ROLE)

        for player in self.players:
            player.get_received()

        self.players[-1].emit(constants.ACCEPT_ROLE)

        for index, player in enumerate(self.players):
            received = player.get_received()
            assert received[0]['name'] == constants.GAME_LISTENER
            assert 'team_leader' in received[0]['args'][0]
            team_leader_name = received[0]['args'][0]['team_leader']
            assert received[0]['args'][0] == {
                'state': constants.STATE_DAY,
                'uuid': self.room_id,
                'team_leader': team_leader_name
            }

            if ('player-' + str(index + 1)) == team_leader_name:
                team_leader = player

        self.team_leader = team_leader
        self.players_role = players_role

    def clean_cache(self):
        """ Clean the list of code received from the player """
        for player in self.players:
            player.get_received()

    def clean_votes(self):
        """ Check the votes to see if the action was valid """
        for index, player in enumerate(self.players):
            received = player.get_received()
            assert received[0]['name'] == constants.GAME_LISTENER
            assert 'team_leader' in received[0]['args'][0]
            new_leader = received[0]['args'][0]['team_leader']
            if ('player-' + str(index + 1)) == new_leader:
                self.update_leader(player)

    def get_minions(self):
        """ Return the list of players that are minions """
        minions = []
        for player in self.players:
            if ROOMS[self.room_id].roles[player.sid] == 'minion':
                minions.append(CLIENTS[player.sid].name)
        return minions

    def get_servants(self):
        """ Return the list of players that are servants of Arthur """
        servants = []
        for player in self.players:
            if ROOMS[self.room_id].roles[player.sid] == 'servant':
                servants.append(CLIENTS[player.sid].name)
        return servants

    def update_leader(self, new_leader):
        """ Update the leadership """
        self.team_leader = new_leader

    def quest_add_player(self, player_name):
        """ Add a player to the quest via their name and then test it works """
        existing_players = []
        for player in ROOMS[self.room_id].quest_team:
            existing_players.append(player.name)

        self.team_leader.emit(constants.PICK_PLAYER, {'player': player_name})
        existing_players.append(player_name)

        for player in self.players:
            received = player.get_received()
            assert received[0]['name'] == constants.GAME_LISTENER
            assert received[0]['args'][0] == {
                'state': constants.STATE_DAY,
                'uuid': self.room_id,
                'picked_players': existing_players
            }

    def quest_remove_player(self, player_name):
        """ Remove from a player from the quest team via their name and then test it works """
        self.team_leader.emit(constants.UNPICK_PLAYER, {'player': player_name})

        for player in self.players:
            received = player.get_received()
            assert received[0]['name'] == constants.GAME_LISTENER
            assert received[0]['args'][0] == {
                'state': constants.STATE_DAY,
                'uuid': self.room_id,
                'picked_players': ROOMS[self.room_id].get_quest_team_names()
            }

    def quest_confirm_team(self, test_players=None):
        """
            Get the team leader to confirm the quest and check the data sent to the players
            test_players: list
                Set of player names to test if the server is sending the correct players' name to
                the players
        """
        self.team_leader.emit(constants.CONFIRM_TEAM)

        if test_players:
            for player in self.players:
                received = player.get_received()
                assert received[0]['name'] == constants.GAME_LISTENER
                data = received[0]['args'][0]
                assert 'picked_players' in data
                assert data['picked_players'] == test_players, "The server did not return the correct list of players"
                assert data == {
                    'state': constants.STATE_VOTE_TEAM,
                    'uuid': self.room_id,
                    'picked_players': test_players
                }

    def quest_vote_team(self, player_name, vote):
        """
            Get a player to vote for the team
            vote: bool
                Whether the player approves or disapproves of the team
        """
        for player in self.players:
            if CLIENTS[player.sid].name == player_name:
                player.emit(constants.VOTE_TEAM, {'vote': vote})
                break

    def quest_succeed_mission(self, player_name, vote):
        """
            Get a player to act on a quest
            vote: bool
                Whether the player succeeds or fails the quest
        """
        for player in self.players:
            if CLIENTS[player.sid].name == player_name:
                player.emit(constants.PERFORM_QUEST, {'vote': vote})
                break

    def disconnect(self):
        """ Disconnect the players """
        for player in self.players:
            player.disconnect()
