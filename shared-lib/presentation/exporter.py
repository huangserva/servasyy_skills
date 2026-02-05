"""
PDF/PPTX 导出器
支持将生成的幻灯片导出为 PDF 或 PPTX 格式
"""

from pathlib import Path
from typing import Optional, List, Dict
import glob


class Exporter:
    """PPT 导出器：支持 PPTX 和 PDF"""
    
    @staticmethod
    def export_to_pptx(
        slides_dir: Path,
        output_path: Optional[Path] = None,
        metadata: Optional[Dict] = None
    ) -> Path:
        """
        导出为 PPTX（使用现有的 assemble_pptx.py 脚本）
        
        Args:
            slides_dir: 幻灯片图片目录
            output_path: 输出文件路径（可选）
            metadata: 元数据（可选）
        
        Returns:
            生成的 PPTX 文件路径
        """
        import subprocess
        import sys
        
        # 获取 assemble_pptx.py 脚本路径
        script_path = Path.home() / '.claude/skills/ppt-generator/scripts/assemble_pptx.py'
        
        if not script_path.exists():
            raise FileNotFoundError(f"assemble_pptx.py 脚本不存在: {script_path}")
        
        # 确定输出路径
        if output_path is None:
            output_path = slides_dir / 'presentation.pptx'
        
        # 构建命令
        cmd = [
            sys.executable,
            str(script_path),
            '--input_dir', str(slides_dir),
            '--output', str(output_path)
        ]
        
        # 执行脚本
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"PPTX 导出失败: {result.stderr}")
        
        print(f"✅ PPTX 已导出: {output_path}")
        return output_path
    
    @staticmethod
    def export_to_pdf(
        slides_dir: Path,
        output_path: Optional[Path] = None,
        metadata: Optional[Dict] = None
    ) -> Path:
        """
        导出为 PDF（使用 img2pdf 或 PIL）
        
        Args:
            slides_dir: 幻灯片图片目录
            output_path: 输出文件路径（可选）
            metadata: 元数据（可选）
        
        Returns:
            生成的 PDF 文件路径
        """
        # 确定输出路径
        if output_path is None:
            output_path = slides_dir / 'presentation.pdf'
        
        # 获取所有幻灯片图片（按编号排序）
        image_files = sorted(
            slides_dir.glob('slide_*.png'),
            key=lambda p: int(p.stem.split('_')[1])
        )
        
        if not image_files:
            raise FileNotFoundError(f"未找到幻灯片图片: {slides_dir}/slide_*.png")
        
        print(f"📄 准备导出 {len(image_files)} 张幻灯片为 PDF...")
        
        # 方法 1：尝试使用 img2pdf（最快）
        try:
            import img2pdf
            
            with open(output_path, 'wb') as f:
                f.write(img2pdf.convert([str(img) for img in image_files]))
            
            print(f"✅ PDF 已导出（img2pdf）: {output_path}")
            return output_path
        
        except ImportError:
            print("⚠️  img2pdf 未安装，尝试使用 PIL + reportlab...")
        
        # 方法 2：使用 PIL + reportlab
        try:
            from PIL import Image
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.utils import ImageReader
            import io
            
            # 读取第一张图片获取尺寸
            first_img = Image.open(image_files[0])
            img_width, img_height = first_img.size
            
            # PDF 页面大小（使用图片比例）
            page_width = 792  # 11 inches * 72 dpi
            page_height = int(page_width * img_height / img_width)
            
            # 创建 PDF
            c = canvas.Canvas(str(output_path), pagesize=(page_width, page_height))
            
            for img_path in image_files:
                # 读取图片
                img = Image.open(img_path)
                
                # 转换为 RGB（如果是 RGBA）
                if img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])
                    img = rgb_img
                
                # 保存到内存
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # 添加到 PDF
                img_reader = ImageReader(img_buffer)
                c.drawImage(img_reader, 0, 0, width=page_width, height=page_height)
                c.showPage()
            
            c.save()
            print(f"✅ PDF 已导出（PIL+reportlab）: {output_path}")
            return output_path
        
        except ImportError as e:
            raise ImportError(
                "PDF 导出需要安装以下库之一：\n"
                "  方法1（推荐）: pip install img2pdf\n"
                "  方法2: pip install Pillow reportlab"
            ) from e
    
    @staticmethod
    def export_both(
        slides_dir: Path,
        pptx_output: Optional[Path] = None,
        pdf_output: Optional[Path] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Path]:
        """
        同时导出 PPTX 和 PDF
        
        Returns:
            {'pptx': Path, 'pdf': Path}
        """
        results = {}
        
        # 导出 PPTX
        try:
            results['pptx'] = Exporter.export_to_pptx(slides_dir, pptx_output, metadata)
        except Exception as e:
            print(f"⚠️  PPTX 导出失败: {e}")
        
        # 导出 PDF
        try:
            results['pdf'] = Exporter.export_to_pdf(slides_dir, pdf_output, metadata)
        except Exception as e:
            print(f"⚠️  PDF 导出失败: {e}")
        
        return results


# 便捷函数

def export_to_pptx(slides_dir: Path, output: Optional[Path] = None) -> Path:
    """导出为 PPTX"""
    return Exporter.export_to_pptx(slides_dir, output)


def export_to_pdf(slides_dir: Path, output: Optional[Path] = None) -> Path:
    """导出为 PDF"""
    return Exporter.export_to_pdf(slides_dir, output)


def export_both(slides_dir: Path) -> Dict[str, Path]:
    """同时导出 PPTX 和 PDF"""
    return Exporter.export_both(slides_dir)


if __name__ == '__main__':
    # 测试（需要有实际的幻灯片图片）
    print("=" * 60)
    print("Exporter 模块已加载")
    print("=" * 60)
    print("\n使用示例:")
    print("  from presentation.exporter import export_to_pdf, export_to_pptx")
    print("  export_to_pptx(Path('/path/to/slides'))")
    print("  export_to_pdf(Path('/path/to/slides'))")
