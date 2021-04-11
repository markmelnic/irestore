import requests, json, hmac, hashlib, base64, random
import urllib.parse as urlparse
from os import getenv
from flask import request, redirect, url_for

from api import *
from .adj import *
from .models import Tokens

def verify_webhook(data, hmac_header):
    digest = hmac.new(getenv('SPF_SECRET').encode('utf-8'), data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

def pos(): return {"status": "Nice"}, 200

@app.errorhandler(500)
@app.errorhandler(501)
@app.errorhandler(502)
@app.errorhandler(503)
@amo_exception
@app.route('/api/neg')
def neg(e = False):
    if e:
        message = str(e)[4:].split(":")
        return {"code": e.code, "reason": message[0], "message": message[1][1:]}
    else:
        return {"status": "Bad"}

@amo_exception
@app.route('/test')
def test():
    res = SPF.get_orders()
    return res if res else pos()

@amo_exception
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
        tokens = Tokens.query.first()
        AMO = AmoOAuthClient(
            tokens.access_token,
            tokens.refresh_token,
            getenv('SUBDOMAIN'),
            getenv('CLIENT_ID'),
            getenv('CLIENT_SECRET'),
            getenv('REDIRECT')
        )

        return pos()
    else:
        return redirect(url_for('neg'))

@amo_exception
@app.route('/api/redirect', methods=['GET'])
def api_redirect():
    return redirect('https://www.amocrm.ru/oauth?client_id='+getenv('CLIENT_ID')+'&state='+getenv('REDIRECT')+'&mode=post_message')

@amo_exception
@app.route('/api/service', methods=['POST', 'GET'])
def api_service():
    parsed = urlparse.urlparse(request.url)
    id = urlparse.parse_qs(parsed.query)['leads[status][0][id]'][0]
    for c in AMO.get_leads_links(id)['_embedded']['links']:
        if c ['metadata']['main_contact']:
            contact_id = c['to_entity_id']

    contact = AMO.get_contact(contact_id)
    for field in contact['custom_fields_values']:
        if field['field_code'] == "PHONE":
            number = field['values'][0]['value']

    return "373" + number[-8:]

@amo_exception
@app.route('/api/add_custom_fields')
def add_custom_fields():
    fs = ["name", "phone", "email", "address", "product", "sku"]
    fields = {}
    fields['add'] = []
    for f in fs:
        origin_id = random.randint(1111,9999)
        fields['add'].append({
            "name": f,
            "field_type": "1",
            "element_type": "2",
            #"origin": f"{origin_id}_irestore",
            "is_editable": "0",
        })
    #print(fields)

    for f in AMO.get_leads_custom_fields()['_embedded']['custom_fields']:
        print(f)
    AMO.create_leads_custom_fields(fs)

    return pos()

@amo_exception
@app.route('/api/order/create', methods=['POST', 'GET'])
def order_create():
    if request.method == "POST":
        data = json.loads(request.get_data())
        verify = verify_webhook(request.get_data(), request.headers.get('X-Shopify-Hmac-SHA256'))
        if not verify:
            return redirect(url_for('neg'))

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
    order_url = str(data['order_status_url'])

    objects = [{
        'name': name,
        'price': price,
        'pipeline_id': PIPELINE,
    }]
    lead = AMO.create_leads(objects)

    for i, p in enumerate(products):
        try:
            color = p['variant_title']
        except KeyError:
            c = False
        prod_text = f"Produs {i + 1}\nTitle: {p['title']}\nSku: {p['sku']}"
        if color:
            prod_text += f"\nCuloarea: {color}"
        print(color, prod_text)

        objects = [
            {
                "entity_id": lead['_embedded']['leads'][0]['id'],
                "note_type": "common",
                "params": {
                    "text": prod_text,
                }
            }
        ]
        AMO.create_lead_note(objects)

    TELEGRAM.send_message("O comanda noua a fost plasata\n%s" % (order_url))

    return pos()

@amo_exception
@app.route('/api/order/update', methods=['POST', 'GET'])
def order_update():
    if request.method == "POST":
        data = json.loads(request.get_data())
        verify = verify_webhook(request.get_data(), request.headers.get('X-Shopify-Hmac-SHA256'))
        if not verify:
            return redirect(url_for('neg'))
    return pos()

@amo_exception
@app.route('/api/order/delete', methods=['POST', 'GET'])
def order_delete():
    if request.method == "POST":
        data = json.loads(request.get_data())
        verify = verify_webhook(request.get_data(), request.headers.get('X-Shopify-Hmac-SHA256'))
        if not verify:
            return redirect(url_for('neg'))

    for user in TelegramUsers.query.filter_by(status=True).all():
        TELEGRAM.send_message("Order %s has been DELETED" % (data['id']), user.user_id)
    return pos()

@amo_exception
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

    title = f"Product id: {target} | SKU: {sku}"
    object = [{
        'name': title,
        'price': int(float(price)),
        'pipeline_id': PIPELINE,
    }]
    AMO.create_leads(object)

    left = SPF.get_inventory_levels(item_id=id)['inventory_levels'][0]['available']
    if int(left) in [5, 10]:
        for user in TelegramUsers.query.filter_by(status=True).all():
            TELEGRAM.send_message("There are %s - %s - items left" % (left, title), user.user_id)

    return pos()

@amo_exception
@app.route('/api/telegram/webhook', methods=['POST'])
def respond():
    data = json.loads(request.get_data())
    user_id = int(data['message']['from']['id'])
    text = data['message']['text']

    try:
        if text == "/start":
            if not TelegramUsers.query.filter_by(user_id=user_id).first():
                user = TelegramUsers(
                    user_id = user_id
                    )
                db.session.add(user)
                db.session.commit()
                TELEGRAM.send_message("Initialisation successful, you will receive notifications. Use /help for more commands", user_id)
            else:
                TELEGRAM.send_message("You have already been initialised, you will receive notifications", user_id)

        elif text == "/help":
            help_message = """
            /help - List of commands
            /start - Initialise app and user
            /info - Receive current user information
            /delete - Remove user
            /toggle - Toggle notifications
            /dev - Receive developer notifications
            """
            TELEGRAM.send_message(help_message, user_id)

        elif text == "/info":
            user = TelegramUsers.query.filter_by(user_id=user_id).first()
            n_status = ""
            if not user.status:
                n_status = "NOT "
            TELEGRAM.send_message("You are currently %sreceiving notifications" % n_status, user_id)

        elif text == "/toggle":
            user = TelegramUsers.query.filter_by(user_id=user_id).first()
            if user.status:
                user.status = False
            else:
                user.status = True
            db.session.commit()

            n_status = ""
            if not user.status:
                n_status = "NOT "
            TELEGRAM.send_message("Status changed, you will %sreceive notifications" % n_status, user_id)

        elif text == "/delete":
            user = TelegramUsers.query.filter_by(user_id=user_id).first()
            db.session.delete(user)
            db.session.commit()
            TELEGRAM.send_message("Removal successful, you will no longer receive notifications. Use '/start' to re-engage", user_id)

        elif text == "/dev":
            user = TelegramUsers.query.filter_by(user_id=user_id).first()
            if user.dev:
                user.dev = False
            else:
                user.dev = True
            db.session.commit()

            n_status = ""
            if not user.dev:
                n_status = "NOT "
            TELEGRAM.send_message("Status changed, you will %sreceive developer notifications" % n_status, user_id)
    except AttributeError:
        return neg()

    return pos()

@amo_exception
@app.route('/test_sms', methods=['GET', 'POST'])
def test_sms():
    nr = "078424479"
    SMS.send_sms(nr, "Acesta este un test.")

    return pos()
