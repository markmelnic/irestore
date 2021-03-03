from os import getenv
from amocrm_api import AmoOAuthClient

from .models import Tokens

def client():
    client = AmoOAuthClient(
        Tokens.access_token,
        Tokens.refresh_token,
        getenv('SUBDOMAIN'),
        getenv('CLIENT_ID'),
        getenv('CLIENT_SECRET'),
        getenv('REDIRECT')
    )

    try:
        client.update_tokens()
    except:
        pass

    return client
