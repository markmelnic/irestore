from os import getenv
from amocrm_api import AmoOAuthClient

def client():
    client = AmoOAuthClient(
        open("access_token.txt", "r").read(),
        open("refresh_token.txt", "r").read(),
        getenv('F_SUBDOMAIN'),
        getenv('CLIENT_ID'),
        getenv('CLIENT_SECRET'),
        getenv('REDIRECT')
        )

    try:
        client.update_tokens()
    except:
        pass

    return client
