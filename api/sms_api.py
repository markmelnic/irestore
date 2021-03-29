import requests, json
from typing import Any
from urllib.parse import urlencode

# do not send sms from 10 to 19

class SMSClient:
    def __init__(self, user: str, password: str) -> None:
        self.base_url = f"https://api.bulksms.md:4432/UnifunBulkSMSAPI.asmx/SendSMSNoneDigitsEncoded?username={user}&password={password}"
        self.sender = "iRestore.md"
        self.dlrmask = 31
        self.dlrurl = "WIP"
        self.charset = "utf8"
        self.coding = "2"

    def _make_api_request(self, query: str) -> dict:
        res = requests.get(self.base_url + query)
        return res

    def send_sms(self, msisdn: str, body: str):
        query = '&' + urlencode({
            'charset': self.charset,
            'dlrmask': self.dlrmask,
            'dlrurl': self.dlrurl,
            'coding': self.coding,
            'from': self.sender,
            'to': '373' + msisdn[-8:],
            'text': body,
        })

        return self._make_api_request(query)
