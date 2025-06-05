from PIL import Image
import os
from pathlib import Path

def fill_transparent_background(input_path, output_path, fill_color=(219, 174, 116)):
    # 打开图片
    img = Image.open(input_path)
    
    # 如果图片没有alpha通道，转换为RGBA
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 放大图片到512x512
    img = img.resize((512, 512), Image.Resampling.LANCZOS)
    
    # 创建新图片，使用指定颜色作为背景
    background = Image.new('RGBA', img.size, fill_color)
    
    # 将原图与背景合并
    # 使用alpha通道作为mask
    background.paste(img, (0, 0), img)
    
    # 确保输出目录存在
    output_path.parent.mkdir(exist_ok=True)
    
    # 保存结果
    background.save(output_path, 'PNG')
    print(f"已处理: {input_path.name}")

def process_all_images():
    input_dir = Path('input')
    output_dir = Path('input3')
    
    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)
    
    # 处理所有PNG文件
    for img_file in input_dir.glob('*.png'):
        output_path = output_dir / img_file.name
        fill_transparent_background(img_file, output_path)

if __name__ == "__main__":
    process_all_images() 