"""
Kubernetes 集群与系统状态运维工具模块
提供基于 Kubernetes API 的只读查询接口，用于获取 Pod、Service、Deployment、
镜像信息，以及私有镜像仓库目录和主机内存状态。
"""

import json
import urllib.request
from kubernetes import client, config

# 默认操作命名空间
NAMESPACE = "default"


def load_k8s_config():
    """
    加载 Kubernetes 配置。
    优先尝试集群内部配置（Pod 内运行），失败则回退到本地 kubeconfig。
    返回 (成功标志, 配置来源) 元组。
    """
    try:
        config.load_incluster_config()
        return True, "incluster"
    except Exception:
        try:
            config.load_kube_config()
            return True, "kubeconfig"
        except Exception as e:
            return False, str(e)


def get_k8s_pods() -> str:
    """获取当前命名空间下所有 Pod 的概览表格（含状态、IP、节点）。"""
    ok, source = load_k8s_config()
    if not ok:
        return f"K8s config load failed: {source}"

    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace=NAMESPACE)

    lines = ["NAME\tREADY\tSTATUS\tRESTARTS\tIP\tNODE"]
    for pod in pods.items:
        ready_count = 0
        total_count = 0
        restart_count = 0

        statuses = pod.status.container_statuses or []
        for s in statuses:
            total_count += 1
            if s.ready:
                ready_count += 1
            restart_count += s.restart_count

        lines.append(
            f"{pod.metadata.name}\t"
            f"{ready_count}/{total_count}\t"
            f"{pod.status.phase}\t"
            f"{restart_count}\t"
            f"{pod.status.pod_ip or '-'}\t"
            f"{pod.spec.node_name or '-'}"
        )

    return "\n".join(lines)


def get_k8s_services() -> str:
    """获取当前命名空间下所有 Service 的概要表格（含类型、Cluster IP、端口）。"""
    ok, source = load_k8s_config()
    if not ok:
        return f"K8s config load failed: {source}"

    v1 = client.CoreV1Api()
    services = v1.list_namespaced_service(namespace=NAMESPACE)

    lines = ["NAME\tTYPE\tCLUSTER-IP\tPORTS"]
    for svc in services.items:
        ports = []
        for p in svc.spec.ports or []:
            if p.node_port:
                ports.append(f"{p.port}:{p.node_port}/{p.protocol}")
            else:
                ports.append(f"{p.port}/{p.protocol}")

        lines.append(
            f"{svc.metadata.name}\t"
            f"{svc.spec.type}\t"
            f"{svc.spec.cluster_ip}\t"
            f"{','.join(ports)}"
        )

    return "\n".join(lines)


def get_k8s_deployments() -> str:
    """获取当前命名空间下所有 Deployment 的状态表格（含副本状态、镜像）。"""
    ok, source = load_k8s_config()
    if not ok:
        return f"K8s config load failed: {source}"

    apps = client.AppsV1Api()
    deployments = apps.list_namespaced_deployment(namespace=NAMESPACE)

    lines = ["NAME\tREADY\tUP-TO-DATE\tAVAILABLE\tIMAGE"]
    for deploy in deployments.items:
        containers = deploy.spec.template.spec.containers or []
        image = containers[0].image if containers else "-"

        lines.append(
            f"{deploy.metadata.name}\t"
            f"{deploy.status.ready_replicas or 0}/{deploy.spec.replicas or 0}\t"
            f"{deploy.status.updated_replicas or 0}\t"
            f"{deploy.status.available_replicas or 0}\t"
            f"{image}"
        )

    return "\n".join(lines)


def get_current_images() -> str:
    """查询 chat-backend 和 chat-frontend 这两个关键 Deployment 当前使用的容器镜像。"""
    ok, source = load_k8s_config()
    if not ok:
        return f"K8s config load failed: {source}"

    apps = client.AppsV1Api()
    result = []

    for name in ["chat-backend", "chat-frontend"]:
        try:
            deploy = apps.read_namespaced_deployment(name=name, namespace=NAMESPACE)
            containers = deploy.spec.template.spec.containers or []
            image = containers[0].image if containers else "-"
            result.append(f"{name} image: {image}")
        except Exception as e:
            result.append(f"{name} image query failed: {e}")

    return "\n".join(result)


def get_registry_catalog() -> str:
    """
    查询内网私有 Docker Registry 的仓库目录。
    通过 HTTP GET 访问 192.168.30.10:5000/v2/_catalog 接口。
    """
    url = "http://192.168.30.10:5000/v2/_catalog"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = response.read().decode("utf-8")
            parsed = json.loads(data)
            return json.dumps(parsed, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Registry query failed: {e}"


def get_system_status() -> str:
    """
    获取主机内存基本状态。
    直接读取 /proc/meminfo 的前 5 行，提供概要信息。
    """
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            mem_lines = f.read().splitlines()[:5]

        return "Memory:\n" + "\n".join(mem_lines)
    except Exception as e:
        return f"System status query failed: {e}"
