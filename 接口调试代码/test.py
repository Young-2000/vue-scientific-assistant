import requests
from sseclient import SSEClient
import json
import uuid
from datetime import datetime

# 基本配置
BASE_URL = "http://127.0.0.1/v1"
login_url = f"{BASE_URL}/user/login"
ask_url = f"{BASE_URL}/conversation/ask"
kb_list_url = f"{BASE_URL}/kb/list"
completion_url = f"{BASE_URL}/conversation/completion"

retrieval_test_url = f"{BASE_URL}/chunk/retrieval_test"
related_questions_url = f"{BASE_URL}/conversation/related_questions"

# 日志文件生成
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"api_log_{timestamp}.txt"

session = requests.Session()

message_history = []


def print_to_both(message):
    print(message)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def login(email, password):
    login_data = {"email": email, "password": password}
    response = session.post(login_url, json=login_data)
    print_to_both(f"登录状态码: {response.status_code}")
    print_to_both(f"登录响应: {response.text}")

    if response.status_code != 200:
        print_to_both("登录失败")
        return None

    auth_token = response.headers.get("Authorization") or response.json().get(
        "data", {}
    ).get("access_token")
    if not auth_token:
        print_to_both("未找到授权Token")
        return None

    session.headers.update(
        {
            "Authorization": auth_token,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json",
        }
    )
    print_to_both(f"Authorization: {auth_token}")
    return auth_token


def get_kb_ids():
    response = session.get(kb_list_url)
    print_to_both(f"kb_list 状态码: {response.status_code}")
    try:
        kb_data = response.json()
        kb_ids = [kb["id"] for kb in kb_data.get("data", {}).get("kbs", [])]
        print_to_both(f"提取的kb_ids: {kb_ids}")
        return kb_ids
    except Exception as e:
        print_to_both(f"获取知识库失败: {e}")
        return []


def create_dialog(kb_ids):
    url = f"{BASE_URL}/dialog/set"
    payload = {
        "name": "test",
        "icon": "",
        "language": "English",
        "kb_ids": kb_ids,
        "llm_id": "deepseek-r1:7b@Ollama",
        "llm_setting": {
            "temperature": 0.1,
            "top_p": 0.3,
            "presence_penalty": 0.4,
            "frequency_penalty": 0.7,
        },
        "prompt_config": {
            "empty_response": "",
            "prologue": "你好！ 我是你的助理，有什么可以帮到你的吗？",
            "quote": True,
            "keyword": False,
            "parameters": [{"key": "knowledge", "optional": False}],
            "reasoning": False,
            "refine_multiturn": False,
            "system": "你是一个智能助手，请总结知识库的内容来回答问题，请列举知识库中的数据详细回答。当所有知识库内容都与问题无关时，根据你的原本的知识来进行回答。回答需要考虑聊天历史。\n以下是知识库：\n{knowledge}\n以上是知识库。",
            "tts": False,
            "use_kg": False,
            "similarity_threshold": 0.2,
            "top_n": 8,
            "vector_similarity_weight": 0.3,
        },
    }
    response = session.post(url, json=payload)
    response.raise_for_status()
    dialog_id = response.json()["data"]["id"]
    print_to_both(f"Dialog 创建成功: {dialog_id}")
    return dialog_id


def create_conversation(dialog_id):
    global message_history
    message_history = []  # 每次新对话清空历史

    url = f"{BASE_URL}/conversation/set"
    full_uuid = str(uuid.uuid4())
    conversation_id = full_uuid[:-4]

    # 第一条消息
    assistant_message = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": "你好！ 我是你的助理，有什么可以帮到你的吗？",
    }

    message_history.append(assistant_message)

    payload = {
        "conversation_id": conversation_id,
        "dialog_id": dialog_id,
        "name": "你好",
        "is_new": True,
        "message": [{"role": "assistant", "content": "你好"}],
    }
    response = session.post(url, json=payload)
    print_to_both(f"Conversation 状态码: {response.status_code}")
    print_to_both(f"Conversation 返回内容: {response.text}")

    try:
        res_json = response.json()
    except Exception as e:
        print_to_both(f"响应解析失败: {e}")
        return None

    if response.status_code != 200 or res_json.get("code") != 0:
        print_to_both(f"Conversation 创建失败，完整响应: {res_json}")
        return None

    print_to_both(f"Conversation 创建成功: {conversation_id}")
    return conversation_id


def send_completion_stream(conversation_id, user_message):
    global message_history

    user_message_id = str(uuid.uuid4())
    message_history.append(
        {"id": user_message_id, "role": "user", "content": user_message, "doc_ids": []}
    )

    payload = {
        "conversation_id": conversation_id,
        "messages": message_history,
    }

    with session.post(completion_url, json=payload, stream=True) as response:
        if response.status_code != 200:
            print_to_both(f"completion 请求失败: {response.status_code}")
            return
        print_to_both("completion 接口流式响应开始：")
        client = SSEClient(response)

        answer_content = ""
        answer_id = str(uuid.uuid4())
        for event in client.events():
            print_to_both(f"事件数据: {event.data}")
            try:
                data = json.loads(event.data)["data"]
                if "answer" in data:
                    answer_content = data["answer"]
            except Exception as e:
                print_to_both(f"事件解析失败: {e}")
                continue

        # 添加助手回复
        message_history.append(
            {"id": answer_id, "role": "assistant", "content": answer_content}
        )
        print(message_history)


def send_ask_stream(question, kb_ids, user_id=""):
    payload = {
        "question": question,
        "conversation_id": "",
        "user_id": user_id,
        "kb_ids": kb_ids,
    }
    with session.post(ask_url, json=payload, stream=True) as response:
        if response.status_code != 200:
            print_to_both(f"ask 请求失败: {response.status_code}")
            return
        print_to_both("ask 接口流式响应开始：")
        client = SSEClient(response)
        for event in client.events():
            print_to_both(f"事件数据: {event.data}")


def retrieval_test(question, kb_ids):
    payload = {
        "kb_id": kb_ids,
        "highlight": True,
        "question": question,
        "page": 1,
        "size": 10,
    }
    response = session.post(retrieval_test_url, json=payload)
    response.raise_for_status()
    result = response.json()
    print_to_both(
        f"retrieval_test 返回:\n{json.dumps(result, ensure_ascii=False, indent=2)}"
    )
    return result


def related_questions(question):
    payload = {"question": question}
    response = session.post(related_questions_url, json=payload)
    response.raise_for_status()
    result = response.json()
    print_to_both(
        f"related_questions 返回:\n{json.dumps(result, ensure_ascii=False, indent=2)}"
    )
    return result


if __name__ == "__main__":
    email = "123@123.com"
    password = "hXWqKtPnAt+tvQeaKHh87nNc5xbuVJu5thZtH1gBOzFfwmjml8DJp3/E2HzILWJVqWy3Vp79g3wPC67+ImkG1IQyvD4BSYXp4zlUy++toYQO1GOEMys4Xn8Xta2G9KTkjhWrR9qfOyEroIIzXEy2+HBf4DenGXPABLIh0HAGlZSdizpq3mHbIhHm26CDl0OIT7S7xd6YCOYpM9VC6IMYQI/a3r5qZc8cIvkQGrEnrhlPVIPQocxY5shmXwaEJxugPd/kezvsienh6TEfctqVcSwIssIgPBunOVJb2PDCF/NevwS3ZGqmFn7VIxUwHi0oz4KYZsudj+K8aJqG/8Jj8w=="

    if login(email, password):
        kb_ids = get_kb_ids()
        question = "多模态大模型是什么"

        # 完整对话流式流程
        # dialog_id = create_dialog(kb_ids)
        # conversation_id = create_conversation(dialog_id)

        # while True:
        #     question = input("请输入你的问题（输入 q 退出）：")
        #     if question.lower() == "q":
        #         break
        #     send_completion_stream(conversation_id, question)

        # 可选额外接口
        retrieval_test(question, kb_ids)
        related_questions(question)
        send_ask_stream(question, kb_ids)  # 流式接口（可选）
