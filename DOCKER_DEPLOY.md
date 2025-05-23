# Docker部署指南

本文档介绍如何使用Docker容器部署Markdown转DOCX的API服务。

## 前提条件

- 安装Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
- 安装Docker Compose (可选): [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

## 方法一：使用Dockerfile构建镜像

1. 构建Docker镜像

```bash
docker build -t md2docx-api:latest .
```

2. 运行容器

```bash
docker run -d -p 5000:5000 -e API_KEY=your-secret-api-key --name md2docx-api md2docx-api:latest
```

3. 查看容器状态

```bash
docker ps
```

4. 查看容器日志

```bash
docker logs md2docx-api
```

## 方法二：使用Docker Compose部署

1. 启动服务前，编辑docker-compose.yml文件，设置安全的API密钥：

```yaml
environment:
  - DEBUG=false
  - API_KEY=your-secure-api-key  # 修改为安全的随机字符串
```

2. 启动服务

```bash
docker-compose up -d
```

3. 查看服务状态

```bash
docker-compose ps
```

4. 查看服务日志

```bash
docker-compose logs
```

5. 停止服务

```bash
docker-compose down
```

## API密钥鉴权

此版本已添加API密钥鉴权功能，保护API不被未授权访问。所有API请求（健康检查接口除外）都需要提供有效的API密钥。

### API密钥传递方式

API密钥可以通过以下方式之一提供：

1. 请求头：`X-API-Key: your-api-key`
2. URL参数：`?api_key=your-api-key`
3. 表单数据：对于文件上传，可以包含`api_key`字段
4. JSON数据：对于文本转换，可以在JSON中包含`api_key`字段

### 设置API密钥

在Docker环境中，通过环境变量设置API密钥：

```bash
# 使用Docker运行
docker run -d -p 5000:5000 -e API_KEY=your-secret-api-key --name md2docx-api md2docx-api:latest

# 或在docker-compose.yml中设置
environment:
  - API_KEY=your-secret-api-key
```

**重要安全提示：**
- 默认的API密钥为`md2docx-default-key`，强烈建议在生产环境中更改为强密钥
- 建议使用随机生成的复杂字符串作为API密钥
- 不要在代码库或公共场所共享您的API密钥

## 测试API服务

服务启动后，可以使用以下命令测试健康检查接口：

```bash
curl http://localhost:5000/api/health
```

期望的响应：

```json
{"status":"ok","service":"md2docx-api"}
```

## 使用示例

转换Markdown文件（包含API密钥）：

```bash
curl -X POST -H "X-API-Key: your-api-key" -F "file=@/path/to/your/file.md" -F "debug=false" http://localhost:5000/api/convert -o output.docx
```

转换Markdown文本（包含API密钥）：

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"markdown": "# 标题\n正文内容"}' \
  http://localhost:5000/api/convert/text -o output.docx
```

## 使用客户端示例

使用Python客户端并提供API密钥：

```bash
# 通过命令行参数提供API密钥
python api_client_example.py --file /path/to/your/file.md --api-key your-api-key

# 或通过环境变量提供API密钥
export MD2DOCX_API_KEY=your-api-key
python api_client_example.py --file /path/to/your/file.md
```

## 环境变量

您可以通过环境变量配置容器：

- `HOST`: API服务监听的主机地址，默认为`0.0.0.0`
- `PORT`: API服务监听的端口，默认为`5000`
- `DEBUG`: 是否启用调试模式，默认为`false`
- `API_KEY`: API鉴权密钥，默认为`md2docx-default-key`（生产环境请修改）

示例：

```bash
docker run -d -p 8080:8080 \
  -e PORT=8080 \
  -e DEBUG=true \
  -e API_KEY=your-secure-api-key \
  --name md2docx-api md2docx-api:latest
```

## 使用自定义卷

持久化日志文件：

```bash
docker run -d -p 5000:5000 -v $(pwd)/logs:/app/logs --name md2docx-api md2docx-api:latest
```

## 生产环境部署建议

对于生产环境，建议：

1. 使用反向代理（如Nginx）转发流量到容器
2. 配置HTTPS
3. 设置适当的资源限制
4. 配置容器自动重启策略
5. 设置强密码的API密钥
6. 监控容器状态和日志

示例docker-compose配置（生产环境）：

```yaml
version: '3'

services:
  md2docx-api:
    build: .
    container_name: md2docx-api
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - DEBUG=false
      - API_KEY=your-secure-random-api-key  # 使用安全的随机字符串
    volumes:
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    networks:
      - md2docx-network

networks:
  md2docx-network:
    driver: bridge
``` 