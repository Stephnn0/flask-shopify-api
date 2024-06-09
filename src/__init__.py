from flask import Flask, helpers, request, jsonify, render_template, redirect
from shopify import ShopifyStoreClient
from typing import List
from flask_cors import CORS
import uuid
import hashlib
import hmac
import base64
import requests

import helpers
import json

import logging


app = Flask(__name__)
CORS(app)

SHOPIFY_SECRET = "d7ffb1c2e529e5598b4598016d101c18"
SHOPIFY_API_KEY = "14064e1bcd7c937195a529cf86851041"
INSTALL_REDIRECT_URL = "https://164b-104-151-91-181.ngrok-free.app/api/auth"
APP_NAME = "flask-app"
WEBHOOK_APP_UNINSTALL_URL = ""
NONCE = None
ACCESS_MODE = []  
SCOPES = ['read_products']
ACCESS_TOKEN = ''

def generate_install_redirect_url(shop: str, scopes: List, nonce: str, access_mode: List):
    scopes_string = ','.join(scopes)
    shop = 'oroa-development.myshopify.com'
    access_mode_string = ','.join(access_mode)
    redirect_url = f"https://{shop}/admin/oauth/authorize?client_id={SHOPIFY_API_KEY}&scope={scopes_string}&redirect_uri={INSTALL_REDIRECT_URL}&state={nonce}&grant_options[]={access_mode_string}"
    return redirect_url



@app.route('/app_launched', methods=['GET'])
def app_launched():
        shop = request.args.get('shop')
        NONCE = uuid.uuid4().hex
        redirect_url = generate_install_redirect_url(shop=shop, scopes=SCOPES, nonce=NONCE, access_mode=ACCESS_MODE)
        response = redirect(redirect_url, code=302)
        response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
        return response
# RESPONSE NOT FOUND code , hmac , shop
# https://2d1a-2601-589-c200-8b90-1db5-6a99-6ddf-52e1.ngrok-free.app/api/auth?code=330a8b08bfd77a5fa83aedffd62f2242&hmac=7731e9c30a94c9ae984cacaf03f2ecd8c67572d7a8f7a4cc0379466070a7b31f&host=YWRtaW4uc2hvcGlmeS5jb20vc3RvcmUvb3JvYS1kZXZlbG9wbWVudA&shop=oroa-development.myshopify.com&state=c7aa708476944bf09f96adebc68ca8f7&timestamp=1717925028

# ==========================================================

@app.route('/api/auth', methods=['GET'])
@helpers.verify_web_call
def app_installed():
    state = request.args.get('state')
    # global NONCE, ACCESS_TOKEN

    # if state != NONCE:
    #     return "Invalid `state` received", 400
    # NONCE = None

    shop = request.args.get('shop')
    code = request.args.get('code')
    ACCESS_TOKEN = ShopifyStoreClient.authenticate(shop=shop, code=code)

    print(ACCESS_TOKEN, 'ACCESS_TOKEN')

    shopify_client = ShopifyStoreClient(shop=shop, access_token=ACCESS_TOKEN)
    # shopify_client.create_webook(address=WEBHOOK_APP_UNINSTALL_URL, topic="app/uninstalled")

    # redirect_url = helpers.generate_post_install_redirect_url(shop=shop)
    redirect_url = helpers.generate_post_install_redirect_url_new()

    return redirect(redirect_url, code=302)

# @app.route('/app_uninstalled', methods=['POST'])
# @helpers.verify_webhook_call
# def app_uninstalled():
#     # https://shopify.dev/docs/admin-api/rest/reference/events/webhook?api[version]=2020-04
#     # Someone uninstalled your app, clean up anything you need to
#     # NOTE the shop ACCESS_TOKEN is now void!
#     global ACCESS_TOKEN
#     ACCESS_TOKEN = None

#     webhook_topic = request.headers.get('X-Shopify-Topic')
#     webhook_payload = request.get_json()
#     logging.error(f"webhook call received {webhook_topic}:\n{json.dumps(webhook_payload, indent=4)}")

#     return "OK"



@app.route('/')
def frontend():
    return render_template('index.html')

@app.route('/success')
def api():
    return render_template('success.html')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)