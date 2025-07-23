# -*- coding: utf-8 -*-
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
    with open(r"接口调试代码\dsl_aiwriting_runse.json", "r", encoding="utf-8") as f:
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
    with open("接口调试代码/dsl_aiwriting_runse.json", "r", encoding="utf-8") as f:
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
        if q.get('key') == 'article':
            q['value'] = '文章润色测试——大模型.docx\n在人工智能领域里，大模型越来越重要。过去我们常用小模型来做事情，比如分类、预测等，但是大模型出现之后，很多问题可以做得更好。大模型就是参数很多的模型，参数越多，模型的能力越强。像GPT、PaLM、Gemini、Qwen这些大模型，它们参数从几十亿到几千亿甚至万亿。这样的大规模，让它们能完成各种任务。大模型的训练需要大量数据。这些数据包括网络上的文章、书籍、对话、代码等等。模型会从这些数据里学习语言规律。训练时，用GPU、TPU这些计算设备，训练过程可能持续几天到几周。有时候要上千块显卡一起训练，需要花很多钱。训练完成后，就可以用来生成文本、写文章、回答问题、翻译语言、写代码等等。但是大模型也有问题。第一是成本很高，不是每个人都做得起。第二是数据质量不一致，网络上的东西有好的也有坏的，一些错误的信息也会带到模型里。模型可能会“胡说八道”，也就是我们常说的“幻觉”。另外虽然模型可以回答问题，但有时候不够精准，或者不知道最新的事实，因为训练数据可能不包含最新的信息。为了解决这些问题，研究人员提出了一些方法。比如指令微调（instruction tuning），就是用人工标注好的指令-回答对，训练模型让它更懂怎么回答；有些方法用RLHF，就是用人类来评价模型回答好不好，再让模型自己学习怎么做得更好。还有模型压缩技术，像量化、剪枝、蒸馏等，让模型变小但性能不差，方便部署到手机、边缘设备上。大模型的硬件支持很关键。比如NVIDIA的A100、H100，Google的TPU，华为的昇腾，都是很强的芯片。硬件发展带动了模型规模的增长。还有模型并行、数据并行、流水线并行等技术，让训练可以在很多机器上同时进行。除此之外，混合精度训练能减少显存消耗，提高效率。除了单纯的语言模型，现在还有多模态大模型。它们不仅能理解文字，还可以理解图像、视频、音频等多种信息。像Qwen-VL、Gemini、Sora这些模型，能看图写故事，能对视频进行描述，甚至做跨模态的推理。未来，人机交互可能就通过语音、图像、文字等等方式进行，不再局限于键盘。大模型的应用领域非常广泛。在教育方面，可以用来自动批改作文，生成教学内容；在医疗行业，大模型可以辅助医生诊断，也可以整理病例信息；在金融领域，可以进行风险评估、市场预测等；在法律领域，可以帮助整理案例，给出法律咨询建议；在内容创作方面，可以协助写小说、剧本、论文初稿、广告文案等。但是大模型也带来一些社会问题。比如隐私泄露问题，如果模型训练数据包含敏感信息，可能被模型记住并泄露；还有伦理问题，比如生成不当内容、偏见问题；还有审批监管问题，目前很多国家还没有制定全面的大模型和AI监管政策；还有环境问题，大模型训练消耗很多能源，碳排放高。针对这些问题，很多人提出了解决思路。比如使用差分隐私、联邦学习等技术保护用户隐私；用偏见检测、可解释性方法提高模型公平和透明；在政策层面，一些国家已经开始制定AI法规，比如欧盟AI行为准则、美国的AI法案草案、中国的AI治理政策等；在能源方面，可以用更节能的芯片、绿色数据中心、可再生能源来降低碳足迹。现在还出现了很多开源大模型。过去大多数大模型都由大型科技公司发布，但开源模型让更多研究者和开发者能用到，这推动了创新和社区合作。比较流行的开源模型有LLaMA、Mistral、Qwen-Open、ChatGLM等。这些模型虽然参数不一定比商业模型多，但可以进行本地部署、二次改进、定制化训练，灵活性高。当然，开源模型也存在风险。没有监管的开源模型可能被不当使用，比如生成虚假信息、网络攻击辅助、垃圾评论自动发布等。此外，它们可能缺少商业模型那样充分考虑的安全对齐机制，需要使用者自行进行风险评估和安全控制。在未来，模型可能越来越通用，更加“智能”。AGI（通用人工智能）是研究目标，虽然现在还没达到，但大模型是迈向AGI的重要基础。未来可能出现更强的推理能力、规划能力、甚至创造力。比如模型能够理解长篇文章的逻辑结构，能进行多步骤思考，能提出更有创造性的解决方案。此外，人机协同也会越来越紧密。未来的助手不仅帮你写，还可以与你讨论、提供建议、甚至一起“思考”。这种智能助手在科研、设计、法律、医疗都可能发挥巨大作用。它们会成为协作者，而不是工具。总的来说，大模型是人工智能发展中非常重要的一部分。它们带来了能力的跃升，也催生了很多新的挑战。训练成本、数据质量、推理效率、社会责任、监管治理、安全隐私、环境影响等问题都需要关注。未来如果这些问题都能被妥善解决，大模型就可能真正服务于各行各业，实现更广泛的价值。\n----\n'
        elif q.get('key') == 'instruction':
            q['value'] = '风格更加学术严谨'
    # 同步修改 graph.nodes 里的 query 字段
    for node in dsl_data.get('dsl', {}).get('graph', {}).get('nodes', []):
        form = node.get('data', {}).get('form', {})
        query_list = form.get('query', [])
        for q in query_list:
            if q.get('key') == 'article':
                q['value'] = '文章润色测试——大模型.docx\n在人工智能领域里，大模型越来越重要。过去我们常用小模型来做事情，比如分类、预测等，但是大模型出现之后，很多问题可以做得更好。大模型就是参数很多的模型，参数越多，模型的能力越强。像GPT、PaLM、Gemini、Qwen这些大模型，它们参数从几十亿到几千亿甚至万亿。这样的大规模，让它们能完成各种任务。大模型的训练需要大量数据。这些数据包括网络上的文章、书籍、对话、代码等等。模型会从这些数据里学习语言规律。训练时，用GPU、TPU这些计算设备，训练过程可能持续几天到几周。有时候要上千块显卡一起训练，需要花很多钱。训练完成后，就可以用来生成文本、写文章、回答问题、翻译语言、写代码等等。但是大模型也有问题。第一是成本很高，不是每个人都做得起。第二是数据质量不一致，网络上的东西有好的也有坏的，一些错误的信息也会带到模型里。模型可能会“胡说八道”，也就是我们常说的“幻觉”。另外虽然模型可以回答问题，但有时候不够精准，或者不知道最新的事实，因为训练数据可能不包含最新的信息。为了解决这些问题，研究人员提出了一些方法。比如指令微调（instruction tuning），就是用人工标注好的指令-回答对，训练模型让它更懂怎么回答；有些方法用RLHF，就是用人类来评价模型回答好不好，再让模型自己学习怎么做得更好。还有模型压缩技术，像量化、剪枝、蒸馏等，让模型变小但性能不差，方便部署到手机、边缘设备上。大模型的硬件支持很关键。比如NVIDIA的A100、H100，Google的TPU，华为的昇腾，都是很强的芯片。硬件发展带动了模型规模的增长。还有模型并行、数据并行、流水线并行等技术，让训练可以在很多机器上同时进行。除此之外，混合精度训练能减少显存消耗，提高效率。除了单纯的语言模型，现在还有多模态大模型。它们不仅能理解文字，还可以理解图像、视频、音频等多种信息。像Qwen-VL、Gemini、Sora这些模型，能看图写故事，能对视频进行描述，甚至做跨模态的推理。未来，人机交互可能就通过语音、图像、文字等等方式进行，不再局限于键盘。大模型的应用领域非常广泛。在教育方面，可以用来自动批改作文，生成教学内容；在医疗行业，大模型可以辅助医生诊断，也可以整理病例信息；在金融领域，可以进行风险评估、市场预测等；在法律领域，可以帮助整理案例，给出法律咨询建议；在内容创作方面，可以协助写小说、剧本、论文初稿、广告文案等。但是大模型也带来一些社会问题。比如隐私泄露问题，如果模型训练数据包含敏感信息，可能被模型记住并泄露；还有伦理问题，比如生成不当内容、偏见问题；还有审批监管问题，目前很多国家还没有制定全面的大模型和AI监管政策；还有环境问题，大模型训练消耗很多能源，碳排放高。针对这些问题，很多人提出了解决思路。比如使用差分隐私、联邦学习等技术保护用户隐私；用偏见检测、可解释性方法提高模型公平和透明；在政策层面，一些国家已经开始制定AI法规，比如欧盟AI行为准则、美国的AI法案草案、中国的AI治理政策等；在能源方面，可以用更节能的芯片、绿色数据中心、可再生能源来降低碳足迹。现在还出现了很多开源大模型。过去大多数大模型都由大型科技公司发布，但开源模型让更多研究者和开发者能用到，这推动了创新和社区合作。比较流行的开源模型有LLaMA、Mistral、Qwen-Open、ChatGLM等。这些模型虽然参数不一定比商业模型多，但可以进行本地部署、二次改进、定制化训练，灵活性高。当然，开源模型也存在风险。没有监管的开源模型可能被不当使用，比如生成虚假信息、网络攻击辅助、垃圾评论自动发布等。此外，它们可能缺少商业模型那样充分考虑的安全对齐机制，需要使用者自行进行风险评估和安全控制。在未来，模型可能越来越通用，更加“智能”。AGI（通用人工智能）是研究目标，虽然现在还没达到，但大模型是迈向AGI的重要基础。未来可能出现更强的推理能力、规划能力、甚至创造力。比如模型能够理解长篇文章的逻辑结构，能进行多步骤思考，能提出更有创造性的解决方案。此外，人机协同也会越来越紧密。未来的助手不仅帮你写，还可以与你讨论、提供建议、甚至一起“思考”。这种智能助手在科研、设计、法律、医疗都可能发挥巨大作用。它们会成为协作者，而不是工具。总的来说，大模型是人工智能发展中非常重要的一部分。它们带来了能力的跃升，也催生了很多新的挑战。训练成本、数据质量、推理效率、社会责任、监管治理、安全隐私、环境影响等问题都需要关注。未来如果这些问题都能被妥善解决，大模型就可能真正服务于各行各业，实现更广泛的价值。\n----\n'
            elif q.get('key') == 'instruction':
                q['value'] = '风格更加学术严谨'
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
