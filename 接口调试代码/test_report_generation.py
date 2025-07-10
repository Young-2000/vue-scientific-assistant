import requests
import json
import copy
import uuid
import argparse

BASE_URL = "http://127.0.0.1/v1"
LOGIN_URL = f"{BASE_URL}/user/login"
SET_URL = f"{BASE_URL}/canvas/set"
RESET_URL = f"{BASE_URL}/canvas/reset"
COMPLETION_URL = f"{BASE_URL}/canvas/completion"

# 直接使用账号密码
EMAIL = "123@123.com"
PASSWORD = "hXWqKtPnAt+tvQeaKHh87nNc5xbuVJu5thZtH1gBOzFfwmjml8DJp3/E2HzILWJVqWy3Vp79g3wPC67+ImkG1IQyvD4BSYXp4zlUy++toYQO1GOEMys4Xn8Xta2G9KTkjhWrR9qfOyEroIIzXEy2+HBf4DenGXPABLIh0HAGlZSdizpq3mHbIhHm26CDl0OIT7S7xd6YCOYpM9VC6IMYQI/a3r5qZc8cIvkQGrEnrhlPVIPQocxY5shmXwaEJxugPd/kezvsienh6TEfctqVcSwIssIgPBunOVJb2PDCF/NevwS3ZGqmFn7VIxUwHi0oz4KYZsudj+K8aJqG/8Jj8w=="

session = requests.Session()

def login(email, password):
    login_data = {"email": email, "password": password}
    resp = session.post(LOGIN_URL, json=login_data)
    print("登录状态码:", resp.status_code)
    print("登录响应:", resp.text)
    if resp.status_code != 200:
        print("登录失败")
        return False
    token = resp.headers.get("Authorization") or resp.json().get("data", {}).get("access_token")
    if not token:
        print("未获取到token")
        return False
    session.headers.update({
        "Authorization": token,
        "Content-Type": "application/json"
    })
    return True

if __name__ == "__main__":
    # 1. 登录
    if not login(EMAIL, PASSWORD):
        exit(1)

    # 1.5 获取模板列表
    templates_url = f"{BASE_URL}/canvas/templates"
    templates_resp = session.get(templates_url)
    try:
        templates_json = templates_resp.json()
        print("TEMPLATES接口响应：", templates_resp.status_code)
        with open("接口调试代码/templates_response.json", "w", encoding="utf-8") as f:
            json.dump(templates_json, f, ensure_ascii=False, indent=2)
    except Exception:
        print("TEMPLATES接口响应：", templates_resp.status_code, templates_resp.text)

    # 2. set 请求
    title = f"test_{uuid.uuid4().hex[:8]}"
    set_payload = {
        "title": title,
        "dsl": {
            "graph": {
                "nodes": [
                    {
                        "id": "begin",
                        "type": "beginNode",
                        "position": {"x": 50, "y": 200},
                        "data": {"label": "Begin", "name": "begin"},
                        "sourcePosition": "left",
                        "targetPosition": "right"
                    }
                ],
                "edges": []
            },
            "components": {
                "begin": {
                    "obj": {"component_name": "Begin", "params": {}},
                    "downstream": ["Answer:China"],
                    "upstream": []
                }
            },
            "messages": [],
            "reference": [],
            "history": [],
            "path": [],
            "answer": []
        }
    }
    set_resp = session.post(SET_URL, json=set_payload)
    set_id = None
    set_title = None
    try:
        set_json = set_resp.json()
        print("SET接口响应：", set_resp.status_code, json.dumps(set_json, ensure_ascii=False, indent=2))
        with open("接口调试代码/set_response.json", "w", encoding="utf-8") as f:
            json.dump(set_json, f, ensure_ascii=False, indent=2)
        # 获取第一次set返回的id和title
        set_id = set_json.get("data", {}).get("id")
        set_title = set_json.get("data", {}).get("title")
    except Exception:
        print("SET接口响应：", set_resp.status_code, set_resp.text)

    # 3. set 请求，负载为 报告生成 (2).json，id和title取自上一次set返回
    with open(r"接口调试代码\dsl.json", "r", encoding="utf-8") as f:
        report_payload = json.load(f)
    if set_id:
        report_payload["id"] = set_id
    if set_title:
        report_payload["title"] = set_title
    set_resp2 = session.post(SET_URL, json=report_payload)
    try:
        set_json2 = set_resp2.json()
        print("SET接口2响应：", set_resp2.status_code, json.dumps(set_json2, ensure_ascii=False, indent=2))
        with open("接口调试代码/set_response2.json", "w", encoding="utf-8") as f:
            json.dump(set_json2, f, ensure_ascii=False, indent=2)
    except Exception:
        print("SET接口2响应：", set_resp2.status_code, set_resp2.text)

    # 3. 生成唯一 id
    unique_id = set_id

    # 4. 读取 dsl.json
    with open("接口调试代码/dsl.json", "r", encoding="utf-8") as f:
        dsl_data = json.load(f)
    
    if set_id:
        dsl_data["id"] = set_id
    if set_title:
        dsl_data["title"] = set_title

    # 5. 替换 dsl 中 query 的 value
    query_list = dsl_data.get('dsl', {}).get('components', {}).get('begin', {}).get('obj', {}).get('params', {}).get('query', [])
    # 输出原始 query_list 内容
    print("原始 query_list:", json.dumps(query_list, ensure_ascii=False, indent=2))
    for q in query_list:
        if q.get('key') == 'instruction':
            q['value'] = '用中文进行回答'
        elif q.get('key') == 'topic':
            q['value'] = '大模型实验报告'
        elif q.get('key') == 'template':
            q['value'] = '期末报告模板_第3次作业.docx\n数据挖掘期末项目报告模板问题背景数据挖掘实验2.1 数据来源2.2 算法介绍2.3 实验过程2.4 结果分析总结\n----\n'

    # 同步修改 graph.nodes 里的 query 字段
    for node in dsl_data.get('dsl', {}).get('graph', {}).get('nodes', []):
        form = node.get('data', {}).get('form', {})
        query_list = form.get('query', [])
        for q in query_list:
            if q.get('key') == 'instruction':
                q['value'] = '用中文进行回答'
            elif q.get('key') == 'topic':
                q['value'] = '大模型实验报告'
            elif q.get('key') == 'template':
                q['value'] = '期末报告模板_第3次作业.docx\n数据挖掘期末项目报告模板问题背景数据挖掘实验2.1 数据来源2.2 算法介绍2.3 实验过程2.4 结果分析总结\n----\n'

    # 保存修改后的 dsl
    with open("接口调试代码/modified_dsl.json", "w", encoding="utf-8") as f:
        json.dump(dsl_data, f, ensure_ascii=False, indent=2)

    # 6. set 请求
    set_resp = session.post(SET_URL, json=dsl_data)
    try:
        resp_json = json.loads(set_resp.text)
        print("SET接口响应：", set_resp.status_code, json.dumps(resp_json, ensure_ascii=False, indent=2))
        # 保存到 set_response.json
        with open("接口调试代码/set_response.json", "w", encoding="utf-8") as f:
            json.dump(resp_json, f, ensure_ascii=False, indent=2)
    except Exception:
        print("SET接口响应：", set_resp.status_code, set_resp.text)

    # 7. reset 请求
    reset_payload = {"id": unique_id}
    reset_resp = session.post(RESET_URL, json=reset_payload)
    try:
        resp_json = json.loads(reset_resp.text)
        # 保存到 reset_response.json
        with open("接口调试代码/reset_response.json", "w", encoding="utf-8") as f:
            json.dump(resp_json, f, ensure_ascii=False, indent=2)
        print("RESET接口响应：", reset_resp.status_code, json.dumps(resp_json, ensure_ascii=False, indent=2))
    except Exception:
        print("RESET接口失败响应：", reset_resp.status_code, reset_resp.text)

    # 8. completion 请求，直接用同一个 id
    completion_payload = {"id": unique_id}
    completion_resp = session.post(COMPLETION_URL, json=completion_payload)
    try:
        resp_json = json.loads(completion_resp.text)
        print("COMPLETION接口响应：", completion_resp.status_code, json.dumps(resp_json, ensure_ascii=False, indent=2))
    except Exception:
        print("COMPLETION接口失败响应：", completion_resp.status_code, completion_resp.text) 
