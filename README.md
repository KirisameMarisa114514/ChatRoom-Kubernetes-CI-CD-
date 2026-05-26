# ChatRoom

基于 **FastAPI + WebSocket + Docker + Kubernetes + Jenkins CI/CD** 的实时聊天室系统，内置 **AI 运维 Agent 管理后台**。

本项目以聊天室为核心业务，提供用户注册、登录、实时聊天、历史消息、头像上传等功能；同时引入 Docker、Kubernetes、Jenkins、本地镜像仓库和 metrics-server，实现容器化部署、自动化发布和真实资源监控。管理员后台接入 DeepSeek API，可通过自然语言查询系统运行状态和 Kubernetes 资源信息。

---

## 项目定位

ChatRoom 是一个面向课程设计、云原生实践和项目答辩的综合型工程项目。

核心目标：

- 普通用户可以使用实时聊天室。
- 管理员可以进入后台查看系统运行状态。
- 项目可以通过 Jenkins 实现 CI/CD 自动部署。
- 系统运行在 Kubernetes 集群中。
- 后台 Agent 可以查询 Pod、Service、Deployment、镜像版本和资源使用情况。
- DeepSeek 作为智能问答能力，为运维分析提供辅助解释。

---

## 功能特性

### 普通聊天室

- 用户注册
- 用户登录
- WebSocket 实时聊天
- 房间聊天
- 历史消息查询
- 历史消息清除
- 头像上传
- 在线用户显示

### 管理员后台

- 独立管理员登录页
- 集群健康状态展示
- 节点状态展示
- CPU / 内存真实使用率展示
- Pod / Service / Deployment 数量展示
- K8s 运维 Agent 问答
- DeepSeek 自然语言解释
- 系统资源查询
- 镜像版本查询

### DevOps 能力

- Docker 前后端容器化
- Kubernetes 部署
- NodePort 暴露前端服务
- ClusterIP 暴露后端服务
- Jenkins 自动构建与部署
- 本地 Registry 镜像仓库
- metrics-server 资源监控
- Sakura-frp 公网映射预留

---

## 技术栈

| 模块         | 技术                            |
| ------------ | ------------------------------- |
| 前端         | HTML / CSS / JavaScript / Nginx |
| 后端         | Python / FastAPI / WebSocket    |
| 数据库       | SQLite                          |
| 容器化       | Docker                          |
| 容器编排     | Kubernetes                      |
| CI/CD        | Jenkins                         |
| 镜像仓库     | registry:2                      |
| AI 能力      | DeepSeek API                    |
| 资源监控     | metrics-server                  |
| K8s API 调用 | Kubernetes Python Client        |
| 公网映射     | Sakura-frp                      |

---

## 项目结构

```text
chat-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 主入口
│   │   ├── db.py                # SQLite 数据库操作
│   │   ├── ws_manager.py        # WebSocket 连接管理
│   │   ├── upload.py            # 头像上传
│   │   ├── auth.py              # 管理员认证
│   │   ├── agent_core.py        # 运维 Agent 逻辑
│   │   ├── ops_tools.py         # K8s / metrics 查询工具
│   │   └── llm_client.py        # DeepSeek 调用封装
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── index.html               # 普通聊天室页面
│   ├── admin.html               # 管理员后台页面
│   ├── nginx.conf               # Nginx 反向代理配置
│   ├── css/
│   │   ├── style.css
│   │   └── admin.css
│   ├── js/
│   │   ├── state.js
│   │   ├── ui.js
│   │   ├── api.js
│   │   ├── chat.js
│   │   ├── main.js
│   │   ├── auth-fix.js
│   │   └── admin-agent.js
│   └── Dockerfile
│
├── k8s/
│   ├── backend.yaml             # 后端 Deployment / Service
│   ├── frontend.yaml            # 前端 Deployment / Service
│   └── backend-rbac.yaml        # 后端 ServiceAccount / RBAC
│
├── deploy.sh                    # 自动构建、推送、部署脚本
├── Jenkinsfile                  # Jenkins Pipeline
├── docker-compose.yml           # 本地测试配置
└── README.md
```



## 系统架构

```
Browser
  |
  | 访问 NodePort 30080
  v
chat-frontend Service
  |
  v
Nginx Frontend Container
  |
  |-- 普通用户接口
  |     /register
  |     /login
  |     /avatar
  |     /history/{room_id}
  |     /ws/{room_id}/{user_id}
  |
  |-- 管理员接口
  |     /api/auth/login
  |     /api/agent/chat
  |     /api/ops/summary
  v
chat-backend Service
  |
  v
FastAPI Backend Container
  |
  |-- SQLite
  |-- WebSocket
  |-- Kubernetes API
  |-- metrics-server
  |-- DeepSeek API
```

------

## 页面入口

普通聊天室：

```
http://192.168.30.10:30080/
```

管理员后台：

```
http://192.168.30.10:30080/admin.html
```

Jenkins：

```
http://192.168.30.10:8080
```

本地镜像仓库：

```
http://192.168.30.10:5000/v2/_catalog
```

> 注意：公网映射时只建议暴露 `30080`，不要暴露 Jenkins 的 `8080` 和 Registry 的 `5000`。

------

## 快速启动

### 1. 本地 Docker Compose 测试

```
docker compose up -d --build
```

访问：

```
http://127.0.0.1:30080/
```

------

### 2. Kubernetes 部署

应用 RBAC：

```
kubectl apply -f k8s/backend-rbac.yaml
```

应用后端：

```
kubectl apply -f k8s/backend.yaml
```

应用前端：

```
kubectl apply -f k8s/frontend.yaml
```

查看状态：

```
kubectl get pods -o wide
kubectl get svc
kubectl get deploy
```

------

### 3. 使用部署脚本

项目提供 `deploy.sh`，用于自动完成镜像构建、推送和 K8s 更新。

```
./deploy.sh v1.0
```

脚本主要流程：

```
1. 构建 backend 镜像
2. 构建 frontend 镜像
3. 推送镜像到本地 registry
4. 更新 Kubernetes Deployment 镜像版本
5. 等待 rollout 完成
6. 输出访问地址
```

------

## CI/CD 流程

本项目使用 Jenkins 实现自动化构建与部署。

流程如下：

```
git push
  |
  v
Jenkins Poll SCM / Webhook
  |
  v
执行 Jenkinsfile
  |
  v
构建前后端 Docker 镜像
  |
  v
推送到本地 Registry
  |
  v
更新 Kubernetes Deployment
  |
  v
自动完成上线
```

常用检查命令：

```
kubectl rollout status deployment/chat-backend
kubectl rollout status deployment/chat-frontend
kubectl get pods -o wide
```

------

## Kubernetes 资源说明

### 后端

```
Deployment: chat-backend
Service: chat-backend
Type: ClusterIP
Port: 8000
```

### 前端

```
Deployment: chat-frontend
Service: chat-frontend
Type: NodePort
NodePort: 30080
```

### RBAC

后端通过 `ServiceAccount` 访问 Kubernetes API。

主要资源：

```
ServiceAccount: chat-backend-sa
Role: chat-backend-readonly
RoleBinding: chat-backend-readonly-binding
ClusterRole: chat-backend-metrics-readonly
ClusterRoleBinding: chat-backend-metrics-readonly-binding
```

用途：

- 查询 Pod
- 查询 Service
- 查询 Deployment
- 查询 Node
- 查询 metrics.k8s.io 指标

------

## AI 运维 Agent

管理员后台提供 K8s 运维 Agent。

支持示例问题：

```
查看当前 pod 状态
查看 service 状态
查看 deployment 状态
查看当前镜像版本
查看系统资源
这个项目当前运行状态怎么样？
K8s 中 Service 的作用是什么？
```

Agent 逻辑：

```
用户输入
  |
  v
/api/agent/chat
  |
  v
关键词判断
  |
  |-- Pod / Service / Deployment / 镜像版本
  |      -> 调用 Kubernetes API
  |
  |-- 系统资源
  |      -> 调用 metrics-server
  |
  |-- 普通解释类问题
         -> 调用 DeepSeek API
```

------

## DeepSeek 配置

DeepSeek API Key 不应写入前端或 GitHub 仓库。

推荐使用 Kubernetes Secret 注入：

```
kubectl create secret generic deepseek-secret \
  --from-literal=DEEPSEEK_API_KEY='your_deepseek_api_key' \
  --from-literal=DEEPSEEK_BASE_URL='https://api.deepseek.com' \
  --from-literal=DEEPSEEK_MODEL='deepseek-chat'
```

在 `backend.yaml` 中通过 `envFrom` 注入：

```
envFrom:
  - secretRef:
      name: deepseek-secret
```

------

## 管理员账号配置

管理员账号密码也建议使用 Kubernetes Secret 管理：

```
kubectl create secret generic admin-secret \
  --from-literal=ADMIN_USERNAME='admin' \
  --from-literal=ADMIN_PASSWORD='your_strong_password' \
  --from-literal=ADMIN_TOKEN='your_random_token'
```

在 `backend.yaml` 中添加：

```
envFrom:
  - secretRef:
      name: deepseek-secret
  - secretRef:
      name: admin-secret
```

> 不建议将真实管理员密码提交到 GitHub。

------

## metrics-server

项目使用 metrics-server 获取真实 CPU / 内存数据。

安装后验证：

```
kubectl get apiservice v1beta1.metrics.k8s.io
kubectl top nodes
kubectl top pods
```

成功示例：

```
NAME          CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
k8s-master    170m         2%     2200Mi          58%
k8s-worker1   167m         4%     1121Mi          29%
```

管理员后台通过：

```
GET /api/ops/summary
```

获取真实资源数据。

------

## 常用命令

查看节点：

```
kubectl get nodes -o wide
```

查看 Pod：

```
kubectl get pods -o wide
```

查看服务：

```
kubectl get svc
```

查看部署：

```
kubectl get deploy
```

查看资源使用：

```
kubectl top nodes
kubectl top pods
```

查看后端日志：

```
kubectl logs deploy/chat-backend --tail=100
```

查看前端日志：

```
kubectl logs deploy/chat-frontend --tail=100
```

重启后端：

```
kubectl rollout restart deployment/chat-backend
```

重启前端：

```
kubectl rollout restart deployment/chat-frontend
```

------

## 公网映射

项目预留 Sakura-frp 公网映射方案。

推荐只映射：

```
192.168.30.10:30080
```

不建议映射：

```
192.168.30.10:8080   Jenkins
192.168.30.10:5000   Registry
```

如果 Sakura-frp 客户端运行在 Windows 宿主机，本地地址应填写：

```
192.168.30.10
```

本地端口填写：

```
30080
```

------

## 安全注意事项

上传 GitHub 前请确认不要提交：

```
backend/venv/
backend/data/messages.db
backend/uploads/
.env
DeepSeek API Key
管理员真实密码
私钥文件
```

推荐 `.gitignore`：

```
backend/venv/
backend/app/__pycache__/
*.pyc

backend/data/*.db
backend/uploads/

.env
*.key
*.pem
```

------



## 当前版本

```
v1.0
```

v1.0 已实现：

- 普通聊天室
- 管理员后台
- K8s 运维 Agent
- DeepSeek 接入
- Jenkins CI/CD
- 本地 Registry
- metrics-server 真实资源监控
- Sakura-frp 公网映射预留