from pathlib import Path

from fastapi import Depends
from .auth import LoginRequest, login_check, require_admin
from .agent_core import AgentChatRequest, agent_reply
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi import UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.db import (
    init_db,
    save_message,
    get_history,
    clear_history,
    create_user,
    verify_user,
    get_user,
    get_user_avatar_url,
    update_user_avatar_url,
)
from app.ws_manager import ConnectionManager
from app.upload import save_avatar_file


app = FastAPI(title="聊天室")
manager = ConnectionManager()

@app.post("/api/auth/login")
def admin_login(data: LoginRequest):
    return login_check(data)


@app.get("/api/auth/me")
def me(admin=Depends(require_admin)):
    return admin


@app.post("/api/agent/chat")
def agent_chat(data: AgentChatRequest, admin=Depends(require_admin)):
    reply = agent_reply(data.message)
    return {"reply": reply}

# backend 目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 挂载静态文件目录
# 浏览器可以通过 /static/avatars/xxx.png 访问头像
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "uploads")),
    name="static"
)


# 允许前端页面跨域访问后端，方便本地测试
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserForm(BaseModel):
    username: str
    password: str


# 初始化数据库
@app.on_event("startup")
def startup():
    init_db()


# 健康检查接口
@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# 注册接口
@app.post("/register")
def register(user: UserForm):
    ok = create_user(user.username, user.password)

    if not ok:
        raise HTTPException(status_code=400, detail="username already exists")

    return {
        "status": "ok",
        "message": "register success",
        "username": user.username
    }


# 登录接口
@app.post("/login")
def login(user: UserForm):
    ok = verify_user(user.username, user.password)

    if not ok:
        raise HTTPException(status_code=401, detail="invalid username or password")

    user_info = get_user(user.username)

    return {
        "status": "ok",
        "message": "login success",
        "username": user.username,
        "avatar_url": user_info["avatar_url"] if user_info else ""
    }


# 上传 / 更新头像
@app.post("/avatar")
async def upload_avatar(
    username: str = Form(...),
    file: UploadFile = File(...)
):
    avatar_url = await save_avatar_file(username, file)

    ok = update_user_avatar_url(username, avatar_url)

    if not ok:
        raise HTTPException(status_code=404, detail="user not found")

    return {
        "status": "ok",
        "message": "avatar updated",
        "username": username,
        "avatar_url": avatar_url
    }


# 历史消息接口
@app.get("/history/{room_id}")
def history(room_id: str):
    return {
        "room_id": room_id,
        "messages": get_history(room_id)
    }


# 清除某个房间的历史消息
@app.delete("/history/{room_id}")
def delete_history(room_id: str):
    deleted_count = clear_history(room_id)

    return {
        "status": "ok",
        "room_id": room_id,
        "deleted": deleted_count
    }


# WebSocket 聊天接口
@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_chat(websocket: WebSocket, room_id: str, user_id: str):
    await manager.connect(room_id, user_id, websocket)

    # 用户进入房间后，广播在线用户列表
    await manager.broadcast_online_users(room_id)

    try:
        while True:
            data = await websocket.receive_json()
            content = data["content"]

            message = save_message(room_id, user_id, content)
            avatar_url = get_user_avatar_url(user_id)

            await manager.send_to_user(
                room_id,
                user_id,
                {
                    "type": "ack",
                    "message_id": message["id"],
                    "status": "sent"
                }
            )

            await manager.broadcast(
                room_id,
                {
                    "type": "message",
                    "message_id": message["id"],
                    "sender": user_id,
                    "content": content,
                    "created_at": message["created_at"],
                    "avatar_url": avatar_url
                },
                exclude_user=user_id
            )

    except WebSocketDisconnect:
        manager.disconnect(room_id, user_id)

        # 用户离开房间后，重新广播在线用户列表
        await manager.broadcast_online_users(room_id)
