import hmac, hashlib, base64
from os import getenv

def pos(): return {"status": "Nice"}, 200

def verify_webhook(data, hmac_header):
    digest = hmac.new(getenv('SPF_SECRET').encode('utf-8'), data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))
