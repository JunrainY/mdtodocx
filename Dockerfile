FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装curl用于健康检查
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 复制应用程序代码
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=5000
ENV DEBUG=false
# 设置默认API密钥，建议在运行容器时覆盖此值
ENV API_KEY=md2docx-default-key

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# 启动命令
CMD ["python", "run_api.py", "--host", "0.0.0.0", "--port", "5000"] 