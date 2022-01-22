import json
import datetime
from app import app
import random, string
from app.models import *
from pywebpush import webpush, WebPushException
from flask import redirect, flash, request, Response
from flask_login import login_required, current_user


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
        tok = Token.query.get(request.args.get('token')) 
        if tok and tok.date == str(datetime.date.today()) and tok.address == request.remote_addr and tok.useragent == str(request.user_agent):
            try:
                return func(*args, **kwargs, token=tok)
            except TypeError:
                return func(*args, **kwargs)
            except Exception as ex:
                print(ex)
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