import envars
from os import getenv
from amocrm_api import AmoOAuthClient

access_token = open("access_token.txt", "r").read()
refresh_token = open("refresh_token.txt", "r").read()

client = AmoOAuthClient(access_token, refresh_token, getenv('F_SUBDOMAIN'), getenv('CLIENT_ID'), getenv('CLIENT_SECRET'), getenv('REDIRECT'))
client.update_tokens()

l1 = client.get_leads(filters = {'name': "Order id ttt 3838"})
l1c = client.get_leads_links(entity_id = 30141591)
print(l1, l1c)
c1 = client.get_contacts(filters = {'id': "45212897"})
print(c1)
