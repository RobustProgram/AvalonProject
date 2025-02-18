from . import constants, CLIENTS
from .client import Client


EMPTY_ROOM = {
    'uuid': '',
    'host': '',
    'state': '',
    'players': []
}


class Room:
    def __init__(self, uuid, host):
        self.uuid = uuid
        self.host = host
        self.state = constants.LOBBY

        self.roles = {}
        self.players = [host]
        self.players_accepted = []

        self.quest_team = []
        self.quest_day = 0
        self.quests = [None, None, None, None, None]
        self.quest_leader = -1

    def add_player(self, player):
        if isinstance(player, Client):
            self.players.append(player)
        else:
            raise RuntimeError('You can only add a Client object')

    def remove_player(self, player):
        self.players.remove(player)

        if len(self.players) > 0:
            if player == self.host:
                self.host = self.players[0]

    def remove_player_using_sid(self, sid):
        player_object = CLIENTS[sid]

        self.players.remove(player_object)

        if len(self.players) > 0:
            if player_object == self.host:
                self.host = self.players[0]

    def get_player_names(self):
        player_names = []

        for player in self.players:
            player_names.append(player.name)

        return player_names

    def add_accepted_player(self, player):
        if isinstance(player, Client):
            self.players_accepted.append(player)
        else:
            raise RuntimeError('You can only add a Client object')

    def get_accepted_player_names(self):
        player_names = []

        for player in self.players_accepted:
            player_names.append(player.name)

        return player_names

    def get_quest_team_names(self):
        player_names = []

        for player in self.quest_team:
            player_names.append(player.name)

        return player_names

    def get_quest_leader_name(self):
        if len(self.players) > 0:
            if self.quest_leader >= len(self.players):
                self.quest_leader = 0
            return self.players[self.quest_leader].name
        return ''

    def advance_quest(self, success):
        self.quests[self.quest_day] = success
        self.quest_day += 1

    def get_room_data_for_client(self):
        return {
            'uuid': self.uuid,
            'host': self.host.name,
            'state': self.state,
            'players': self.get_player_names()
        }
