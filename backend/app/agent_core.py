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

    return (
        "我是 K8s 运维 Agent，目前支持这些查询：\n"
        "1. 查看 Pod 状态\n"
        "2. 查看 Service 状态\n"
        "3. 查看 Deployment 状态\n"
        "4. 查看当前镜像版本\n"
        "5. 查看 registry 镜像仓库\n"
        "6. 查看系统资源\n\n"
        "你可以问：当前服务运行情况怎么样？"
    )