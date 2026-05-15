from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # 保存所有 WebSocket 连接
        # 结构：
        # {
        #   "room1": {
        #       "alice": websocket,
        #       "bob": websocket
        #   }
        # }
        self.active_connections: dict[str, dict[str, WebSocket]] = {}

    # 用户连接
    async def connect(self, room_id: str, user_id: str, websocket: WebSocket):
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}

        self.active_connections[room_id][user_id] = websocket

    # 用户断开连接
    def disconnect(self, room_id: str, user_id: str):
        if room_id not in self.active_connections:
            return

        self.active_connections[room_id].pop(user_id, None)

        # 如果房间没人了，就删除这个房间
        if not self.active_connections[room_id]:
            self.active_connections.pop(room_id, None)

    # 给某个用户单独发消息
    async def send_to_user(self, room_id: str, user_id: str, message: dict):
        if room_id not in self.active_connections:
            return

        websocket = self.active_connections[room_id].get(user_id)

        if websocket:
            await websocket.send_json(message)

    # 给房间内用户广播消息
    async def broadcast(self, room_id: str, message: dict, exclude_user: str | None = None):
        if room_id not in self.active_connections:
            return

        for user_id, websocket in self.active_connections[room_id].items():
            if exclude_user and user_id == exclude_user:
                continue

            await websocket.send_json(message)

    # 获取某个房间在线用户
    def get_room_users(self, room_id: str) -> list[str]:
        if room_id not in self.active_connections:
            return []

        return list(self.active_connections[room_id].keys())

    # 广播当前房间在线用户列表
    async def broadcast_online_users(self, room_id: str):
        users = self.get_room_users(room_id)

        await self.broadcast(
            room_id,
            {
                "type": "online_users",
                "users": users
            }
        )