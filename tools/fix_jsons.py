import pyjson5
import json
from pathlib import Path

npc_dir = Path("Data/dialogue/Chinese/NPCs")
for file in npc_dir.glob("*.json"):
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = pyjson5.load(f)
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"修复并覆盖: {file}")
    except Exception as e:
        print(f"修复失败: {file}，原因: {e}") 