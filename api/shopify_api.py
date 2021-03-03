import requests, json
from urllib.parse import urlencode

class Shopify:
    def __init__(self, user: str, psw: str, store: str, headers: str) -> None:
        self.base_url = f"https://{user}:{psw}@{store}.myshopify.com/admin/api/2021-01/"
        self.headers = {"Cookie": headers}

    def _make_api_request(self, category: str, query: str = "") -> dict:
        _url = self.base_url + category + ".json" + query
        res = requests.get(_url, headers=self.headers)
        return json.loads(res.content.decode('utf8'))

    def get_products(self) -> dict:
        return self._make_api_request('products')

    def get_inventory_item(self, item_id: int) -> dict:
        return self._make_api_request('inventory_items/' + str(item_id))

    def get_inventory_levels(self) -> dict:
        return self._make_api_request('inventory_levels')

    def get_inventory_levels_product(self, item_id: str) -> dict:
        query = '?' + urlencode({'inventory_item_ids': item_id})
        return self._make_api_request('inventory_levels', query=query)
