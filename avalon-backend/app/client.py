from . import constants


class Client:
    def __init__(self, name, sid):
        self.name = name
        self.sid = sid
        self.room_id = None
        self.kick = 0

    def assign_room(self, room_id):
        self.room_id = room_id
