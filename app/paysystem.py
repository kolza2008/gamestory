import time
import datetime
import requests
from flask import *
from app import app, db
from app.utils import *
from app.models import *
from flask_login import login_required, current_user


@app.route('/pay/game') 
@login_required
def pay_to_game():
    if GameDeal.query.filter(GameDeal.game==request.args.get('id') and GameDeal.user==current_user.id and (GameDeal.status=='WAITING' or GameDeal.status=='PAID')).first() != None:
        return Response(status=409)
    
    game_id = request.args.get('id')
    key_in_qiwi = f'game_{current_user.id}{game_id}'

    game = Game.query.get(game_id)

    if game == None: return Response(status=404)
    if game.price == 0.0: return Response(status=400)

    date = datetime.datetime.now() + datetime.timedelta(days=7)
    date_expired = datetime.datetime.strftime(date, '%Y-%m-%dT%H:%M:%S±03:00')

    deal = GameDeal(key_in_qiwi=key_in_qiwi,
                    status='WAITING',
                    user=current_user.id,
                    game=game.id, 
                    timestamp=time.time())
    db.session.add(deal)
    db.session.commit()

    #obj = requests.put()
    return redirect('/')

@app.route('/pay/notify')
def notify_about_bill():
    billdata = request.form.get('bill')
    if billdata['billid'].split('_')[0] == 'game':
        deal = GameDeal.query.get(billdata['customFields']['deal_id'])
        if deal.status == billdata['status']['value']:
            return 
        deal.status = billdata['status']['value']
        if deal.status == 'PAID':
            purchase = GamePurchases(date=time.time(),
                                     user=deal.user,
                                     game=deal.game)
            db.session.add(purchase)
    else:
        return Response(status=400)
    db.session.commit()
    return 