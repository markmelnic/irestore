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

        res = requests.post(url, headers=headers, data=payload)
        tokens = json.loads(res.content.decode('utf8'))
        Tokens.access_token = tokens['access_token']
        Tokens.refresh_token = tokens['refresh_token']
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
    if data:
        pass
    else:
        # test file
        res = json.loads(open("results.json", "r").read())
        products = res['line_items']
        price = int(float(res['total_price']))
        phone = str(res['phone'])
        email = str(res['contact_email'])
        name = str(res['name'])
        address = str(res['billing_address'])

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
    if data:
        pass
    else:

        products = SPF.get_products()['products']

        for prod in products:
            for inv in prod['variants']:
                id = inv['inventory_item_id']

        return SPF.get_inventory_levels(item_id=id)
    return redirect(url_for('pos'))
