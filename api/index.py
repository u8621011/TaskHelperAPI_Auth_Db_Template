from flask import Flask, Response, request, jsonify
import os
from flask_cors import CORS
from .auth_pluginlab import get_user_info_from_token
from .db import add_todo_item, get_user_todo_items, cancel_user_todo_item


app = Flask(__name__)


CORS(app, resources={r"/*": {"origins": ["http://chat.openai.com", "https://chat.openai.com"]}})  # 允許 chatgpt 的 CORS 請求


@app.route("/todos/<string:username>", methods=['POST'])
def add_todo(username):
    # 我們其實拿不到 username, 使用 OAuth 得到的 user_id 來當作 key
    (user_id, plan_id, name, email) = get_user_info_from_token()

    data = request.get_json(force=True)

    todo = data["todo"]

    add_todo_item(user_id, todo)

    return 'OK', 200

@app.route("/todos/<string:username>", methods=['GET'])
def get_todos(username):
    # 我們其實拿不到 username, 使用 OAuth 得到的 user_id 來當作 key
    (user_id, plan_id, name, email) = get_user_info_from_token()

    docs = get_user_todo_items(user_id)

    print(f'docs returned: {jsonify(docs)}')
    if docs and len(docs) > 0:
        todos = [d['task_name'] for d in docs]
        return jsonify(todos)
    else:
        return jsonify([])
    

# ChatGPT 目前並不支援 DELETE。使用 HTTP DELETE 會失敗，改用 POST 來 workaround
#@app.route("/todos/<string:username>", methods=['DELETE'])
#def delete_todo(username):
@app.route("/todos/cancel/<string:username>", methods=['POST'])
def cancel_todo(username):
    # 我們其實拿不到 username, 使用 OAuth 得到的 user_id 來當作 key
    (user_id, plan_id, name, email) = get_user_info_from_token()

    data = request.get_json(force=True)
    todo_idx = data["todo_idx"]

    document_deleted = cancel_user_todo_item(user_id, todo_idx)

    if document_deleted:
        return 'OK', 200
    else:
        return 'Cannot find the cancelling todo', 200


@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'