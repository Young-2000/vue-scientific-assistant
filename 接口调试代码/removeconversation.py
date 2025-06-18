import requests
from sseclient import SSEClient
import json
import uuid
from datetime import datetime

url = "http://127.0.0.1/v1/dialog/list"
login_url = "http://127.0.0.1/v1/user/login"
rm_url = "http://127.0.0.1/v1/dialog/rm"

session = requests.Session()


def login(email, password):
    login_data = {"email": email, "password": password}
    response = session.post(login_url, json=login_data)
    print(f"登录状态码: {response.status_code}")
    print(f"登录响应: {response.text}")

    if response.status_code != 200:
        print("登录失败")
        return None

    auth_token = response.headers.get("Authorization") or response.json().get(
        "data", {}
    ).get("access_token")
    if not auth_token:
        print("未找到授权Token")
        return None

    session.headers.update(
        {
            "Authorization": auth_token,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json",
        }
    )
    print(f"Authorization: {auth_token}")
    return auth_token


def get_user_id():
    resp = session.get("http://127.0.0.1/v1/user/info")
    return resp.json().get("data", {}).get("id")


def get_list():
    ids = []
    response = session.get(url)
    res_json = response.json()
    for data in res_json["data"]:
        ids.append(data["id"])
    return ids


def rm_conversation(id, user_id):
    payload = {
        "dialog_ids": [id],
        "user_id": user_id,
    }
    response = session.post(rm_url, json=payload)
    print(f"删除对话ID: {id}")
    print(f"删除响应: {response.text}")


if __name__ == "__main__":
    email = "123@123.com"
    password = "hXWqKtPnAt+tvQeaKHh87nNc5xbuVJu5thZtH1gBOzFfwmjml8DJp3/E2HzILWJVqWy3Vp79g3wPC67+ImkG1IQyvD4BSYXp4zlUy++toYQO1GOEMys4Xn8Xta2G9KTkjhWrR9qfOyEroIIzXEy2+HBf4DenGXPABLIh0HAGlZSdizpq3mHbIhHm26CDl0OIT7S7xd6YCOYpM9VC6IMYQI/a3r5qZc8cIvkQGrEnrhlPVIPQocxY5shmXwaEJxugPd/kezvsienh6TEfctqVcSwIssIgPBunOVJb2PDCF/NevwS3ZGqmFn7VIxUwHi0oz4KYZsudj+K8aJqG/8Jj8w=="

    if login(email, password):
        ids = get_list()
        user_id = get_user_id()
        for id in ids:
            rm_conversation(id, user_id)
