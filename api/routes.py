from os import getenv
import requests, json
from flask import request, redirect, url_for

from api import *
from .models import Tokens

@app.route('/api/pos')
def pos(): return {"status": "Nice"}

@app.errorhandler(500)
@app.errorhandler(501)
@app.errorhandler(502)
@app.errorhandler(503)
@app.route('/api/neg')
def neg(e = False):
    if e:
        message = str(e)[4:].split(":")
        return {"code": e.code, "reason": message[0], "message": message[1][1:]}
    else:
        return {"status": "Bad"}

@app.route('/api/init')
def init():
    code = request.args.get('code')
    if code:
        url = "https://irestoremoldova.amocrm.ru/oauth2/access_token"

        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'user_lang=ru'
            }

        payload = {
            "client_id": getenv('CLIENT_ID'),
            "client_secret": getenv('CLIENT_SECRET'),
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://api-irestore.mdhtcdn.net/api/init" # url_for("api/init")
            }

        data = requests.post(url, headers=headers, data=json.dumps(payload))
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

@app.route('/api/redirect', methods=['GET'])
def api_redirect():
    return redirect('https://www.amocrm.ru/oauth?client_id='+getenv('CLIENT_ID')+'&state='+getenv('REDIRECT')+'&mode=post_message')

@app.route('/api/add_custom_fields')
def add_custom_fields():
    fs = ["name", "phone", "email", "address", "product", "sku"]
    fields = []
    for f in fs:
        fields.append({"type": "text", "name": f})
    print(fields)
    AMO.create_leads_custom_fields(fs)

    return redirect(url_for('pos'))

@app.route('/api/order', methods=['POST', 'GET'])
def order():
    if request.method == "POST":
        data = json.load(request.get_data())
    else:
        try:
            data = json.loads(open("results.json", "r").read())
        except FileNotFoundError:
            return redirect(url_for('neg'))

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
    print(objects)

#    AMO.create_leads_custom_fields()
    #AMO.create_leads(objects)

    return redirect(url_for('pos'))

@app.route('/api/inventory', methods=['POST', 'GET'])
def inventory():
    if request.method == "POST":
        data = json.loads(request.get_data())
    else:
        try:
            data = json.loads(open("inventory.json", "r").read())
        except FileNotFoundError:
            return redirect(url_for('neg'))
    id = data['inventory_item_id']

    products = SPF.get_products()['products']
    target = None
    for p in products:
        for v in p['variants']:
            if id == v['inventory_item_id']:
                product = p
                target = v['product_id']
                price = v['price']
                sku = v['sku']
                break
        if target:
            break

    title = f"{target} | {sku}"
    object = [{
        'name': title,
        'price': int(float(price)),
        'pipeline_id': PIPELINE,
    }]
    AMO.create_leads(object)

    left = SPF.get_inventory_levels(item_id=id)['inventory_levels'][0]['available']
    if int(left) in [5, 10]:
        print(TelegramUsers.query.filter_by(status=True).all())
        for user in TelegramUsers.query.filter_by(status=True).all():
            TELEGRAM.send_message("There are %s %s left" % (left, title), user.user_id)

    return redirect(url_for('pos'))

@app.route('/api/telegram/add/<user_id>', methods=['GET'])
def telegram_add(user_id):
    dish = TelegramUsers(
        user_id = user_id
    )
    db.session.add(dish)
    db.session.commit()

    return redirect(url_for('pos'))

@app.route('/api/telegram/del/<user_id>', methods=['GET'])
def telegram_del(user_id):
    user = TelegramUsers.query.filter_by(user_id=user_id).first()
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('pos'))

@app.route('/api/telegram/toggle/<user_id>', methods=['GET'])
def telegram_toggle(user_id):
    user = TelegramUsers.query.filter_by(user_id=user_id).first()
    if user.status:
        user.status = False
    else:
        user.status = True
    db.session.commit()

    return redirect(url_for('pos'))
