from app.models import *
from app.utils import *
from flask import *
from app import app
import time


METHODS = ['left', 'right', 'forward', 'back', 'shoot_in', 'shoot_out', 'win1', 'win2']


class Event():
    def __init__(self, method_type, owner):
        self.owner = owner
        if method_type in METHODS:
            self.method = method_type
        else:
            raise TypeError('Method type is not allowed')
        self.timestamp = time.time()
    @property
    def prioritet(self) -> int : 
        if self.method in ('win1', 'win2'): return 3
        elif self.method in ('shoot_in', 'shoot_out'): return 2
        elif self.method in ('left', 'right', 'forward', 'back'): return 10
        else: return 0

class GameState():
    def __init__(self):
        self.user1, self.user2 = -1, -1
        self.status = 'wait'

        self.user1_time = time.time()
        self.user2_time = time.time()

        self.events = []
        self.health_u1 = 100
        self.health_u2 = 100

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
    if not lobby.get(name_room, False): return Response(status=404)
    if not 'nullplayer' in lobby[name_room].nicks: return Response(status=423)
    if User.query.get(token.user).nick in lobby[name_room].nicks: return Response(status=409)
    lobby[name_room].set_user(token.user)
    return '1'

@app.route('/api/game/cs/lobby/all')
@token_required
def all_rooms():
    return '\n'.join(lobby.keys())

@app.route('/api/game/cs/status')
@token_required
def get_room(game, token):
    game_state = room(token.user)
    try:
        name = list(game_state.keys())[0]
        game_state = game_state[name]
    except:
        return Response(status=404)
    #print(game_state.user_status)
    res = '\n'.join([name, 
                     game_state.nicks[0], 
                     game_state.nicks[1], 
                     game_state.status])
    return res

@app.route('/api/game/cs/ready')
@token_required
def set_ready(game, token):
    game_state = room(token.user)
    try:
        name = list(game_state.keys())[0]
        game_state = game_state[name]
    except:
        return Response(status=423)
    user_id = game_state.user_id(token.user)
    print(user_id)
    if user_id == 1 and game_state.user2 != -1:
        game_state.status = 'ready'
        return '1'
    else:
        return Response(status=423)

@app.route('/api/game/cs/exit')
@token_required
def exit_room(game, token):
    game_state = room(token.user)
    try:
        name = list(game_state.keys())[0]
        game_state = game_state[name]
    except:
        return Response(status=423)
    user_id = game_state.user_id(token.user)
    if user_id == 1: game_state.user1, game_state.user2 = game_state.user2, -1
    elif user_id == 2: game_state.user2 = -1
    if game_state.user1 == -1 and game_state.user2 == -1: del lobby[name]
    return '1'

@app.route('/api/game/cs/operate/<method>')
@token_required
def operate_method(method, game, token):
    game_state = room(token.user)
    try:
        name = list(game_state.keys())[0]
        game_state = game_state[name]
    except:
        return Response(status=423)
    user_id = game_state.user_id(token.user)
    invert_id = 2 if user_id == 1 else 1
    
    try:
        game_state.events.append(Event(method, user_id))
        if method == 'shoot_in':
            exec(f'state.health_u{invert_id} -= 10', {'state': game_state})
            if eval(f'state.health_u{invert_id}', {'state': game_state}) == 0:
                game_state.events.append(Event(f'win{user_id}', user_id))
    except TypeError:
        return Response(status=406)

    return '1'

@app.route('/api/game/cs/lastevents')
@token_required
def last_events(game, token):
    game_state = room(token.user)
    try:
        name = list(game_state.keys())[0]
        game_state = game_state[name]
    except:
        return Response(status=423)
    user_id = game_state.user_id(token.user)
    invert_id = 2 if user_id == 1 else 1

    last_time:float = game_state.user1_time if user_id == 1 else game_state.user2_time
    now = time.time()

    events = list(filter(lambda x: x.owner == invert_id and now>x.timestamp>last_time, game_state.events))
    events = sorted(events, key=lambda x: x.prioritet)

    if user_id == 1: 
        game_state.user1_time = now
    else:
        game_state.user2_time = now

    return '\n'.join([event.method for event in events])