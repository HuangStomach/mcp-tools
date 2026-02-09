FROM python:3.12.12-alpine3.23

WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["fastmcp", "run", "index.py:mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]