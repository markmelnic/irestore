import requests, json
from flask import Flask

app = Flask(__name__)

@app.route('/order')
def order():

    url = "https://a59b86043473feded6627533f30ec1fe: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@irestoremd.myshopify.com/admin/api/2021-01/orders.json"

    headers = {
    'Cookie': '_secure_admin_session_id=88639c77e66d62c035e544f4e532161d; _secure_admin_session_id_csrf=88639c77e66d62c035e544f4e532161d; _y=42b3b466-00aa-40cf-990d-e1ba0fe69b9b; _shopify_y=42b3b466-00aa-40cf-990d-e1ba0fe69b9b; _shopify_fs=2021-02-10T16%3A42%3A07Z; _s=0415647a-7a8c-46e3-9f42-972740946a3f; _shopify_s=0415647a-7a8c-46e3-9f42-972740946a3f'
    }

    response = requests.get(url, headers=headers)
    data = json.loads(response.content.decode('utf8'))

    return data
