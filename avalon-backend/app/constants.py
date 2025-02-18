""" Centralise all of the event calls into a single file """
# General Constants
SYS_MESSAGE = 'sys_message'

# Room Constants
CREATE_ROOM = 'create_room'
CREATE_ROOM_LISTENER = 'create_room_listener'
JOIN_ROOM = 'join_room'
LEAVE_ROOM = 'leave_room'
ROOM_LISTENER = 'room_listener'

# Room Command Constants
KICK_PLAYER = 'kick_player'

# ## Game constants
LOBBY = 'lobby'
GAME_LISTENER = 'game_listener'

# Pre game constants
START_SETUP = 'start_setup'
START_GAME = 'start_game'
ACCEPT_ROLE = 'accept_role'

# Game constants
PICK_PLAYER = 'pick_player'
UNPICK_PLAYER = 'unpick_player'
PICK_TEAM = 'pick_team'
CONFIRM_TEAM = 'confirm_team'
VOTE_TEAM = 'vote_team'
PERFORM_QUEST = 'perform_quest'

# Game state
STATE_SETUP = 'game_state_setup'
STATE_BEGIN = 'game_state_begin'
STATE_DAY = 'game_state_day'
STATE_VOTE_TEAM = 'game_state_vote_team'
STATE_QUEST = 'game_state_quest'
STATE_FINISHED = 'game_state_finished'

# ## Characters
# Evil
MORGANA = 'morgana'
ASSASSIN = 'assassin'
MORDRED = 'mordred'
OBERON = 'oberon'
MINION = 'minion'
# Good
PERCIVAL = 'percival'
MERLIN = 'merlin'
SERVANT = 'servant'
