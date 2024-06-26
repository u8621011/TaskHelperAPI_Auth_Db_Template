import requests
import jwt
import os
from flask import request, abort


# 認證 ChatGPT Action 用的 token
KOBBLE_SDK_SECRET = os.environ.get('KOBBLE_SDK_SECRET')


def download_jwt_public_key():
    # 從 URL 獲取公鑰資訊
    url = "https://sdk.kobble.io/gateway/getPublicKey"
    response = requests.get(url, headers={"Kobble-Sdk-Secret": KOBBLE_SDK_SECRET})

    # response will like this:
    #{
    #    "pem": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0C...1V2G+mCP8bmy/3fg==\n-----END PUBLIC KEY-----\n",
    #    "algorithm": "ES256",
    #    "projectId": "cludjcj1w00bhm6v9hw3wimwv"
    #}

    data = response.json()

    # 直接返回PEM格式的公鑰
    return data['pem']


_kobble_public_key = None

def get_kobble_public_key():
    global _kobble_public_key
    if _kobble_public_key is None:
        _kobble_public_key = download_jwt_public_key()
    return _kobble_public_key


def get_user_info_from_token(optinal=False):
    # 這裏會拿到 pluginLab 給我們的一個 jwt bearer token, 我們將它解開來取得使用者資訊
    token = request.headers.get('Authorization')
    print(f'token: {token}')
    if not token:
        if optinal:
            return None, None, None
        else:
            # 認證失敗，沒有 Authorization token
            abort(401, description="Authorization token is missing")

    # 將 token 的前面的 Bearer 字串去掉
    token = token.split(' ')[1]

    try:
        # 用公鑰解碼 JWT
        kobble_public_key = get_kobble_public_key()
        
        payload = jwt.decode(token, kobble_public_key, algorithms=['ES256'], options={"verify_aud": False})
    except jwt.PyJWTError as e:
        abort(401, description="Invalid token")

    # 目前的格式
    # {
    #     'aud': 'cludjcj1w00bhm6v9hw3wimwv',
    #     'exp': 1711782968,
    #     'iat': 1711779368,
    #     'iss': 'gateway.kobble.io',
    #     'sub': 'clud..izra8pz',
    #     'user': {
    #         'email': 'someone@gmail.com',
    #         'id': 'clud..izra8pz',
    #         'name': None,
    #         'products': [
    #         {
    #             'id': 'cludjcj2v00bjm6v9f3lrapre',
    #             'quotas': [
    #             ]
    #         }
    #         ]
    #     }
    # }
    print(payload)

    # 從 payload取得使用者基本訊息
    user_id = payload['user']['id']
    user_name = payload['user']['name']
    user_email = payload['user']['email']

    return user_id, user_name, user_email
