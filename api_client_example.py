#!/usr/bin/env python3
"""
API客户端示例，演示如何使用API进行Markdown转DOCX
"""
import os
import argparse
import requests

def convert_file(api_url, file_path, output_path=None, debug=False, api_key=None):
    """使用API将Markdown文件转换为DOCX
    
    Args:
        api_url: API服务地址，例如 'http://localhost:5000/api/convert'
        file_path: Markdown文件路径
        output_path: 输出文件路径，如果不指定则使用输入文件名+.docx
        debug: 是否启用调试模式
        api_key: API密钥
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 {file_path}")
        return False
    
    # 如果不指定输出路径，则使用原文件名+.docx
    if not output_path:
        file_name = os.path.basename(file_path)
        file_base_name = os.path.splitext(file_name)[0]
        output_path = f"{file_base_name}.docx"
    
    # 准备请求数据
    files = {'file': open(file_path, 'rb')}
    data = {'debug': str(debug).lower()}
    
    # 如果提供了API密钥，添加到表单数据中
    if api_key:
        data['api_key'] = api_key
    
    # 准备请求头
    headers = {}
    if api_key:
        headers['X-API-Key'] = api_key
    
    print(f"正在上传 {file_path} 到 {api_url}...")
    
    try:
        # 发送请求
        response = requests.post(api_url, files=files, data=data, headers=headers)
        
        # 检查响应状态
        if response.status_code == 200:
            # 保存返回的文件
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"转换成功，已保存到 {output_path}")
            return True
        else:
            # 处理错误
            try:
                error_info = response.json()
                print(f"转换失败: {error_info.get('error', '未知错误')}")
            except:
                print(f"转换失败: HTTP状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"请求出错: {str(e)}")
        return False
    finally:
        # 关闭文件
        files['file'].close()

def convert_text(api_url, markdown_text, output_path, debug=False, api_key=None):
    """使用API将Markdown文本转换为DOCX
    
    Args:
        api_url: API服务地址，例如 'http://localhost:5000/api/convert/text'
        markdown_text: Markdown文本内容
        output_path: 输出文件路径
        debug: 是否启用调试模式
        api_key: API密钥
    """
    # 准备请求数据
    data = {
        'markdown': markdown_text,
        'debug': debug
    }
    
    # 如果提供了API密钥，添加到JSON数据中
    if api_key:
        data['api_key'] = api_key
    
    # 准备请求头
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['X-API-Key'] = api_key
    
    print(f"正在发送Markdown文本到 {api_url}...")
    
    try:
        # 发送请求
        response = requests.post(api_url, json=data, headers=headers)
        
        # 检查响应状态
        if response.status_code == 200:
            # 保存返回的文件
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"转换成功，已保存到 {output_path}")
            return True
        else:
            # 处理错误
            try:
                error_info = response.json()
                print(f"转换失败: {error_info.get('error', '未知错误')}")
            except:
                print(f"转换失败: HTTP状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"请求出错: {str(e)}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='使用API将Markdown转换为DOCX')
    parser.add_argument('--server', default='http://localhost:5000', help='API服务地址')
    parser.add_argument('--file', help='要转换的Markdown文件路径')
    parser.add_argument('--text', help='要转换的Markdown文本，与--file互斥')
    parser.add_argument('--output', help='输出的DOCX文件路径')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--api-key', help='API密钥')
    
    args = parser.parse_args()
    
    # 尝试从环境变量获取API密钥（如果命令行未提供）
    api_key = args.api_key or os.environ.get('MD2DOCX_API_KEY')
    
    # 检查参数
    if args.file and args.text:
        print("错误: --file 和 --text 不能同时使用")
        return
    
    if not args.file and not args.text:
        print("错误: 必须指定 --file 或 --text")
        return
    
    if args.file:
        # 文件转换
        api_url = f"{args.server}/api/convert"
        convert_file(api_url, args.file, args.output, args.debug, api_key)
    else:
        # 文本转换
        if not args.output:
            print("错误: 使用--text时必须指定--output")
            return
        
        api_url = f"{args.server}/api/convert/text"
        convert_text(api_url, args.text, args.output, args.debug, api_key)

if __name__ == '__main__':
    main() 