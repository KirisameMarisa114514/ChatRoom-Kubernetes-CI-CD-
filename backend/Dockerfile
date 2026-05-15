# 使用轻量 Python 镜像
FROM python:3.12-slim

# 设置容器内工作目录
WORKDIR /app

# 避免生成 pyc 缓存
ENV PYTHONDONTWRITEBYTECODE=1

# 让 Python 日志实时输出
ENV PYTHONUNBUFFERED=1

# 先复制依赖文件，方便 Docker 缓存
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY app ./app

# 创建 SQLite 数据目录和头像上传目录
RUN mkdir -p data uploads/avatars

# 暴露 FastAPI 端口
EXPOSE 8000

# 启动后端服务
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]