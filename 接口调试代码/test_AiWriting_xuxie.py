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
    with open(r"接口调试代码\dsl_aiwriting_xuxie.json", "r", encoding="utf-8") as f:
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
    with open("接口调试代码/dsl_aiwriting_xuxie.json", "r", encoding="utf-8") as f:
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
            q['value'] = '大模型.docx\n近年来，随着人工智能技术的飞速发展，大语言模型（Large Language Model，简称LLM）逐渐成为人工智能领域的研究热点。从最初的统计语言模型，到基于神经网络的序列模型，再到如今的千亿参数级别的大模型，语言模型的发展路径反映了AI技术的演进和技术瓶颈的不断突破。大语言模型的核心在于规模。传统的语言模型通常只能捕捉到局部的语言规律，而大模型通过堆叠更多的参数、使用更大规模的训练数据，能够学习更复杂的语义和语言逻辑关系。以GPT系列、PaLM、Gemini、Qwen等模型为例，它们的参数数量从几十亿逐步扩展到数千亿，甚至朝向万亿级别迈进。这种规模化的发展，使得模型具备了更强的泛化能力，能够处理各种自然语言任务，如文本生成、摘要、翻译、问答、代码补全等。但大模型的成功并不仅仅在于规模的堆叠，更重要的是训练策略和数据管理的优化。预训练-微调（Pretrain-Finetune）的范式曾经是主流，但近年来，指令微调（Instruction Tuning）、RLHF（人类反馈强化学习）、多任务协同学习等方法逐渐成为新趋势。这些技术让大语言模型从“语言预测机器”逐步转向“多功能助手”，不仅能模仿语言，还能理解任务意图，完成更加复杂的交互任务。大模型的训练通常需要海量的数据。公开网络数据、维基百科、书籍、代码库、论文、对话记录等，构成了大语言模型的训练语料。然而，数据质量问题也逐渐显现。网络数据包含大量噪声，低质量数据可能导致模型输出错误信息，甚至生成有害内容。因此，数据过滤、清洗和对齐成为大模型训练中的重要环节。部分企业和机构开始尝试构建高质量的专用数据集，以降低模型的幻觉率，提升知识的准确性。硬件资源是大模型发展的另一个关键因素。训练一个千亿参数级别的模型通常需要上千张GPU或者AI专用加速芯片，如NVIDIA的A100、H100，或是华为的Ascend系列，训练过程可能持续数周甚至数月。能源消耗巨大，也带来了环境和经济方面的争议。为了降低成本和提升效率，模型并行训练、混合精度计算、模型压缩等技术被广泛采用，同时也推动了专用AI芯片和分布式训练系统的发展。大模型的推理部署同样面临挑战。尽管参数规模巨大，但实际应用场景中，用户希望模型响应快速且资源占用低。为了满足这一需求，业界提出了量化、剪枝、蒸馏等模型压缩技术。例如，INT4、INT8量化可以大幅度减少模型的存储和计算开销，而知识蒸馏可以用小模型模拟大模型的行为，实现边缘部署。此外，LoRA（低秩适配）、P-Tuning等微调技术也使得企业可以在成本可控的情况下，快速定制属于自己的大模型。随着大模型的能力日益强大，应用场景逐步扩展到生产力工具、教育辅助、法律咨询、医疗健康、内容创作等各个领域。大模型甚至开始被用于代码生成、化学分子结构预测、工程设计等跨领域任务，逐步展现出通用人工智能（AGI）的雏形。然而，这也引发了关于模型滥用、伦理和监管的问题。如何防止大模型生成虚假信息、如何确保AI的透明度和可解释性，成为技术和社会亟需讨论的重要议题。另一个值得关注的现象是开源大模型的兴起。过去，大模型主要掌握在大型科技公司手中，但近年来，越来越多的开源项目如LLaMA、Mistral、Qwen、DeepSeek等逐步发布了自己的大模型权重。这推动了研究社区的繁荣，也使得中小企业和个人开发者有机会参与大模型的创新。但与此同时，开源模型的滥用风险也需要警惕，例如自动化生成垃圾信息、网络攻击辅助等问题。多模态大模型（Multi-modal LLM）的发展是目前的大模型研究新前沿。语言模型不再局限于文本，开始逐步接入图像、视频、音频、传感器数据，形成通用感知和生成能力。例如，Sora、Gemini、Qwen-VL等模型，已经可以做到文本生成、图片理解、视频描述甚至跨模态推理。这一趋势可能引发更广泛的技术革命，推动人机交互方式的根本变化。\n----\n'
        elif q.get('key') == 'instruction':
            q['value'] = '主要续写大模型应用方面的内容'
    # 同步修改 graph.nodes 里的 query 字段
    for node in dsl_data.get('dsl', {}).get('graph', {}).get('nodes', []):
        form = node.get('data', {}).get('form', {})
        query_list = form.get('query', [])
        for q in query_list:
            if q.get('key') == 'article':
                q['value'] = '大模型.docx\n近年来，随着人工智能技术的飞速发展，大语言模型（Large Language Model，简称LLM）逐渐成为人工智能领域的研究热点。从最初的统计语言模型，到基于神经网络的序列模型，再到如今的千亿参数级别的大模型，语言模型的发展路径反映了AI技术的演进和技术瓶颈的不断突破。大语言模型的核心在于规模。传统的语言模型通常只能捕捉到局部的语言规律，而大模型通过堆叠更多的参数、使用更大规模的训练数据，能够学习更复杂的语义和语言逻辑关系。以GPT系列、PaLM、Gemini、Qwen等模型为例，它们的参数数量从几十亿逐步扩展到数千亿，甚至朝向万亿级别迈进。这种规模化的发展，使得模型具备了更强的泛化能力，能够处理各种自然语言任务，如文本生成、摘要、翻译、问答、代码补全等。但大模型的成功并不仅仅在于规模的堆叠，更重要的是训练策略和数据管理的优化。预训练-微调（Pretrain-Finetune）的范式曾经是主流，但近年来，指令微调（Instruction Tuning）、RLHF（人类反馈强化学习）、多任务协同学习等方法逐渐成为新趋势。这些技术让大语言模型从“语言预测机器”逐步转向“多功能助手”，不仅能模仿语言，还能理解任务意图，完成更加复杂的交互任务。大模型的训练通常需要海量的数据。公开网络数据、维基百科、书籍、代码库、论文、对话记录等，构成了大语言模型的训练语料。然而，数据质量问题也逐渐显现。网络数据包含大量噪声，低质量数据可能导致模型输出错误信息，甚至生成有害内容。因此，数据过滤、清洗和对齐成为大模型训练中的重要环节。部分企业和机构开始尝试构建高质量的专用数据集，以降低模型的幻觉率，提升知识的准确性。硬件资源是大模型发展的另一个关键因素。训练一个千亿参数级别的模型通常需要上千张GPU或者AI专用加速芯片，如NVIDIA的A100、H100，或是华为的Ascend系列，训练过程可能持续数周甚至数月。能源消耗巨大，也带来了环境和经济方面的争议。为了降低成本和提升效率，模型并行训练、混合精度计算、模型压缩等技术被广泛采用，同时也推动了专用AI芯片和分布式训练系统的发展。大模型的推理部署同样面临挑战。尽管参数规模巨大，但实际应用场景中，用户希望模型响应快速且资源占用低。为了满足这一需求，业界提出了量化、剪枝、蒸馏等模型压缩技术。例如，INT4、INT8量化可以大幅度减少模型的存储和计算开销，而知识蒸馏可以用小模型模拟大模型的行为，实现边缘部署。此外，LoRA（低秩适配）、P-Tuning等微调技术也使得企业可以在成本可控的情况下，快速定制属于自己的大模型。随着大模型的能力日益强大，应用场景逐步扩展到生产力工具、教育辅助、法律咨询、医疗健康、内容创作等各个领域。大模型甚至开始被用于代码生成、化学分子结构预测、工程设计等跨领域任务，逐步展现出通用人工智能（AGI）的雏形。然而，这也引发了关于模型滥用、伦理和监管的问题。如何防止大模型生成虚假信息、如何确保AI的透明度和可解释性，成为技术和社会亟需讨论的重要议题。另一个值得关注的现象是开源大模型的兴起。过去，大模型主要掌握在大型科技公司手中，但近年来，越来越多的开源项目如LLaMA、Mistral、Qwen、DeepSeek等逐步发布了自己的大模型权重。这推动了研究社区的繁荣，也使得中小企业和个人开发者有机会参与大模型的创新。但与此同时，开源模型的滥用风险也需要警惕，例如自动化生成垃圾信息、网络攻击辅助等问题。多模态大模型（Multi-modal LLM）的发展是目前的大模型研究新前沿。语言模型不再局限于文本，开始逐步接入图像、视频、音频、传感器数据，形成通用感知和生成能力。例如，Sora、Gemini、Qwen-VL等模型，已经可以做到文本生成、图片理解、视频描述甚至跨模态推理。这一趋势可能引发更广泛的技术革命，推动人机交互方式的根本变化。\n----\n'
            elif q.get('key') == 'instruction':
                q['value'] = '主要续写大模型应用方面的内容'
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
