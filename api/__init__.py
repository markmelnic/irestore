from os import getenv
import requests, json
from flask import Flask, request, redirect
from .init_amo import client
from .envars import *

app = Flask(__name__)

AMO = client()
PIPELINE = 3944278

@app.route('/api/init')
def init():
    code = request.args.get('code')

    if code:
        url = "https://irestoremoldova.amocrm.ru/oauth2/access_token"

        #payload = json.loads("""{
        #    'client_id': %s,
        #    'client_secret': %s,
        #    'grant_type':'authorization_code',
        #    'code': %s,
        #    'redirect_uri': %s
        #}""" % (getenv('CLIENT_ID'), getenv('CLIENT_SECRET'), getenv('NEW_CODE'), getenv('REDIRECT')))
        #print(payload)
        payload="{\"client_id\":\"84160251-089e-4ffc-8545-048f8f2d7a1f\",\n\"client_secret\":\"fAGSAc3CJdaLKCOhGEhn6oHUdhhXHvdKF5nCGOSJd3yICCIgcuFlpnDpWNnE8eGU\",\n\"grant_type\":\"authorization_code\",\n\"code\":\""+code+"\",\n\"redirect_uri\":\"https://api-irestore.mdhtcdn.net/api/init\"\n}"

        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'user_lang=ru'
        }

        res = requests.post(url, headers=headers, data=payload)
        tokens = json.loads(res.content.decode('utf8'))
        with open("access_token.txt", "w") as _:
            _.write(tokens['access_token'])
        with open("refresh_token.txt", "w") as _:
            _.write(tokens['refresh_token'])

        global AMO
        AMO = client()
        return {"status": "Nice"}
    else:
        return {"status": "Bad"}

@app.route('/api/redirect')
def api_redirect():
    return redirect('https://www.amocrm.ru/oauth?client_id='+getenv('CLIENT_ID')+'&state='+getenv('REDIRECT')+'&mode=post_message')

@app.route('/api/order')
def order():
    url = "https://a59b86043473feded6627533f30ec1fe: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@irestoremd.myshopify.com/admin/api/2021-01/orders.json"

    headers = {
    'Cookie': '_secure_admin_session_id=88639c77e66d62c035e544f4e532161d; _secure_admin_session_id_csrf=88639c77e66d62c035e544f4e532161d; _y=42b3b466-00aa-40cf-990d-e1ba0fe69b9b; _shopify_y=42b3b466-00aa-40cf-990d-e1ba0fe69b9b; _shopify_fs=2021-02-10T16%3A42%3A07Z; _s=0415647a-7a8c-46e3-9f42-972740946a3f; _shopify_s=0415647a-7a8c-46e3-9f42-972740946a3f'
    }

    res = requests.get(url, headers=headers)
    data = json.loads(res.content.decode('utf8'))

    order = json.loads(open("results.json", "r").read())
    products = order['line_items']
    price = order['total_price']
    phone = order['phone']
    email = order['contact_email']
    name = order['name']
    address = order['billing_address']

    AMO.create_leads([{
        'name': name,
        'price': price,
        'pipeline_id': PIPELINE,
        'custom_fields_values': [
            {
                "field_id": 100,
                "values": [{"name": name}]
            },
            {
                "field_id": 101,
                "values": [{"phone": phone}]
            },
            {
                "field_id": 102,
                "values": [{"email": email}]
            },
            {
                "field_id": 103,
                "values": [{"address": address}]
            },
            {
                "field_id": 104,
                "values": [{"title": p['title'], "sku": p['sku']} for p in products]
            },
        ],
    }])

    return data

@app.route('/api/inventory')
def inventory():
    pass
