// 后端 HTTP 和 WebSocket 地址
window.API_BASE = "http://127.0.0.1:8000";
window.WS_BASE = "ws://127.0.0.1:8000";

// 全局状态
window.AppState = {
  ws: null,
  currentUser: "",
  currentRoom: "",
  currentAvatarUrl: "",
  ignoreNextClose: false
};