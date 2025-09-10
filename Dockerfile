# 基础镜像
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 仅复制依赖文件用于缓存层
COPY requirements.txt .

# Python 依赖
RUN pip install -r requirements.txt

# 复制其余代码
COPY ./app /app/

COPY .env /app/.env

RUN chmod -R 777 /app

# 默认启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]