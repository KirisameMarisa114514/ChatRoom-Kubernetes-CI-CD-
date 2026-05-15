// 注册用户
async function register() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!username || !password) {
    setTip("用户名和密码不能为空", "error");
    return;
  }

  const res = await fetch(API_BASE + "/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      username: username,
      password: password
    })
  });

  const data = await res.json();

  if (res.ok) {
    setTip("注册成功，现在可以登录", "success");
  } else {
    setTip(data.detail || "注册失败", "error");
  }
}

// 登录用户
async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!username || !password) {
    setTip("用户名和密码不能为空", "error");
    return;
  }

  const res = await fetch(API_BASE + "/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      username: username,
      password: password
    })
  });

  const data = await res.json();

  if (res.ok) {
    showChat(data.username, data.avatar_url || "");
  } else {
    setTip(data.detail || "登录失败", "error");
  }
}

// 加载历史消息
async function loadHistory(room) {
  const res = await fetch(API_BASE + "/history/" + encodeURIComponent(room));

  if (!res.ok) {
    addMessage({
      type: "system",
      message: "历史消息加载失败"
    });
    return;
  }

  const data = await res.json();

  if (data.messages.length === 0) {
    addMessage({
      type: "system",
      message: "暂无历史消息"
    });
    return;
  }

  data.messages.forEach(function (msg) {
    addMessage({
      type: "message",
      sender: msg.sender,
      content: msg.content,
      created_at: msg.created_at,
      avatar_url: msg.avatar_url || ""
    });
  });
}

// 清除当前房间历史消息
async function clearHistory() {
  if (!AppState.currentRoom) {
    alert("请先进入房间");
    return;
  }

  const ok = confirm(`确定要清除 ${AppState.currentRoom} 的历史记录吗？`);

  if (!ok) {
    return;
  }

  const res = await fetch(
    API_BASE + "/history/" + encodeURIComponent(AppState.currentRoom),
    {
      method: "DELETE"
    }
  );

  const data = await res.json();

  if (res.ok) {
    clearMessages();

    addMessage({
      type: "system",
      message: `已清除 ${AppState.currentRoom} 的历史记录，共删除 ${data.deleted} 条`
    });
  } else {
    addMessage({
      type: "system",
      message: "清除历史记录失败"
    });
  }
}

// 上传头像
async function uploadAvatar() {
  const fileInput = document.getElementById("avatarFile");
  const file = fileInput.files[0];

  if (!AppState.currentUser) {
    alert("请先登录");
    return;
  }

  if (!file) {
    return;
  }

  const formData = new FormData();
  formData.append("username", AppState.currentUser);
  formData.append("file", file);

  const res = await fetch(API_BASE + "/avatar", {
    method: "POST",
    body: formData
  });

  const data = await res.json();

  if (res.ok) {
    setCurrentAvatar(data.avatar_url);

    addMessage({
      type: "system",
      message: "头像上传成功"
    });
  } else {
    alert(data.detail || "头像上传失败");
  }

  fileInput.value = "";
}

// 暴露给 HTML onclick 和其他 JS 文件使用
window.register = register;
window.login = login;
window.loadHistory = loadHistory;
window.clearHistory = clearHistory;
window.uploadAvatar = uploadAvatar;