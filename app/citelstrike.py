from re import S
from app.models import *
from app.utils import *
from flask import *
from app import app


class GameState():
    def __init__(self):
        self.user1, self.user1_status = -1, 'wait'
        self.user2, self.user2_status = -1, 'wait'
    def set_user(self, id_):
        if self.user1 < 0:
            self.user1 = id_
        elif self.user2 < 0:
            self.user2 = id_
        else:
            raise ValueError('Not space for new player')
    def user_id(self, id_):
        if self.user1 == id_: return 1
        elif self.user2 == id_: return 2
        else: return -1
    def in_match(self, id_):
        return self.user1 == id_ or self.user2 == id_
    @property
    def nicks(self):
        return (User.query.get(self.user1).nick, User.query.get(self.user2).nick if User.query.get(self.user2) else 'nullplayer')
    @property
    def status(self):
        if self.user1_status == 'ready':
            if self.user2_status == 'ready':
                return 'ready'
        return 'wait'    
    def __repr__(self):
        return '\n'.join([self.nicks[0], 
                          self.nicks[1], 
                          self.status])

lobby = {}
def room(user):
    #print(1)
    for name, state in lobby.items():
        #print(2)
        if state.in_match(user):
            return {name: state}
    return None


@app.route('/api/game/cs/lobby/new/<name_room>')
@token_required
def new_lobby_room(name_room, game, token):
    lobby[name_room] = GameState()
    lobby[name_room].set_user(token.user)
    return '1'

@app.route('/api/game/cs/lobby/enter/<name_room>')
@token_required
def enter_room(name_room, game=None, token=None):
    #print(lobby.get(name_room, False))
    if not lobby.get(name_room, False): return Response(404)
    if not 'nullplayer' in lobby[name_room].nicks: return Response(status=423)
    if User.query.get(token.user).nick in lobby[name_room].nicks: return Response(status=409)
    lobby[name_room].set_user(token.user)
    return '1'

@app.route('/api/game/cs/lobby/all')
@token_required
def all_rooms():
    return '\n'.join(lobby.keys())

@app.route('/api/game/cs/lobby/status/<id_text>')
@token_required
def get_room(id_text, game, token):
    game_state = lobby[id_text]
    if not game_state: return Response(status=404)
    #print(game_state.user_status)
    res = '\n'.join([id_text, 
                     game_state.nicks[0], 
                     game_state.nicks[1], 
                     game_state.status])
    return res

@app.route('/api/game/cs/ready')
@token_required
def set_ready(game, token):
    game_state = room(token.user)
    name = list(game_state.keys())[0]
    game_state = game_state[name]
    user_id = game_state.user_id(token.user)
    print(user_id)
    if user_id > 0:
        if user_id == 1:  game_state.user1_status = 'ready'
        elif user_id == 2:  game_state.user2_status = 'ready'
        return '1'
    else:
        return Response(status=423)