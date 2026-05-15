// 显示注册 / 登录提示信息
function setTip(text, type = "") {
  const tip = document.getElementById("authTip");
  tip.innerText = text;
  tip.className = "tip " + type;
}

// 更新左侧在线状态
function setOnlineStatus(text, state = "") {
  const statusDot = document.getElementById("statusDot");
  const loginStatus = document.getElementById("loginStatus");

  loginStatus.innerText = text;
  statusDot.className = "status-dot";

  if (state) {
    statusDot.classList.add(state);
  }
}

// 更新当前房间状态
function setRoomStatus(text) {
  document.getElementById("roomStatus").innerText = text;
}

// 获取完整头像地址
function getFullAvatarUrl(avatarUrl) {
  if (!avatarUrl) {
    return "";
  }

  if (avatarUrl.startsWith("http://") || avatarUrl.startsWith("https://")) {
    return avatarUrl;
  }

  return API_BASE + avatarUrl;
}

// 设置当前用户头像
function setCurrentAvatar(avatarUrl) {
  AppState.currentAvatarUrl = avatarUrl || "";

  const avatarImg = document.getElementById("avatarImg");
  const avatarText = document.getElementById("avatarText");

  if (AppState.currentAvatarUrl) {
    avatarImg.src = getFullAvatarUrl(AppState.currentAvatarUrl);
    avatarImg.style.display = "flex";
    avatarText.style.display = "none";
  } else {
    avatarImg.style.display = "none";
    avatarText.style.display = "flex";
    avatarText.innerText = AppState.currentUser
      ? AppState.currentUser.charAt(0).toUpperCase()
      : "U";
  }
}

// 登录成功后切换到聊天界面
function showChat(username, avatarUrl = "") {
  AppState.currentUser = username;
  AppState.currentAvatarUrl = avatarUrl || "";

  document.getElementById("currentUser").innerText = username;
  document.getElementById("avatarText").innerText = username.charAt(0).toUpperCase();

  setCurrentAvatar(avatarUrl);

  setOnlineStatus("已登录：" + username, "warning");
  setRoomStatus("未进入房间");

  document.getElementById("authPanel").style.display = "none";
  document.getElementById("chatPanel").style.display = "flex";
}

// 创建消息旁边的头像
function createAvatarElement(sender, avatarUrl) {
  if (avatarUrl) {
    const img = document.createElement("img");
    img.className = "msg-avatar";
    img.src = getFullAvatarUrl(avatarUrl);
    return img;
  }

  const div = document.createElement("div");
  div.className = "msg-avatar";
  div.innerText = sender ? sender.charAt(0).toUpperCase() : "U";
  return div;
}

// 渲染在线用户列表
function renderOnlineUsers(users) {
  const box = document.getElementById("onlineUsers");
  box.innerHTML = "";

  if (!users || users.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-online";
    empty.innerText = "当前房间暂无在线用户";
    box.appendChild(empty);
    return;
  }

  users.forEach(function (username) {
    const item = document.createElement("div");
    item.className = "online-user-item";

    const avatar = document.createElement("div");
    avatar.className = "online-user-avatar";
    avatar.innerText = username.charAt(0).toUpperCase();

    const name = document.createElement("div");
    name.className = "online-user-name";
    name.innerText = username;

    item.appendChild(avatar);
    item.appendChild(name);

    if (username === AppState.currentUser) {
      const me = document.createElement("div");
      me.className = "online-user-me";
      me.innerText = "我";
      item.appendChild(me);
    }

    box.appendChild(item);
  });
}

// 把一条消息显示到页面上
function addMessage(data) {
  const box = document.getElementById("messages");

  if (data.type === "online_users") {
    renderOnlineUsers(data.users);
    return;
  }
  
  if (data.type === "ack") {
    return;
  }

  if (data.type === "system") {
    const div = document.createElement("div");
    div.className = "message system";
    div.innerText = data.message;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
    return;
  }

  const isMe = data.sender === AppState.currentUser;

  const row = document.createElement("div");
  row.className = "message-row " + (isMe ? "me" : "other");

  const bubble = document.createElement("div");
  bubble.className = "message " + (isMe ? "me" : "other");

  const contentDiv = document.createElement("div");
  contentDiv.innerText = data.content;

  const timeDiv = document.createElement("div");
  timeDiv.className = "time";
  timeDiv.innerText = data.created_at || "";

  if (!isMe) {
    const senderDiv = document.createElement("div");
    senderDiv.className = "sender";
    senderDiv.innerText = data.sender;
    bubble.appendChild(senderDiv);
  }

  bubble.appendChild(contentDiv);
  bubble.appendChild(timeDiv);

  const avatar = createAvatarElement(
    data.sender,
    isMe ? AppState.currentAvatarUrl : data.avatar_url
  );

  if (isMe) {
    row.appendChild(bubble);
    row.appendChild(avatar);
  } else {
    row.appendChild(avatar);
    row.appendChild(bubble);
  }

  box.appendChild(row);
  box.scrollTop = box.scrollHeight;
}

// 年月日时间
function formatDateTime(date) {
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();

  const hour = String(date.getHours()).padStart(2, "0");
  const minute = String(date.getMinutes()).padStart(2, "0");
  const second = String(date.getSeconds()).padStart(2, "0");

  return `${year}/${month}/${day} ${hour}:${minute}:${second}`;
}

// 清空消息
function clearMessages() {
  document.getElementById("messages").innerHTML = "";
}

// 暴露给其他 JS 文件使用
window.setTip = setTip;
window.setOnlineStatus = setOnlineStatus;
window.setRoomStatus = setRoomStatus;
window.showChat = showChat;
window.addMessage = addMessage;
window.formatDateTime = formatDateTime;
window.clearMessages = clearMessages;
window.getFullAvatarUrl = getFullAvatarUrl;
window.setCurrentAvatar = setCurrentAvatar;
window.createAvatarElement = createAvatarElement;
window.renderOnlineUsers = renderOnlineUsers;