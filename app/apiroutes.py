import datetime
from flask import *
from app.utils import *
from app.models import *
from app import app, temp_token


@app.route('/api/login/token/<int:secret_value>')
def _token(secret_value):
    print(secret_value, type(secret_value))
    for i in Game.query.all():
        print(i.secret_product, type(i.secret_product))
        if i.secret_product == secret_value:
            game_for = i
            break
    #game_for = Game.query.filter(Game.secret_product == int(secret_value)).first()
    if not game_for: return '401'
    token = str(game_for.secret_value_under*random.randint(0, 1000)+game_for.secret_value_top) + '\n' + generate_token()
    temp_token[token.replace('\n', ':')] = (str(request.user_agent), game_for)
    return token

@app.route('/api/login', methods=['GET', 'POST'])
def login_for_apps():
    if request.method == 'POST':
        user = User.query.filter_by(nick=request.form.get('name')).first()
        if not user or not user.check_password(request.form.get('pass')):
            flash('Неправильный ник или пароль')
            return redirect(f'/api/login?token={request.args.get("token")}')
        try:
            token = request.args.get("token")
            db.session.add(
                Token(
                    token = token.split(':')[1],
                    sequence_seed = int(token.split(':')[0]),
                    useragent = temp_token[token][0],
                    address = request.remote_addr,
                    date = str(datetime.date.today()),
                    user = user.id,
                    game = temp_token[token][1].id,
                    secret_key = (int(token.split(':')[0]) - temp_token[token][1].secret_value_top) // temp_token[token][1].secret_value_under
                )
            )
        except KeyError:
            print(temp_token)
            flash('Токен сгенерирован не на странице сервера')
            return redirect(f'/api/login?token={request.args.get("token")}')
        except Exception as ex:
            print(ex)
            flash('Ваш токен уже существует')
            return redirect(f'/api/login?token={request.args.get("token")}')
        db.session.commit()
        return redirect('/buddy_apps')
    return render_template('login.html', token=request.args.get('token'))

@app.route('/buddy_apps')
def buddy():
    return render_template('buddy.html')


@app.route('/api/user')
@token_required
def get_user(game, token):
    return User.query.get(token.user).nick

@app.route('/api/get_achievement/<id_>')
@token_required
def throw_achievement(id_, game, token):
    user = User.query.get(token.user)
    achieve = Achievement.query.get(id_)
    obj = GetAchieve(
        user = user.id,
        achieve = achieve.id
    )
    db.session.add(obj)
    db.session.commit()

@app.route('/api/set_data/<key>/<value>')
@token_required
def set_data_for_user(game, key, value, token):
    if not Game.query.get(game): return 'none'
    user = User.query.get(token.user)
    if db.session.query(GameDictonary).filter_by(game=game, user=user.id, key=key).count() < 1:
        row = GameDictonary(user=user.id,
                            game=game,
                            key=key,
                            value=value)
        db.session.add(row)   
    else:
         row = db.session.query(GameDictonary).filter_by(game=game, user=user.id, key=key).first()
         row.value = value
    db.session.commit()
    return 'ok'

@app.route('/api/get_data/<key>')
@token_required
def get_data_for_user(key, game, token):
    user = User.query.get(token.user)
    row = db.session.query(GameDictonary).filter_by(game=game, user=user.id, key=key).first()
    return row.value if row else 'none'