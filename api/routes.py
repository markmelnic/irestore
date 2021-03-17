import requests, json, hmac, hashlib, base64, random
import urllib.parse as urlparse
from os import getenv
from flask import request, redirect, url_for

from api import *
from .models import Tokens

def verify_webhook(data, hmac_header):
    digest = hmac.new(getenv('SPF_SECRET'), data.encode('utf-8'), hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

def pos(): return {"status": "Nice"}, 200

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

        return pos()
    else:
        return redirect(url_for('neg'))

@app.route('/api/redirect', methods=['GET'])
def api_redirect():
    return redirect('https://www.amocrm.ru/oauth?client_id='+getenv('CLIENT_ID')+'&state='+getenv('REDIRECT')+'&mode=post_message')

@app.route('/api/service', methods=['POST', 'GET'])
def api_service():
    encodedStr = b'http://foo.appspot.com/?leads%5Bstatus%5D%5B0%5D%5Bid%5D=30267969&leads%5Bstatus%5D%5B0%5D%5Bname%5D=apple+tv+3&leads%5Bstatus%5D%5B0%5D%5Bstatus_id%5D=16525558&leads%5Bstatus%5D%5B0%5D%5Bold_status_id%5D=16525555&leads%5Bstatus%5D%5B0%5D%5Bprice%5D=1&leads%5Bstatus%5D%5B0%5D%5Bresponsible_user_id%5D=1764433&leads%5Bstatus%5D%5B0%5D%5Blast_modified%5D=1615985846&leads%5Bstatus%5D%5B0%5D%5Bmodified_user_id%5D=1760815&leads%5Bstatus%5D%5B0%5D%5Bcreated_user_id%5D=1764433&leads%5Bstatus%5D%5B0%5D%5Bdate_create%5D=1615894221&leads%5Bstatus%5D%5B0%5D%5Bpipeline_id%5D=788512&leads%5Bstatus%5D%5B0%5D%5Btags%5D%5B0%5D%5Bid%5D=482205&leads%5Bstatus%5D%5B0%5D%5Btags%5D%5B0%5D%5Bname%5D=Sasa&leads%5Bstatus%5D%5B0%5D%5Baccount_id%5D=16503244&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B0%5D%5Bid%5D=491053&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B0%5D%5Bname%5D=IMEI%2FSERIE&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B0%5D%5Bvalues%5D%5B0%5D%5Bvalue%5D=1&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B1%5D%5Bid%5D=481305&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B1%5D%5Bname%5D=Cind+trebuie%3F&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B1%5D%5Bvalues%5D%5B0%5D=1615845600&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B2%5D%5Bid%5D=496779&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B2%5D%5Bname%5D=Stare+Device&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B2%5D%5Bvalues%5D%5B0%5D%5Bvalue%5D=Zghirieturi+minore&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B2%5D%5Bvalues%5D%5B0%5D%5Benum%5D=959761&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B3%5D%5Bid%5D=481313&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B3%5D%5Bname%5D=Tip+Lead&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B3%5D%5Bvalues%5D%5B0%5D%5Bvalue%5D=Lead+nou&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B3%5D%5Bvalues%5D%5B0%5D%5Benum%5D=932119&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B4%5D%5Bid%5D=481307&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B4%5D%5Bname%5D=Unde+au+aflat%3F&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B4%5D%5Bvalues%5D%5B0%5D%5Bvalue%5D=Google&leads%5Bstatus%5D%5B0%5D%5Bcustom_fields%5D%5B4%5D%5Bvalues%5D%5B0%5D%5Benum%5D=932073&leads%5Bstatus%5D%5B0%5D%5Bcreated_at%5D=1615894221&leads%5Bstatus%5D%5B0%5D%5Bupdated_at%5D=1615985846&account%5Bsubdomain%5D=irestoremoldova&account%5Bid%5D=16503244&account%5B_links%5D%5Bself%5D=https%3A%2F%2Firestoremoldova.amocrm.ru'

    url = 'http://foo.appspot.com/abc?def=ghi'
    parsed = urlparse.urlparse(encodedStr.decode("utf-8"))
    #print(parse_qs(parsed.query))
    id = urlparse.parse_qs(parsed.query)['leads[status][0][id]'][0]
    print(AMO.get_leads_links(id))


    leads = request.args.get('leads')
    print(leads)
    if leads:
        for l in leads:
            print(l)
            if int(l['status_id']) == 16525558:
                print(l)
                return l
            else:
                return "X"
    else:
        return "A"

@app.route('/api/sync_products', methods=['POST', 'GET'])
def sync_products():
    temp = [[str(v['sku']) +'|'+ str(v['product_id']) for v in p['variants']] for p in SPF.get_products()['products']]
    products = []
    c = 0
    for __ in temp:
        for _ in __:
            c += 1
            products.append({"value": _, "sort": c})

    return AMO.get_lead(30269101)

    custom = [
        {
            "name": "TEST BLEA",
            "type": "multiselect",
            "enums": products,
            "is_deletable": False,
            "is_visible": True,
            "is_required": True,
            "required_statuses": [{
                "pipeline_id": PIPELINE
            }]
        }
    ]
    #print(custom)
    #AMO.create_leads_custom_fields(custom)

    return pos()

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

@app.route('/api/order/create', methods=['POST', 'GET'])
def order_create():
    if request.method == "POST":
        data = json.loads(request.get_data())
        verify = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))
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

    objects = [{
        'name': name,
        'price': price,
        'pipeline_id': PIPELINE,
    }]

    AMO.create_leads(objects)

    return pos()

@app.route('/api/order/update', methods=['POST', 'GET'])
def order_update():
    if request.method == "POST":
        data = json.loads(request.get_data())
        verify = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))
        if not verify:
            return redirect(url_for('neg'))

@app.route('/api/order/delete', methods=['POST', 'GET'])
def order_delete():
    if request.method == "POST":
        data = json.loads(request.get_data())
        verify = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))
        if not verify:
            return redirect(url_for('neg'))

    for user in TelegramUsers.query.filter_by(status=True).all():
        TELEGRAM.send_message("Order %s has been DELETED" % (data['id']), user.user_id)
    return pos()

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

@app.route('/api/telegram/webhook', methods=['POST'])
def respond():
    data = json.loads(request.get_data())
    user_id = int(data['message']['from']['id'])
    text = data['message']['text']
    if text == "/start":
        dish = TelegramUsers(
            user_id = user_id
            )
        db.session.add(dish)
        db.session.commit()
        TELEGRAM.send_message("Initialisation successful, you will receive notifications", user_id)

    elif text == "/help":
        help_message = """
        /help - List of commands
        /start - Initialise app and user
        /info - Receive current user information
        /delete - Remove user
        /toggle - Receive or not notifications
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
        TELEGRAM.send_message("Status changed, you are %sreceiving notifications" % n_status, user_id)

    elif text == "/delete":
        user = TelegramUsers.query.filter_by(user_id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        TELEGRAM.send_message("Removal successful, you will no longer receive notifications. Use '/start' to reingage", user_id)

    return pos()
