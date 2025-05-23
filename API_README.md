# Markdown转DOCX API服务

这是一个基于Flask的Web API服务，用于将Markdown文件转换为DOCX(Word)文件。

## 安装

1. 确保已安装Python 3.7+
2. 安装依赖项

```bash
pip install -r requirements.txt
```

## 启动API服务

```bash
python run_api.py --api-key your-secret-key
```

默认情况下，服务将在 `http://0.0.0.0:5000` 上运行。

### 命令行选项

```bash
python run_api.py --host 127.0.0.1 --port 8080 --debug
```

- `--host`: 指定监听的主机地址，默认为 `0.0.0.0`
- `--port`: 指定监听的端口，默认为 `5000`
- `--debug`: 启用调试模式

### 环境变量设置

可以通过环境变量配置服务：

```bash
# 设置API密钥
export API_KEY=your-secure-api-key

# 启动服务
python run_api.py
```

## API鉴权

除了健康检查接口外，所有API接口都需要提供有效的API密钥进行鉴权。API密钥可以通过以下方式提供：

1. 请求头：`X-API-Key: your-api-key`
2. URL参数：`?api_key=your-api-key`
3. 表单数据：对于文件上传，可以包含`api_key`字段
4. JSON数据：对于文本转换，可以在JSON中包含`api_key`字段

**重要安全提示：**
- 默认的API密钥为`md2docx-default-key`，强烈建议在生产环境中修改
- 使用随机生成的复杂字符串作为API密钥
- 避免在代码库或公共场所共享API密钥

## API接口说明

### 1. 文件转换接口

**接口**: `/api/convert`
**方法**: POST
**请求格式**: multipart/form-data

**参数**:
- `file`: Markdown文件 (必填)
- `debug`: 是否启用调试模式，默认为false (可选)
- `api_key`: API密钥 (可选，也可通过请求头提供)

**响应**:
- 成功: 返回DOCX文件下载
- 失败: 返回错误信息的JSON
- 未授权: 返回401状态码和错误信息

**示例**:
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -F "file=@/path/to/your/file.md" \
  -F "debug=false" \
  http://localhost:5000/api/convert -o output.docx
```

### 2. 文本转换接口

**接口**: `/api/convert/text`
**方法**: POST
**请求格式**: application/json

**请求体**:
```json
{
    "markdown": "# 标题\n正文内容",
    "debug": false,  // 可选，默认为false
    "api_key": "your-api-key"  // 可选，也可通过请求头提供
}
```

**响应**:
- 成功: 返回DOCX文件下载
- 失败: 返回错误信息的JSON
- 未授权: 返回401状态码和错误信息

**示例**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{"markdown": "# 标题\n正文内容"}' \
  http://localhost:5000/api/convert/text -o output.docx
```

### 3. 健康检查接口

**接口**: `/api/health`
**方法**: GET
**注意**: 此接口不需要API密钥鉴权

**响应**:
```json
{
    "status": "ok",
    "service": "md2docx-api"
}
```

**示例**:
```bash
curl http://localhost:5000/api/health
```

## 使用客户端示例

我们提供了一个Python客户端示例，演示如何使用API。

### 文件转换示例

```bash
# 通过命令行参数提供API密钥
python api_client_example.py --file /path/to/your/file.md --output output.docx --api-key your-api-key

# 或通过环境变量提供API密钥
export MD2DOCX_API_KEY=your-api-key
python api_client_example.py --file /path/to/your/file.md --output output.docx
```

### 文本转换示例

```bash
python api_client_example.py --text "# 标题\n正文内容" --output output.docx --api-key your-api-key
```

### 客户端选项

- `--server`: API服务地址，默认为`http://localhost:5000`
- `--file`: 要转换的Markdown文件路径
- `--text`: 要转换的Markdown文本内容（与`--file`互斥）
- `--output`: 输出的DOCX文件路径
- `--debug`: 启用调试模式
- `--api-key`: API密钥，也可通过环境变量`MD2DOCX_API_KEY`提供

## 错误处理

API在遇到错误时会返回相应的HTTP状态码和JSON格式的错误信息：

```json
{
    "error": "错误描述"
}
```

常见错误状态码：
- 400: 请求参数错误
- 401: 未授权（API密钥无效或未提供）
- 500: 服务器内部错误

## 部署建议

对于生产环境，建议使用Gunicorn或uWSGI作为WSGI服务器来运行Flask应用，并配合Nginx作为反向代理。

### 使用Gunicorn运行

安装Gunicorn:
```bash
pip install gunicorn
```

启动服务:
```bash
# 设置API密钥环境变量
export API_KEY=your-secure-api-key

# 启动Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'src.api:app'
```

其中`-w 4`表示使用4个工作进程。 