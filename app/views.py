import os
import time
from flask import *
from app import app, temp_codes
from app.utils import *
from app.models import *
from flask_login import login_required, current_user, login_user, logout_user

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response 

"""@app.route('/send')
def send():
    for i in User.query.all():
        push_notification(i.id, "Biblia")"""

@app.route('/profile')
@login_required
def profile():
    achieves_users = GetAchieve.query.filter(GetAchieve.user == current_user.id).all()
    achieves = [i for i in Achievement.query.all() if i.id in [j.achieve for j in achieves_users]]
    payments = GameDeal.query.filter_by(user=current_user.id).all()
    return render_template('my_profile.html', achievements=achieves, payments=payments)


@app.route('/')
def index_page():
    return render_template('main.html')

@app.route('/sw')
def service_worker():
    return send_file(app.config['PATH_TO_APP']+('app/static/sw.js'), mimetype='application/javascript')

@app.route('/game<id_>')
def game_page(id_):
    obj = db.session.query(Game).get(id_)
    if obj == None: 
        return Response(status=404)
    if'Android' in str(request.user_agent):
        return render_template('game_mobile.html', obj=obj)
    return render_template('game.html', obj=obj)

@app.route('/mobile/game<id_>')
def mobile(id_):
    return render_template('game_mobile.html', obj=db.session.query(Game).get(id_))

@app.route('/game/photo/<id_>')
def game_photo(id_):
    return send_file(app.config['PATH_TO_APP']+(f'photos/{Game.query.get(id_).photo_name}'))

@app.route('/game/donwload/<id_>')
def game_apk(id_):
    name = Game.query.get(id_).apk_name
    return send_file(app.config['PATH_TO_APP']+(f'applications/{name.split(".")[:-1]}.apk'), as_attachment=True, attachment_filename=name)


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    print(request.form)
    print(request.args)
    try:
        obj = NotificationSubscription(
            subscriptiondata=request.form.get('object'),
            userdata = current_user.id
        )
        db.session.add(obj)
        db.session.commit()
        return 'ok'
    except:
        return 'neok'

@app.route('/send')
def test():
    for i in NotificationSubscription.query.all():
        user_subscription = NotificationSubscription.query.filter_by(userdata=i.userdata).first()
        try:
            webpush(
                subscription_info=json.loads(user_subscription.subscriptiondata),
                data="test",
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

@app.route("/docs")
def docs():
    return render_template('docs.html')

@app.route("/friend/add/<int:id_>")
@login_required
def add_friend(id_):
    if id_ == current_user.id:
        return Response(status=412)
    elif Friend.query.filter((Friend.user_1 == current_user.id or Friend.user_2 == current_user.id) and (Friend.user_1 == id_ or Friend.user_2 == id_)).first(): #если дружба между ними уже есть
        return Response(status=409) #вернуть ошибку что состояние сервера уже это включает
    elif FriendRequest.query.filter(FriendRequest.waiter==current_user.id and FriendRequest.decisiver==id_).first(): #если ровно такой же запрос есть
        return Response(status=409) #вернуть ошибку что сервер уже отправил это запрос
    elif FriendRequest.query.filter(FriendRequest.waiter==id_ and FriendRequest.decisiver==current_user.id).first(): #если был запрос на дружбу от того кого мы хотим добавить в друзья
        db.session.delete(FriendRequest.query.filter(FriendRequest.waiter==id_ and FriendRequest.decisiver==current_user.id).first()) #удалить запрос на дружбу
        db.session.add(Friend(user_1=id_, user_2=current_user.id)) #создать дружбу между принявшим заявку и отправившим
    else:
        db.session.add(FriendRequest(waiter=current_user.id, decisiver=id_)) #создать запрос на дружбу
    db.session.commit()
    return '1'

@app.route('/friend/notify')
def notifications():
    return render_template('notifications.html')

@app.route('/api/notifications_friends')
@login_required
def friend_requests():
    print(current_user.id)
    return jsonify([i.json() for i in FriendRequest.query.filter_by(decisiver=current_user.id).all()])

@app.route('/achievement/<id_>')
def get_achievement(id_):
    return render_template('achievement.html', obj=Achievement.query.get(id_))

@app.route('/game/achievement/<id_>')
def all_achievements(id_):
    game = Game.query.get(id_)
    achieves = Achievement.query.filter(Achievement.game == game.id).all()
    return render_template('achieves.html', name_game=game.name, achieves=achieves)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect('/')
    if request.method == 'POST':
        user = User.query.filter_by(nick=request.form.get('name')).first()
        if not user or not user.check_password(request.form.get('pass')):
            flash('Неправильный ник или пароль')
            return redirect('/login')
        '''if request.form.get('rememberme'):
            login_user(user, remember=True)
        else:'''
        login_user(user)
        return redirect('/')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect('/')
    if request.method == 'POST':
        if User.query.filter_by(nick=request.form.get('name')).first():
            flash('Такой пользователь уже существует')
            return redirect('/register')
        user = User(nick=request.form.get('name'), email=request.form.get('email'))
        user.set_password(request.form.get('pass'))
        db.session.add(user)
        db.session.commit()
        flash('Спасибо за регистрацию! Авторизируйтесь')
        return redirect('/login')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из своего аккаунта")
    return redirect('/login')

@app.route('/vk_entrypoint')
def vk_oauth_handler():
    if request.args:
        user = User.query.filter_by(vk_id=request.args.get('user_id')).first()
        if user:
            temp_codes.update({user.id: request.args.get('access_token')})
            login_user(user)
            return redirect('/')
        else:
            flash('Аккаунта, привязанного к этой учетной записи ВК, не существует')
            return redirect('/register')
    return render_template('vk_code.html')