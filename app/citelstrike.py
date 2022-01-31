from app.models import *
from app.utils import *
from flask import *
from app import app


class GameState():
    def __init__(self):
        self.user1 = -1
        self.user2 = -1
        self.user_status = ['wait, wait']
    def set_user(self, id_):
        if self.user1 < 0:
            self.user1 = id_
        elif self.user2 < 0:
            self.user2 = id_
        else:
            raise ValueError('Not space for new player')
    def in_match(self, id_):
        return self.user1 == id_ or self.user2 == id_
    @property
    def nicks(self):
        return (User.query.get(self.user1), User.query.get(self.user2))
    @property
    def status(self):
        return 'ready' if all([x == 'ready' for x in self.user_status]) else 'wait'    

lobby = {}
def room(user):
    for name, state in lobby:
        if state.in_match(user):
            return {name: state}
    return None


@app.route('/api/game/cs/lobby/new/<name_room>')
@token_required
def new_lobby_room(name_room, game, token):
    lobby[name_room] = GameState()
    lobby[name_room].set_user(token.user)
    return '1'

@app.route('/api/game/cs/lobby/all')
@token_required
def all_rooms():
    print(lobby.keys())
    return '\n'.join(lobby.keys())

@app.route('/api/game/cs/lobby')
@token_required
def get_room(game, token):
    game_state = room(token.user)
    name = game_state.keys()[0]
    game_state = game_state[name]
    if not game_state: return Response(status=601)
    return '\n'.join(name, game_state.nicks[0], game_state.nicks[1], game_state.user_status[0], game_state.user_status[1], game_state.status)

@app.route('/api/game/cs/ready')
@token_required
def set_ready():
    return 