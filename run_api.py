#!/usr/bin/env python3
"""
启动Markdown转DOCX的API服务
"""
import os
import argparse
from src.api import start_server

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='启动Markdown转DOCX的API服务')
    parser.add_argument('--host', default=os.environ.get('HOST', '0.0.0.0'), 
                        help='监听的主机地址，默认为0.0.0.0')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5000)), 
                        help='监听的端口，默认为5000')
    parser.add_argument('--debug', action='store_true', 
                        help='启用调试模式')
    parser.add_argument('--api-key', 
                        help='API密钥，用于鉴权，也可通过环境变量API_KEY设置')
    
    args = parser.parse_args()
    
    # 如果环境变量中设置了DEBUG=true，则覆盖命令行参数
    if os.environ.get('DEBUG', '').lower() == 'true':
        args.debug = True
    
    # 如果在命令行中提供了API密钥，则覆盖环境变量
    if args.api_key:
        os.environ['API_KEY'] = args.api_key
    
    print(f"启动API服务在 http://{args.host}:{args.port}")
    print(f"调试模式: {'启用' if args.debug else '禁用'}")
    print("按 Ctrl+C 停止服务")
    start_server(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main() 