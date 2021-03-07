import os, json, requests

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.base = "https://api.telegram.org/bot{}/".format(self.token)

    def get_updates(self, offset=None):
        url = self.base + "getUpdates?timeout=100"
        if offset:
            url = url + "&offset={}".format(offset + 1)
        response = requests.get(url)
        return json.loads(response.content)

    def send_message(self, message, chat_id):
        url = self.base + "sendMessage?chat_id={}&text={}".format(chat_id, message)
        if message is not None:
            requests.get(url)
