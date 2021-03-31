from os import getenv
from api import TELEGRAM
from amocrm_api import AmoException
from .models import TelegramUsers

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
    return _handle
