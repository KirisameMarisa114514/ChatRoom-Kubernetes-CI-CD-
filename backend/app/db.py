import sqlite3  # 数据库模块
import hashlib
import secrets
from datetime import datetime  # 用来生成消息时间
from pathlib import Path  # 处理数据库文件路径


# 数据库文件路径：
# 当前文件是 app/db.py
# parent.parent 表示回到 backend 目录
# 最终数据库会放在 backend/data/messages.db
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "messages.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: str) -> str:
    raw = (password + salt).encode()
    return hashlib.sha256(raw).hexdigest()


def init_db():
    """
    初始化数据库。

    如果 data 目录不存在，就创建。
    如果 messages / users 表不存在，就创建。
    如果旧 users 表没有 avatar_url 字段，就自动补上。
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id TEXT NOT NULL,
        sender TEXT NOT NULL,
        content TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        avatar_url TEXT DEFAULT '',
        created_at TEXT NOT NULL
    )
    """)

    # 兼容旧数据库：
    # 如果 users 表以前已经存在，但没有 avatar_url 字段，就补一个。
    try:
        cur.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


# 注册用户
def create_user(username: str, password: str) -> bool:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO users (username, password_hash, salt, avatar_url, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, password_hash, salt, "", created_at)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


# 登录验证
def verify_user(username: str, password: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT username, password_hash, salt
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cur.fetchone()
    conn.close()

    if user is None:
        return False

    input_hash = hash_password(password, user["salt"])
    return input_hash == user["password_hash"]


# 获取用户信息
def get_user(username: str) -> dict | None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, username, avatar_url, created_at
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return dict(row)


# 获取用户头像 URL
def get_user_avatar_url(username: str) -> str:
    user = get_user(username)

    if user is None:
        return ""

    return user.get("avatar_url") or ""


# 更新用户头像 URL
def update_user_avatar_url(username: str, avatar_url: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET avatar_url = ?
        WHERE username = ?
        """,
        (avatar_url, username)
    )

    updated = cur.rowcount

    conn.commit()
    conn.close()

    return updated > 0


def save_message(room_id: str, sender: str, content: str) -> dict:
    """
    保存一条聊天消息。

    参数：
    room_id: 房间 ID
    sender: 发送者
    content: 消息内容

    返回：
    保存后的消息信息，包括 message_id。
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "sent"

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO messages (room_id, sender, content, status, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (room_id, sender, content, status, created_at)
    )

    message_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {
        "id": message_id,
        "room_id": room_id,
        "sender": sender,
        "content": content,
        "status": status,
        "created_at": created_at
    }


def get_history(room_id: str, limit: int = 50) -> list[dict]:
    """
    查询某个房间的历史消息。

    参数：
    room_id: 房间 ID
    limit: 最多查询多少条，默认 50 条

    返回：
    消息列表。每条消息会带上发送者头像 URL。
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            messages.id,
            messages.room_id,
            messages.sender,
            messages.content,
            messages.status,
            messages.created_at,
            users.avatar_url
        FROM messages
        LEFT JOIN users ON messages.sender = users.username
        WHERE messages.room_id = ?
        ORDER BY messages.id DESC
        LIMIT ?
        """,
        (room_id, limit)
    )

    rows = cur.fetchall()
    conn.close()

    # 查询时是倒序取最新 50 条，这里 reversed 让返回结果按正常时间顺序显示
    return [dict(row) for row in reversed(rows)]


# 清除某个房间的历史消息
def clear_history(room_id: str) -> int:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM messages
        WHERE room_id = ?
        """,
        (room_id,)
    )

    deleted_count = cur.rowcount

    conn.commit()
    conn.close()

    return deleted_count