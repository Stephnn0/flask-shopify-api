import requests
from requests.exceptions import HTTPError
import json

import logging


SHOPIFY_SECRET = "d7ffb1c2e529e5598b4598016d101c18"
SHOPIFY_API_KEY = "14064e1bcd7c937195a529cf86851041"

SHOPIFY_API_VERSION = "2020-01"

REQUEST_METHODS = {
    "GET": requests.get,
    "POST": requests.post,
    "PUT": requests.put,
    "DEL": requests.delete
}
# https://oroa-development.myshopify.com/admin/oauth/access_token
# oroa-development.myshopify.com
class ShopifyStoreClient:

    def __init__(self, shop: str, access_token: str):
        self.shop = shop
        self.base_url = f"https://{shop}/admin/api/{SHOPIFY_API_VERSION}/"
        self.access_token = access_token


    @staticmethod
    def authenticate(shop: str, code: str) -> str:
        url = f"https://{shop}/admin/oauth/access_token"
        payload = {
            "client_id": SHOPIFY_API_KEY,
            "client_secret": SHOPIFY_SECRET,
            "code": code
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()['access_token']
        except HTTPError as ex:
            print(ex)

        return None
    
    
    def authenticated_shopify_call(self, call_path: str, method: str, params: dict = None, payload: dict = None, headers: dict = {}) -> dict:
        url = f"{self.base_url}{call_path}"
        request_func = REQUEST_METHODS[method]
        headers['X-Shopify-Access-Token'] = self.access_token
        try:
            response = request_func(url, params=params, json=payload, headers=headers)
            response.raise_for_status()
            logging.debug(f"authenticated_shopify_call response:\n{json.dumps(response.json(), indent=4)}")
            return response.json()
        except HTTPError as ex:
            logging.exception(ex)
            return None
        
    def create_webook(self, address: str, topic: str) -> dict:
        call_path = f'webhooks.json'
        method = 'POST'
        payload = {
            "webhook": {
                "topic": topic,
                "address": address,
                "format": "json"
            }
        }
        webhook_response = self.authenticated_shopify_call(call_path=call_path, method=method, payload=payload)
        if not webhook_response:
            return None
        return webhook_response['webhook']