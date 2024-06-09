from functools import wraps
from typing import List
import logging

import os
import re
import hmac
import base64
import hashlib
from flask import request, abort

from dotenv import load_dotenv

SHOPIFY_SECRET = "d7ffb1c2e529e5598b4598016d101c18"
APP_NAME = "flask-app"
INSTALL_REDIRECT_URL = "https://164b-104-151-91-181.ngrok-free.app/"


def generate_post_install_redirect_url_new():
    redirect_url = f"https://164b-104-151-91-181.ngrok-free.app/success"
    return redirect_url

def generate_post_install_redirect_url(shop: str):
    redirect_url = f"https://{shop}/admin/apps/{APP_NAME}"
    return redirect_url

def verify_web_call(f):
    @wraps(f)
    def wrapper(*args, **kwargs) -> bool:
        get_args = request.args
        hmac = get_args.get('hmac')
        sorted(get_args)
        data = '&'.join([f"{key}={value}" for key, value in get_args.items() if key != 'hmac']).encode('utf-8')
        if not verify_hmac(data, hmac):
            logging.error(f"HMAC could not be verified: \n\thmac {hmac}\n\tdata {data}")
            abort(400)

        shop = get_args.get('shop')
        if shop and not is_valid_shop(shop):
            logging.error(f"Shop name received is invalid: \n\tshop {shop}")
            abort(401)
        return f(*args, **kwargs)
    return wrapper

def verify_hmac(data: bytes, orig_hmac: str):
    new_hmac = hmac.new(
        SHOPIFY_SECRET.encode('utf-8'),
        data,
        hashlib.sha256
    )
    return new_hmac.hexdigest() == orig_hmac


def is_valid_shop(shop: str) -> bool:
    # Shopify docs give regex with protocol required, but shop never includes protocol
    shopname_regex = r'[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com[\/]?'
    return True if re.match(shopname_regex, shop) else False
