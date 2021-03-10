from os import getenv
import requests, json
from flask import request, redirect, url_for

from api import *
from .models import Tokens

@app.route('/api/pos')
def pos(): return {"status": "Nice"}

@app.route('/api/neg')
def neg(): return {"status": "Bad"}

@app.route('/api/init')
def init():
    code = request.args.get('code')
    if code:
        url = "https://irestoremoldova.amocrm.ru/oauth2/access_token"
        payload="{\"client_id\":\"84160251-089e-4ffc-8545-048f8f2d7a1f\",\n\"client_secret\":\"fAGSAc3CJdaLKCOhGEhn6oHUdhhXHvdKF5nCGOSJd3yICCIgcuFlpnDpWNnE8eGU\",\n\"grant_type\":\"authorization_code\",\n\"code\":\""+code+"\",\n\"redirect_uri\":\"https://api-irestore.mdhtcdn.net/api/init\"\n}"

        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'user_lang=ru'
        }

        data = requests.post(url, headers=headers, data=payload)
        tokens = json.loads(data.content.decode('utf8'))
        db_tokens = Tokens.query.first()
        db_tokens.access_token = tokens['access_token']
        db_tokens.refresh_token = tokens['refresh_token']
        db.session.commit()

        global AMO
        AMO = client()

        return redirect(url_for('pos'))
    else:
        return redirect(url_for('neg'))

@app.route('/api/redirect')
def api_redirect():
    return redirect('https://www.amocrm.ru/oauth?client_id='+getenv('CLIENT_ID')+'&state='+getenv('REDIRECT')+'&mode=post_message')

@app.route('/api/order')
def order():
    data = request.get_data()
    if not data:
        data = json.loads(open("results.json", "r").read())

    products = data['line_items']
    price = int(float(data['total_price']))
    phone = str(data['phone'])
    email = str(data['contact_email'])
    name = str(data['name'])
    address = str(data['billing_address'])

    objects = [{
        'name': name,
        'price': price,
        'pipeline_id': PIPELINE,
        'custom_fields_values': [
                {
                "field_id": 0,
                "values": [{
                    "text": name,
                    "phone": phone,
                    "email": email,
                    "address": address,
                    "products": [{"title": str(p['title']), "sku": str(p['sku'])} for p in products]
                }],
            },
        ],
    }]
    #print(objects)

    AMO.create_leads_custom_fields()
    AMO.create_leads(objects)

    return redirect(url_for('pos'))

@app.route('/api/inventory')
def inventory():
    data = request.get_data()
    if not data:
        data = json.loads(open("inventory.json", "r").read())

    id = data['inventory_item_id']

    left = SPF.get_inventory_levels(item_id=id)['inventory_levels'][0]['available']
    if int(left) in [5, 10]:
        print(TelegramUsers.query.filter_by(status=True).all())
        for user in TelegramUsers.query.filter_by(status=True).all():
            TELEGRAM.send_message("There are %s items left" % (left), user.user_id)

    return SPF.get_inventory_levels(item_id=id)
    return redirect(url_for('pos'))

@app.route('/api/telegram/add/<user_id>')
def telegram_add(user_id):
    dish = TelegramUsers(
        user_id = user_id
    )
    db.session.add(dish)
    db.session.commit()

    return redirect(url_for('pos'))

@app.route('/api/telegram/del/<user_id>')
def telegram_del(user_id):
    user = TelegramUsers.query.filter_by(user_id=user_id).first()
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('pos'))

@app.route('/api/telegram/toggle/<user_id>')
def telegram_toggle(user_id):
    user = TelegramUsers.query.filter_by(user_id=user_id).first()
    if user.status:
        user.status = False
    else:
        user.status = True
    db.session.commit()

    return redirect(url_for('pos'))
