FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 使用阿里云镜像源加速（Debian 12 Bookworm）
RUN cat /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|security.debian.org|mirrors.aliyun.com/debian-security|g' /etc/apt/sources.list.d/debian.sources && \
    echo "--- After modification ---" && \
    cat /etc/apt/sources.list.d/debian.sources

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
      pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 复制启动脚本
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# 暴露端口
EXPOSE 8000

# 使用启动脚本
ENTRYPOINT ["./entrypoint.sh"]
