import requests
import json

login_url = "http://127.0.0.1/v1/user/login"
canvas_list_url = "http://127.0.0.1/v1/canvas/list"
rm_url = "http://127.0.0.1/v1/canvas/rm"

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

def fetch_canvas_list():
    response = session.get(canvas_list_url)
    if response.status_code != 200:
        print("获取canvas列表失败")
        return []
    data = response.json()
    data = data["data"]
    test_ids = []
    for i in data:
        if isinstance(i.get("title"), str) and i["title"].startswith("test"):
            test_ids.append(i["id"])
    print("以'test'开头的title对应的id:", test_ids)
    for i in test_ids:
        rm_payload = {"canvas_ids": [i]}
        rm_resp = session.post(rm_url, json=rm_payload)
        if(rm_resp.status_code == 200):
            print(f"删除{i}成功")
        else:
            print(f"删除{i}失败")
    return data

if __name__ == "__main__":
    email = "123@123.com"
    password = "hXWqKtPnAt+tvQeaKHh87nNc5xbuVJu5thZtH1gBOzFfwmjml8DJp3/E2HzILWJVqWy3Vp79g3wPC67+ImkG1IQyvD4BSYXp4zlUy++toYQO1GOEMys4Xn8Xta2G9KTkjhWrR9qfOyEroIIzXEy2+HBf4DenGXPABLIh0HAGlZSdizpq3mHbIhHm26CDl0OIT7S7xd6YCOYpM9VC6IMYQI/a3r5qZc8cIvkQGrEnrhlPVIPQocxY5shmXwaEJxugPd/kezvsienh6TEfctqVcSwIssIgPBunOVJb2PDCF/NevwS3ZGqmFn7VIxUwHi0oz4KYZsudj+K8aJqG/8Jj8w=="
    if login(email, password):
        fetch_canvas_list() 