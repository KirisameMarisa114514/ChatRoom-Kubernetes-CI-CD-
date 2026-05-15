from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException


# 当前文件：backend/app/upload.py
# parent.parent 回到 backend 目录
BACKEND_DIR = Path(__file__).resolve().parent.parent

# 头像保存目录：backend/uploads/avatars/
AVATAR_DIR = BACKEND_DIR / "uploads" / "avatars"

# 允许上传的图片后缀
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# 最大头像大小：2MB
MAX_AVATAR_SIZE = 2 * 1024 * 1024


def safe_username(username: str) -> str:
    """
    简单处理用户名，避免文件名里出现奇怪字符。
    只保留字母、数字、下划线和短横线。
    """
    result = []

    for ch in username:
        if ch.isalnum() or ch in ["_", "-"]:
            result.append(ch)

    if not result:
        return "user"

    return "".join(result)


async def save_avatar_file(username: str, file: UploadFile) -> str:
    """
    保存用户上传的头像文件。

    参数：
    username: 当前用户名
    file: FastAPI 接收到的上传文件

    返回：
    avatar_url，例如：
    /static/avatars/alice_xxxxx.png
    """

    AVATAR_DIR.mkdir(parents=True, exist_ok=True)

    original_name = file.filename or ""
    suffix = Path(original_name).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="only jpg, jpeg, png, webp are allowed"
        )

    content = await file.read()

    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=400,
            detail="avatar file is too large"
        )

    name = safe_username(username)
    filename = f"{name}_{uuid4().hex}{suffix}"

    save_path = AVATAR_DIR / filename

    with open(save_path, "wb") as f:
        f.write(content)

    avatar_url = f"/static/avatars/{filename}"

    return avatar_url