"""
API服务，提供Markdown转Word的Web接口
"""
import os
import tempfile
import time
from pathlib import Path
import uuid
import functools
from flask import Flask, request, send_file, jsonify, make_response
from .converter import BaseConverter

app = Flask(__name__)

# 设置上传文件大小限制（默认为16MB）
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 从环境变量获取API密钥，如果未设置则使用默认值（不建议在生产环境中使用默认值）
API_KEY = os.environ.get('API_KEY', 'md2docx-default-key')

def require_api_key(f):
    """装饰器：要求API密钥验证"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # 从请求头获取API密钥（尝试多种可能的大小写形式）
        key_from_header = (
            request.headers.get('X-API-Key') or 
            request.headers.get('X-Api-Key') or 
            request.headers.get('x-api-key') or
            request.headers.get('X-API-KEY')
        )
        
        # 从URL参数获取API密钥
        key_from_url = request.args.get('api_key')
        
        # 从表单数据获取API密钥
        key_from_form = request.form.get('api_key') if request.form else None
        
        # 从JSON数据获取API密钥
        json_data = request.get_json(silent=True) or {}
        key_from_json = json_data.get('api_key')
        
        # 检查API密钥是否匹配
        provided_key = key_from_header or key_from_url or key_from_form or key_from_json
        
        if app.debug:
            print(f"请求头中的密钥: {key_from_header}")
            print(f"URL参数中的密钥: {key_from_url}")
            print(f"表单中的密钥: {key_from_form}")
            print(f"JSON中的密钥: {key_from_json}")
            print(f"当前API环境变量密钥: {API_KEY}")
        
        if not provided_key:
            response = make_response(jsonify({
                "error": "未提供API密钥",
                "status": "unauthorized"
            }), 401)
            response.headers['WWW-Authenticate'] = 'Bearer'
            return response
        
        if provided_key != API_KEY:
            response = make_response(jsonify({
                "error": "API密钥无效",
                "status": "unauthorized"
            }), 401)
            response.headers['WWW-Authenticate'] = 'Bearer'
            return response
            
        return f(*args, **kwargs)
    return decorated

@app.route('/api/test-auth', methods=['GET'])
@require_api_key
def test_auth():
    """测试API密钥鉴权是否正常工作"""
    return jsonify({
        "status": "ok",
        "message": "API密钥验证成功",
        "api_key_source": "环境变量",
        "api_key_value_masked": f"{API_KEY[:3]}...{API_KEY[-3:]}" if len(API_KEY) > 6 else "***"
    })

@app.route('/api/convert', methods=['POST'])
@require_api_key
def convert_api():
    """接收Markdown文件并转换为DOCX格式
    
    请求格式: multipart/form-data
    参数:
        - file: Markdown文件
        - debug: (可选) 是否启用调试模式，默认为False
        - api_key: (可选) API密钥，也可通过请求头X-API-Key传递
    
    返回:
        - DOCX文件下载
    """
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({"error": "未找到上传的文件"}), 400
    
    file = request.files['file']
    
    # 检查文件是否为空
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400
    
    # 检查文件扩展名
    if not file.filename.lower().endswith(('.md', '.markdown', '.mdown')):
        return jsonify({"error": "仅支持Markdown文件格式"}), 400
    
    # 获取调试参数
    debug = request.form.get('debug', 'false').lower() == 'true'
    
    try:
        # 创建临时文件保存上传的Markdown内容
        with tempfile.NamedTemporaryFile(delete=False, suffix='.md') as temp_input:
            file.save(temp_input.name)
        
        # 创建临时文件用于保存转换后的DOCX
        output_filename = f"{Path(file.filename).stem}_{int(time.time())}.docx"
        temp_output = tempfile.gettempdir() / Path(output_filename)
        
        # 读取上传的Markdown文件内容
        with open(temp_input.name, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 执行转换
        converter = BaseConverter(debug=debug)
        doc = converter.convert(content)
        
        # 保存为DOCX文件
        doc.save(temp_output)
        
        # 删除临时输入文件
        os.unlink(temp_input.name)
        
        # 返回生成的DOCX文件
        return send_file(
            temp_output,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    
    except Exception as e:
        return jsonify({"error": f"转换过程中发生错误: {str(e)}"}), 500

@app.route('/api/convert/text', methods=['POST'])
@require_api_key
def convert_text_api():
    """接收Markdown文本并转换为DOCX格式
    
    请求格式: application/json
    请求体:
        {
            "markdown": "# 标题\n正文内容",
            "debug": false,  // 可选，默认为false
            "api_key": "your-api-key"  // 可选，也可通过请求头X-API-Key传递
        }
    
    返回:
        - DOCX文件下载
    """
    # 获取JSON请求数据
    data = request.get_json()
    
    # 检查是否提供了Markdown文本
    if not data or 'markdown' not in data:
        return jsonify({"error": "未提供Markdown文本"}), 400
    
    markdown_text = data['markdown']
    debug = data.get('debug', False)
    
    try:
        # 生成唯一的文件名
        output_filename = f"document_{uuid.uuid4().hex}.docx"
        temp_output = Path(tempfile.gettempdir()) / output_filename
        
        # 执行转换
        converter = BaseConverter(debug=debug)
        doc = converter.convert(markdown_text)
        
        # 保存为DOCX文件
        doc.save(temp_output)
        
        # 返回生成的DOCX文件
        return send_file(
            temp_output,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    
    except Exception as e:
        return jsonify({"error": f"转换过程中发生错误: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口 - 此接口不需要鉴权"""
    return jsonify({"status": "ok", "service": "md2docx-api"}), 200

def start_server(host='0.0.0.0', port=5000, debug=False):
    """启动API服务器"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_server(debug=True) 