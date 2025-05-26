"""
Mermaid图表转换器模块
"""
import os
import json
import tempfile
import subprocess
from pathlib import Path
from docx.shared import Inches
from .base import ElementConverter


class MermaidConverter(ElementConverter):
    """Mermaid图表转换器，处理Markdown中的mermaid代码块"""

    def __init__(self, base_converter=None):
        """初始化Mermaid转换器
        
        Args:
            base_converter: 基础转换器实例
        """
        super().__init__(base_converter)
        self.debug = False
        if base_converter:
            self.debug = base_converter.debug

    def convert(self, token):
        """转换mermaid代码块为图片
        
        Args:
            token: mermaid代码块token
            
        Returns:
            docx.paragraph: 包含图片的段落
        """
        if not self.document:
            raise ValueError("Document not set for MermaidConverter")

        if self.debug:
            print(f"处理Mermaid图表: {token}")

        # 获取mermaid代码
        code = token.content if hasattr(token, 'content') else ''
        if not code:
            return None

        try:
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            
            # 创建临时文件保存mermaid代码
            mmd_file = os.path.join(temp_dir, 'diagram.mmd')
            with open(mmd_file, 'w', encoding='utf-8') as f:
                f.write(code)

            # 创建配置文件
            config = {
                "theme": "default",
                "themeVariables": {
                    "fontSize": "16px",
                    "fontFamily": "arial",
                },
                "flowchart": {
                    "htmlLabels": True,
                    "curve": "linear"
                },
                "sequence": {
                    "showSequenceNumbers": False,
                    "actorMargin": 50,
                    "messageMargin": 40
                },
                "gantt": {
                    "leftPadding": 75,
                    "rightPadding": 20
                }
            }
            
            config_file = os.path.join(temp_dir, 'config.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f)

            # 生成图片文件路径
            img_file = os.path.join(temp_dir, 'diagram.png')
            
            # 使用mmdc命令行工具生成图片
            cmd = [
                'mmdc',
                '-i', mmd_file,
                '-o', img_file,
                '-c', config_file,
                '-b', 'transparent'  # 使用透明背景
            ]
            
            if self.debug:
                print(f"执行命令: {' '.join(cmd)}")
                cmd.append('--verbose')  # 添加详细输出
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                if self.debug:
                    print(f"Mermaid转换失败: {result.stderr}")
                    print(f"命令输出: {result.stdout}")
                return None
            print(f"img_file---------: {img_file}")
            # 检查图片是否生成成功
            if not os.path.exists(img_file):
                if self.debug:
                    print(f"图片文件未生成: {img_file}")
                return None

            # 创建新段落
            paragraph = self.document.add_paragraph()
            paragraph.alignment = 1  # 居中对齐

            # 添加图片到段落
            run = paragraph.add_run()
            run.add_picture(img_file, width=Inches(6))  # 设置合适的宽度

            # 清理临时文件
            os.unlink(mmd_file)
            os.unlink(config_file)
            os.unlink(img_file)
            os.rmdir(temp_dir)

            return paragraph

        except Exception as e:
            if self.debug:
                print(f"Mermaid转换异常: {str(e)}")
            return None 