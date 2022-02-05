import os
import json
import zipfile
import datetime
from app import app
import random, string
from app.models import *
from pywebpush import webpush, WebPushException
from flask import redirect, flash, request, Response
from flask_login import login_required, current_user

def int_upg(text):
    if not 'E' in text:
        return int(text)
    else:
        parts = text.lower().split('e')
        return round(float(parts[0]) * (10 ** int(parts[1])))

        
def push_notification(user_id, data):
    user_subscription = NotificationSubscription.query.filter_by(userdata=user_id).first()
    try:
        webpush(
            subscription_info=json.loads(user_subscription.subscriptiondata),
            data=data,
            vapid_private_key='./private_key.pem',
            vapid_claims={
                        'sub': f'mailto:{app.config["ADMIN_EMAIL"]}',
            }
        )
    except WebPushException as ex:
        print('I\'m sorry, Dave, but I can\'t do that: {}'.format(repr(ex)))
        print(ex)
        # Mozilla returns additional information in the body of the response.
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print('Remote service replied with a {}:{}, {}',
                  extra.code,
                  extra.errno,
                  extra.message)

def admin_required(roletype=1):
    def decor_factory(func):
        @login_required
        def decor(*args, **kwargs):
            if current_user.role < roletype: 
                flash('Эта страница только для администраторов')
                return redirect('/login')
            else:
                return func(*args, **kwargs)
        decor.__name__ = func.__name__
        return decor
    return decor_factory

def token_required(func):
    def decor(*args, **kwargs):
        original = request.args.get('token').split(':')
        tok = Token.query.get(original[1])
        if not tok: return Response(status=418)
        if all((tok,  #token isn't none 
               tok.address == request.remote_addr, #token from same device
               tok.useragent == str(request.user_agent), #token from same origin
               int_upg(original[0]) == sequence_getter(tok.sequence_seed, tok.sequence_member, *tok.secret_keys))): #token has same transformation path
            try:
                res = func(*args, **kwargs, game=tok.game, token=tok)
                tok.sequence_member += 1
                db.session.commit()
                return res
            except TypeError:
                res =  func(*args, **kwargs)
                tok.sequence_member += 1
                db.session.commit()
                return res
            except Exception as ex:
                print(ex)
                print('МАМА Я В ТЕЛЕВИЗОРЕ')
                return Response(status=500)
        else:
            return Response(status=401)
    decor.__name__ = func.__name__
    return decor


def generate_token():
    return ''.join([random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits) for i in range(random.randint(15, 20))])


@app.context_processor
def custom_context():
    def vk_oauth_url():
        return f'https://oauth.vk.com/authorize?client_id={app.config["VK_ID"]}&redirect_uri={app.config["APP_URL"]}/vk_entrypoint&display=page&scope={app.config["VK_SCOPE"]}&response_type=token'
    return {'notify_key': app.config['NOTIFICATION_KEY'], 'VK_URL':vk_oauth_url}

def sequence_getter(seed, member, *secret_keys):
    res = seed
    for i in range(1, member):
        res = res * secret_keys[0] // secret_keys[1] - secret_keys[2]
    return res


class FileManager():
    def __init__(self, app_path, photo_path, zip_path):
        self.zip_path = zip_path
        self.app_path = app_path
        self.photo_path = photo_path
    def add_game(self, game):
        with zipfile.ZipFile(os.path.join(self.zip_path, f'{game.name.lower().replace(" ", "")}.zip'), 'x') as file:
            file.write(os.path.join(self.photo_path, game.photo_name), arcname=game.photo_name)
            file.write(os.path.join(self.app_path, game.apk_name), arcname=game.apk_name)
    def get_photo(self, game):
         with zipfile.ZipFile(os.path.join(self.zip_path, f'{game.name.lower().replace(" ", "")}.zip'), 'r') as file:
             return file.read(game.photo_name)
    def get_apk(self, game):
         with zipfile.ZipFile(os.path.join(self.zip_path, f'{game.name.lower().replace(" ", "")}.zip'), 'r') as file:
             return file.read(game.apk_name)