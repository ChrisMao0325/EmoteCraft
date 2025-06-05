import json
import os
from pathlib import Path

def is_character_name(name):
    """判断是否为角色名称"""
    # 排除日期相关的键
    date_related = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'spring', 'summer', 'fall', 'winter']
    return not any(prefix in name for prefix in date_related)

def extract_names_from_json(file_path):
    """从JSON文件中提取人物姓名"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        names = set()
        
        # 处理不同的JSON结构
        if isinstance(data, dict):
            if "Changes" in data:
                # 处理包含Changes的JSON
                for change in data["Changes"]:
                    if "Entries" in change:
                        names.update(change["Entries"].keys())
            elif "Entries" in data:
                # 处理直接包含Entries的JSON
                names.update(data["Entries"].keys())
        
        # 过滤掉非角色名称
        return {name for name in names if is_character_name(name)}
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        return set()

def main():
    # 设置基础目录
    base_dir = Path("Data/dialogue/Chinese")
    
    # 存储所有找到的名字
    all_names = set()
    
    # 递归遍历所有JSON文件
    for json_file in base_dir.rglob("*.json"):
        names = extract_names_from_json(json_file)
        all_names.update(names)
    
    # 将名字转换为列表并排序
    names_list = sorted(list(all_names))
    
    # 创建输出目录（如果不存在）
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 保存结果到JSON文件
    output_file = output_dir / "character_names.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"characters": names_list}, f, ensure_ascii=False, indent=2)
    
    print(f"已找到 {len(names_list)} 个独特的角色名称")
    print(f"结果已保存到: {output_file}")

if __name__ == "__main__":
    main() 