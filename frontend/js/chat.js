// 退出登录
function logout() {
  if (AppState.ws) {
    AppState.ignoreNextClose = true;
    AppState.ws.close();
    AppState.ws = null;
  }

  AppState.currentUser = "";
  AppState.currentRoom = "";
  AppState.currentAvatarUrl = "";

  clearMessages();
  renderOnlineUsers([]);

  document.getElementById("authPanel").style.display = "block";
  document.getElementById("chatPanel").style.display = "none";

  document.getElementById("currentUser").innerText = "-";
  document.getElementById("avatarText").innerText = "U";
  document.getElementById("password").value = "";

  setCurrentAvatar("");
  setOnlineStatus("未登录", "");
  setRoomStatus("未进入房间");

  setTip("已退出登录，可以重新登录。");
}

// 连接后端 WebSocket 接口
async function connect() {
  const room = document.getElementById("room").value.trim();

  if (!AppState.currentUser) {
    alert("请先登录");
    return;
  }

  if (!room) {
    alert("房间不能为空");
    return;
  }

  AppState.currentRoom = room;

  setOnlineStatus("连接中：" + AppState.currentUser, "warning");
  setRoomStatus("正在进入：" + room);

  if (AppState.ws) {
    AppState.ignoreNextClose = true;
    AppState.ws.close();
  }

  clearMessages();
  renderOnlineUsers([]);

  addMessage({
    type: "system",
    message: `正在进入房间 ${room}...`
  });

  await loadHistory(room);

  AppState.ws = new WebSocket(`${WS_BASE}/ws/${room}/${AppState.currentUser}`);

  // 连接成功时执行
  AppState.ws.onopen = function () {
    setOnlineStatus("在线：" + AppState.currentUser, "online");
    setRoomStatus("当前房间：" + room);

    addMessage({
      type: "system",
      message: `已进入房间 ${room}`
    });
  };

  // 服务端发消息给前端
  AppState.ws.onmessage = function (event) {
    const data = JSON.parse(event.data);
    addMessage(data);
  };

  AppState.ws.onclose = function () {
    if (AppState.ignoreNextClose) {
      AppState.ignoreNextClose = false;
      return;
    }

    setOnlineStatus("连接断开：" + AppState.currentUser, "warning");
    setRoomStatus("未连接房间");

    addMessage({
      type: "system",
      message: "连接已断开"
    });
  };
}

// 把输入框里的内容发给后端
function sendMessage() {
  const input = document.getElementById("content");
  const content = input.value.trim();

  if (!AppState.ws || AppState.ws.readyState !== WebSocket.OPEN) {
    alert("请先进入房间，或等待连接成功");
    return;
  }

  if (!content) {
    return;
  }

  // 先在自己的页面显示自己发送的内容
  addMessage({
    type: "message",
    sender: AppState.currentUser,
    content: content,
    created_at: formatDateTime(new Date()),
    avatar_url: AppState.currentAvatarUrl
  });

  // 再发送给后端
  AppState.ws.send(JSON.stringify({
    content: content
  }));

  input.value = "";
}

// 暴露给 HTML onclick 使用
window.logout = logout;
window.connect = connect;
window.sendMessage = sendMessage;