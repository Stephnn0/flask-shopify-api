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
INSTALL_REDIRECT_URL = "https://9f1c-104-151-91-181.ngrok-free.app/api/auth"
APP_NAME = "flask-app"
WEBHOOK_APP_UNINSTALL_URL = ""
NONCE = None
ACCESS_MODE = []  
SCOPES = ['read_products']
ACCESS_TOKEN = ''

# CREATE TABLE sessions (
#     id SERIAL PRIMARY KEY,
#     unique_id UUID NOT NULL,
#     shop VARCHAR(255) NOT NULL,
#     state VARCHAR(255) NOT NULL,
#     access_token VARCHAR(255) NOT NULL
# );

# import psycopg2
# import uuid

# DATABASE_URL = "postgresql://username:password@localhost/dbname"  # Replace with your actual database URL

# def get_db_connection():
#     conn = psycopg2.connect(DATABASE_URL)
#     return conn

# def store_shopify_session(shop: str, state: str, access_token: str):
#     unique_id = uuid.uuid4()
    
#     conn = get_db_connection()
#     cur = conn.cursor()
#     try:
#         cur.execute("""
#             INSERT INTO sessions (unique_id, shop, state, access_token)
#             VALUES (%s, %s, %s, %s)
#             """,
#             (unique_id, shop, state, access_token))
#         conn.commit()
#     except Exception as e:
#         conn.rollback()
#         raise e
#     finally:
#         cur.close()
#         conn.close()


#  GET SHOPIFY STORAGE 

# def fetch_shopify_session(shop: str) -> dict:
#     conn = get_db_connection()
#     cur = conn.cursor()
#     try:
#         cur.execute("SELECT shop, access_token FROM sessions WHERE shop = %s", (shop,))
#         session = cur.fetchone()
#         if session:
#             return {
#                 "shop": session[0],
#                 "access_token": session[1]
#             }
#         return None
#     except Exception as e:
#         raise e
#     finally:
#         cur.close()
#         conn.close()

def generate_install_redirect_url(shop: str, scopes: List, nonce: str, access_mode: List):
    scopes_string = ','.join(scopes)
    shop = 'oroa-development.myshopify.com'
    access_mode_string = ','.join(access_mode)
    redirect_url = f"https://{shop}/admin/oauth/authorize?client_id={SHOPIFY_API_KEY}&scope={scopes_string}&redirect_uri={INSTALL_REDIRECT_URL}&state={nonce}&grant_options[]={access_mode_string}"
    return redirect_url


# LINK TO START OAUTH
@app.route('/app_launched', methods=['GET'])
def app_launched():
        shop = request.args.get('shop')
        NONCE = uuid.uuid4().hex
        redirect_url = generate_install_redirect_url(shop=shop, scopes=SCOPES, nonce=NONCE, access_mode=ACCESS_MODE)
        response = redirect(redirect_url, code=302)
        response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
        return response


# SHOULD MATCH SHOPIFY REDIRECT PARTNERS LINK
@app.route('/api/auth', methods=['GET'])
@helpers.verify_web_call
def app_installed():
    state = request.args.get('state')
    # global NONCE, ACCESS_TOKEN

    # if state != NONCE:
    #     return "Invalid `state` received", 400
    # NONCE = None

    # SAVE AND CREATE SESSION TABLE IN POSTRGRESS FOR LATER USE AND ACCESS OK TOKEN
    # save shop, state, accesstoken,

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


@app.route('/api/get_shop', methods=['GET'])
def get_shop_info():
    # Here, you should retrieve the shop and access token from a secure source.
    # For this example, let's assume you have them globally available.
    shop = 'oroa-development.myshopify.com'  # Replace with your actual shop domain
    access_token = 'shpua_ef591e962fce21d114147cc8ac6480f6'  # Replace with the actual access token

    shopify_client = ShopifyStoreClient(shop=shop, access_token=access_token)
    shop_info = shopify_client.get_shop()

    if shop_info is None:
        return jsonify({"error": "Failed to retrieve shop information"}), 500

    return jsonify(shop_info)


@app.route('/api/products_count', methods=['GET'])
def get_products_count():

    # session = fetch_shopify_session(shop)

    # if not session:
    #     return jsonify({"error": "Failed to retrieve session information"}), 500

    # shopify_client = ShopifyStoreClient(shop=session['shop'], access_token=session['access_token'])

    shop = 'oroa-development.myshopify.com' 
    access_token = 'shpua_ef591e962fce21d114147cc8ac6480f6' 

    shopify_client = ShopifyStoreClient(shop=shop, access_token=access_token)
    shop_info = shopify_client.get_products_count()

    if shop_info is None:
        return jsonify({"error": "Failed to retrieve shop information"}), 500

    return jsonify(shop_info)


@app.route('/api/all_products', methods=['GET'])
def get_all_products():

    shop = 'oroa-development.myshopify.com' 
    access_token = 'shpua_ef591e962fce21d114147cc8ac6480f6' 

    shopify_client = ShopifyStoreClient(shop=shop, access_token=access_token)
    shop_info = shopify_client.get_all_products()

    if shop_info is None:
        return jsonify({"error": "Failed to retrieve shop information"}), 500

    return jsonify(shop_info)



@app.route('/')
def frontend():
    return render_template('index.html')

@app.route('/success')
def api():
    return render_template('success.html')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)