// 页面事件绑定入口
document.addEventListener("DOMContentLoaded", function () {
  const contentInput = document.getElementById("content");

  // 回车发送消息
  contentInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });
});