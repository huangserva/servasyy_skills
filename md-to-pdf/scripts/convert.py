#!/usr/bin/env python3
"""
Markdown to PDF converter
可选调用 illustration-generator
"""
import sys
import subprocess
from pathlib import Path

def convert_md_to_pdf(markdown_file, output_pdf=None, with_illustrations=False, workers=4):
    """转换 MD 到 PDF"""
    markdown_path = Path(markdown_file)
    
    if not markdown_path.exists():
        print(f"❌ 文件不存在: {markdown_file}")
        return False
    
    # 如果需要配图
    if with_illustrations:
        print("🎨 正在生成配图...")
        illustration_script = Path.home() / '.claude' / 'skills' / 'illustration-generator' / 'scripts' / 'generate.py'
        
        if illustration_script.exists():
            result = subprocess.run([
                sys.executable,
                str(illustration_script),
                str(markdown_path),
                '--workers', str(workers)
            ])
            
            if result.returncode != 0:
                print("⚠️  配图生成失败，继续转换 PDF")
        else:
            print("⚠️  illustration-generator 未安装，跳过配图")
    
    # 调用 servasyy 的 PDF 生成脚本
    print("\n📄 正在生成 PDF...")
    pdf_script = Path.home() / '.claude' / 'skills' / 'servasyy-document-interpreter' / 'scripts' / 'generate_pdf.py'
    
    if not pdf_script.exists():
        print(f"❌ PDF 生成脚本不存在: {pdf_script}")
        return False
    
    cmd = [sys.executable, str(pdf_script), str(markdown_path)]
    if output_pdf:
        cmd.extend([str(output_pdf)])
    
    result = subprocess.run(cmd)
    
    return result.returncode == 0


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Markdown to PDF converter')
    parser.add_argument('markdown', help='Markdown 文件路径')
    parser.add_argument('-o', '--output', help='输出 PDF 路径')
    parser.add_argument('--with-illustrations', action='store_true', help='自动生成配图')
    parser.add_argument('--workers', type=int, default=4, help='配图并行线程数')
    
    args = parser.parse_args()
    
    success = convert_md_to_pdf(
        args.markdown,
        args.output,
        args.with_illustrations,
        args.workers
    )
    
    sys.exit(0 if success else 1)
