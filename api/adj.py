import hmac, hashlib, base64
from os import getenv
from api import TELEGRAM
from amocrm_api import AmoException
from .models import TelegramUsers

def pos(): return {"status": "Nice"}, 200

def verify_webhook(data, hmac_header):
    digest = hmac.new(getenv('SPF_SECRET').encode('utf-8'), data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

def amo_exception(func):
    def _handle(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except AmoException:
            for user in TelegramUsers.query.filter_by(dev=True).all():
                TELEGRAM.send_message(
                    "AMO Tokens Unavailable\n",
                    'https://www.amocrm.ru/oauth?client_id='+getenv('CLIENT_ID')+'&state='+getenv('REDIRECT')+'&mode=post_message'
                    )
        except:
            print("CAUGHT")
    return _handle
