import os
import json
from astrapy.db import AstraDB, AstraDBCollection
from astrapy.ops import AstraDBOps


# get Astra connection information from environment variables
ASTRA_DB_APPLICATION_TOKEN = os.environ.get('ASTRA_DB_APPLICATION_TOKEN')
ASTRA_DB_API_ENDPOINT = os.environ.get('ASTRA_DB_API_ENDPOINT')
ASTRA_DB_COLLECTION_NAME = os.environ.get('ASTRA_DB_COLLECTION_NAME')

# 這個目前沒有用到，先使用 default keyspace
#ASTRA_DB_KEYSPACE = os.environ.get('ASTRA_DB_KEYSPACE')


# Initialization
db = AstraDB(
  token=ASTRA_DB_APPLICATION_TOKEN,
#   namespace=ASTRA_DB_KEYSPACE,
  api_endpoint=ASTRA_DB_API_ENDPOINT)

print(f"Connected to Astra DB: {db.get_collections()}")


#Create collection
col = db.create_collection(ASTRA_DB_COLLECTION_NAME, dimension=5, metric="cosine")


def add_todo_item(user_id, task_name):
    col.insert_one(
        {
            "user_id": user_id,
            "task_name": task_name,
            "$vector": [0.25, 0.25, 0.25, 0.25, 0.25],
        }
    )

def get_user_todo_items(user_id):
    response  = col.find(filter={"user_id": user_id})

    # 以漂亮的格式打印 JSON
    print(json.dumps(response, indent=4, ensure_ascii=False))

    # response 格式怎麼拆解的範例，從 astradb 裏面 vector_find 的實做方式複製出來的，其實可以效仿這個實做方式
    #cast(List[API_DOC], raw_find_result["data"]["documents"])
    data = response['data']

    # 印出所有找到的文件
    if 'documents' in data:
        documents = data['documents']

        print(f'Found {len(documents)} documents')
        for document in documents:
            print(type(document), document)

        return documents
    
    return []


def cancel_user_todo_item(user_id, todo_idx):
    print(f'cancel_user_todo_item: {user_id}, {todo_idx}')
    response  = col.find(filter={"user_id": user_id})

    # 以漂亮的格式打印 JSON
    print(json.dumps(response, indent=4, ensure_ascii=False))

    documents = response["data"]["documents"]
    if documents and (0 <= todo_idx < len(documents) > 0):
        document = documents[todo_idx]
        document_id = document["_id"]
        response_delete = col.delete(id=document_id)
    
        # data format：  {'status': {'deletedCount': 1}}
        print(f'response_deleted: {response_delete}')

        return response_delete['status']['deletedCount'] > 0

    return False
