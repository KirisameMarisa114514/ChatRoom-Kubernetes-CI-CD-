from .llm_client import call_deepseek
from pydantic import BaseModel
from .ops_tools import (
    get_k8s_pods,
    get_k8s_services,
    get_k8s_deployments,
    get_current_images,
    get_registry_catalog,
    get_system_status,
)


class AgentChatRequest(BaseModel):
    message: str


def agent_reply(message: str) -> str:
    msg = message.lower()

    if any(word in msg for word in ["pod", "pods", "容器", "运行", "状态"]):
        return "当前 Pod 状态：\n\n" + get_k8s_pods()

    if any(word in msg for word in ["svc", "service", "服务", "端口"]):
        return "当前 Service 状态：\n\n" + get_k8s_services()

    if any(word in msg for word in ["deploy", "deployment", "部署"]):
        return "当前 Deployment 状态：\n\n" + get_k8s_deployments()

    if any(word in msg for word in ["镜像", "image", "版本", "version"]):
        return "当前镜像版本：\n\n" + get_current_images()

    if any(word in msg for word in ["registry", "仓库", "镜像仓库"]):
        return "当前 Registry 内容：\n\n" + get_registry_catalog()

    if any(word in msg for word in ["内存", "磁盘", "资源", "system", "cpu"]):
        return "当前系统资源：\n\n" + get_system_status()

    return call_deepseek(
        message,
        system_prompt=(
            "你是一个 K8s 运维 Agent。"
            "项目是一个 FastAPI + WebSocket + SQLite + Kubernetes + Jenkins CI/CD 的聊天室系统。"
            "你可以解释项目架构、运维状态含义、K8s 概念和排错思路。"
            "不要编造实时状态。实时状态应通过固定工具查询。"
        )
    )
