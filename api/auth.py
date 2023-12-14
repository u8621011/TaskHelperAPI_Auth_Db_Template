import requests
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from base64 import urlsafe_b64decode, b64decode
from jwt.algorithms import RSAAlgorithm
from flask import request


def pad_base64(b64string):
    """對 Base64 字符串進行填充以使其成為有效的 Base64 編碼"""
    padding = 4 - len(b64string) % 4
    return b64string + ('=' * padding if padding != 4 else '')


def get_jwt_public_key():
    # 從 URL 獲取公鑰資訊
    url = "https://auth.pluginlab.ai/admin/v1/cert"
    response = requests.get(url)
    jwks = response.json()

    # 選擇合適的公鑰
    for key in jwks['keys']:
        # 我們這裏直接用第一個 key, pluginLab 應該只會有一個 key
        public_key = RSAAlgorithm.from_jwk(jwks['keys'][0])

        return public_key


pluginlab_public_key = get_jwt_public_key()


def get_user_info_from_token():
    # 下面是 pluginLab 的驗證流程
    event_id = request.headers.get('X-PluginLab-Event-Id')

    # 這裏會拿到 pluginLab 給我們的一個 jwt bearer token, 我們將它解開來取得使用者資訊
    token = request.headers.get('Authorization')
    print(f'token: {token}')

    # 將 token 的前面的 Bearer 字串去掉
    token = token.split(' ')[1]

    # 用公鑰解碼 JWT
    payload = jwt.decode(token, pluginlab_public_key, algorithms=['PS256'], options={"verify_aud": False})
    print(payload)

    # 從 payload 讀取使用者的資訊
    user_id = payload['uid']
    plan_id = payload['user']['planId']
    name = payload['user']['name']
    email = payload['user']['email']
    print(f'user_id: {user_id}, plan_id: {plan_id}, name: {name}, email: {email}')

    return user_id, plan_id, name, email