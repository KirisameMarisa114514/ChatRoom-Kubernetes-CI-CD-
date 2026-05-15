import json
import os
import urllib.request


def call_deepseek(user_message: str, system_prompt: str = "") -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    if not api_key:
        return "DeepSeek API Key 未配置，请检查 Kubernetes Secret。"

    url = base_url.rstrip("/") + "/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt or (
                    "你是一个 K8s 运维 Agent。"
                    "你只能做只读分析，不执行修改、删除、部署等操作。"
                    "如果需要实时状态，应优先建议用户查询 Pod、Service、Deployment、镜像版本。"
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "stream": False
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw)
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"DeepSeek 调用失败：{e}"