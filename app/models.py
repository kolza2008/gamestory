from app import db, lm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    nick = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(365))
    email = db.Column(db.String(96))
    vk_id = db.Column(db.Integer(), default=(-1))
    role = db.Column(db.Integer(), default=0)
    @property
    def json(self):
        return {
            'id': self.id,
            'username': self.nick,
            'is_admin': self.role > 0
        }
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self,  password):
	    return check_password_hash(self.password_hash, password)

@lm.user_loader
def user_loader(id_):
    return db.session.query(User).get(id_)

class Game(db.Model):
    __tablename__ = 'content' 
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    name = db.Column(db.String(20), nullable=False)
    version = db.Column(db.String(20), default='1.0')
    timestamp = db.Column(db.Integer())
    description = db.Column(db.String(365), nullable=False)
    photo_name = db.Column(db.String(20), nullable=False)
    apk_name = db.Column(db.String(20), nullable=False)

    secret_value_under = db.Column(db.Integer())
    secret_value_top = db.Column(db.Integer())
    @property
    def secret_product(self):
        return self.secret_value_under * self.secret_value_top
    @property
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'timestamp': self.timestamp,
            'description': self.description,
            'photo_name': self.photo_name,
            'apk_name': self.apk_name
        }

class Token(db.Model):
    __tablename__ = 'tokens'
    token = db.Column(db.String(20), primary_key=True)
    date = db.Column(db.String(15))
    address = db.Column(db.String(15))
    useragent = db.Column(db.String(128))
    user = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    game = db.Column(db.Integer(), db.ForeignKey('content.id', ondelete='CASCADE'))
    sequence_seed = db.Column(db.Integer())
    secret_key = db.Column(db.Integer())
    sequence_member = db.Column(db.Integer(), default=1)
    @property
    def secret_keys(self):
        game = Game.query.get(self.game)
        return (game.secret_value_under, game.secret_value_top, self.secret_key)

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    name = db.Column(db.String(24))
    description = db.Column(db.String(64))
    game = db.Column(db.Integer(), db.ForeignKey('content.id', ondelete='CASCADE'))
    def __repr__(self):
        return f'Ачивка {self.id}'
    #screenshot = db.Column(db.String(128))

class GetAchieve(db.Model):
    __tablename__ = 'achieves'
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    user = db.Column(db.Integer(), db.ForeignKey('users.id'))
    achieve = db.Column(db.Integer(), db.ForeignKey('achievements.id', ondelete='CASCADE'))
    def __repr__(self):
        return f'Пользователь {self.user} получил ачивку {self.achieve}'

class NotificationSubscription(db.Model):
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    subscriptiondata = db.Column(db.String(512))
    userdata = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))

class GameDictonary(db.Model):
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    game = db.Column(db.Integer(), db.ForeignKey('content.id', ondelete='CASCADE'))
    user = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    key = db.Column(db.String(64))
    value = db.Column(db.String(64))

class Friend(db.Model):
    __tablename__ = "friends"
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    user_1 = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    user_2 = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))

class FriendRequest(db.Model):
    __tablename__ = "friendrequests"
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    waiter = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    decisiver = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    def json(self):
        return {
            'id': self.id,
            'waiter': self.waiter,
            'decisiver': self.decisiver
        }