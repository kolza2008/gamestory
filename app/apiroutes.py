import datetime
from flask import *
from app.utils import *
from app.models import *
from app import app, temp_token


@app.route('/api/login/token')
def _token():
    token = generate_token()
    temp_token[token] = str(request.user_agent)
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
                    token = token,
                    useragent = temp_token[token],
                    address = request.remote_addr,
                    date = str(datetime.date.today()),
                    user = user.id
                )
            )
        except KeyError:
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
def get_user(token):
    return User.query.get(token.user).nick

@app.route('/api/get_achievement/<id_>')
@token_required
def throw_achievement(id_, token):
    user = User.query.get(token.user)
    achieve = Achievement.query.get(id_)
    obj = GetAchieve(
        user = user.id,
        achieve = achieve.id
    )
    db.session.add(obj)
    db.session.commit()
