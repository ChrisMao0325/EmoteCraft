from flask import Flask, render_template, request, send_from_directory, jsonify
import json
from pathlib import Path
import threading
import time
from llm import get_emote_prompts
from main import generate_emote

app = Flask(__name__)

# 递归收集所有对话组
all_dialogue_groups = []
base_dir = Path('Data/dialogue/Chinese')
print(f"开始加载对话组，基础目录: {base_dir}")
for json_file in base_dir.rglob('*.json'):
    rel_path = json_file.relative_to(base_dir)
    print(f"正在处理文件: {json_file}")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 1. 有Changes字段（如节日文件）
        if isinstance(data, dict) and 'Changes' in data:
            for change in data['Changes']:
                logname = change.get('LogName') or str(rel_path)
                entries = change.get('Entries', {})
                if entries:
                    # 使用更简单的group_id格式
                    group_id = str(rel_path).replace('\\', '/')
                    print(f"添加对话组: {group_id}")
                    all_dialogue_groups.append({
                        'group_id': group_id,
                        'display': f'{logname} ({rel_path})',
                        'entries': entries
                    })
        # 2. 直接有Entries字段（如NPC文件）
        elif isinstance(data, dict) and 'Entries' in data:
            logname = str(rel_path)
            entries = data['Entries']
            if entries:
                # 使用更简单的group_id格式
                group_id = str(rel_path).replace('\\', '/')
                print(f"添加对话组: {group_id}")
                all_dialogue_groups.append({
                    'group_id': group_id,
                    'display': f'{logname} ({rel_path})',
                    'entries': entries
                })
    except Exception as e:
        print(f'解析{json_file}失败: {e}')

print(f"总共加载了 {len(all_dialogue_groups)} 个对话组")

def get_emote_image_path(group_id, page, denoise, unique_id=None):
    safe_id = str(group_id).replace('/', '_').replace('\\', '_')
    if unique_id:
        return f'static/emotes/{safe_id}_{page}_{denoise}_{unique_id}.png'
    else:
        return f'static/emotes/{safe_id}_{page}_{denoise}.png'

def get_emote_image_url(group_id, page, denoise, unique_id=None):
    safe_id = str(group_id).replace('/', '_').replace('\\', '_')
    if unique_id:
        return f'/static/emotes/{safe_id}_{page}_{denoise}_{unique_id}.png'
    else:
        return f'/static/emotes/{safe_id}_{page}_{denoise}.png'

@app.route('/')
def index():
    groups = [{'display': g['display'], 'group_id': g['group_id']} for g in all_dialogue_groups]
    return render_template('index.html', groups=groups)

@app.route('/dialogue')
def dialogue():
    group_id = request.args.get('logname')
    print(f"查找对话组: {group_id}")
    page = int(request.args.get('page', 0))
    denoise = float(request.args.get('denoise', 0.35))
    group = next((g for g in all_dialogue_groups if g['group_id'] == group_id), None)
    if not group:
        print(f"未找到对话组: {group_id}")
        print(f"可用的对话组: {[g['group_id'] for g in all_dialogue_groups]}")
        return '未找到该对话组', 404
    entries = list(group['entries'].items())
    if not entries:
        print("该对话组无对话")
        return '该对话组无对话', 404
    total = len(entries)
    page = max(0, min(page, total-1))
    gid = str(group['group_id']).replace('\\', '/').replace('\\', '/')
    if gid.startswith('NPCs/'):
        npc_name = gid.split('/')[1].split('.')[0]
        content = entries[page][1]
        speaker = npc_name
        avatar_path = f'/avatar/{npc_name}.png'
        context = None
    else:
        speaker, content = entries[page]
        # 为上下文中的每句话添加角色名
        context = [f"{e[0]}: {e[1]}" for e in entries[max(0, page-5):page]] if page > 0 else None
        avatar_path = f'/avatar/{speaker}.png'
    emote_img_url = get_emote_image_url(group_id, page, denoise)
    return render_template('dialogue.html',
                           logname=group['display'],
                           speaker=speaker,
                           content=content,
                           avatar_path=avatar_path,
                           page=page,
                           total=total,
                           group_id=group['group_id'],
                           denoise=denoise,
                           emote_img_url=emote_img_url)

# 生成表情图片的API
@app.route('/generate_emote', methods=['POST'])
def generate_emote_api():
    data = request.json
    group_id = data['group_id']
    page = int(data['page'])
    denoise = float(data.get('denoise', 0.35))
    ckpt_name = data.get('ckpt_name', 'allInOnePixelModel_v1.ckpt')
    unique_id = data.get('unique_id')
    group = next((g for g in all_dialogue_groups if g['group_id'] == group_id), None)
    if not group:
        print("未找到对话组")
        return jsonify({'status': 'error', 'msg': '未找到对话组'}), 404
    entries = list(group['entries'].items())
    total = len(entries)
    page = max(0, min(page, total-1))
    gid = str(group['group_id']).replace('\\', '/').replace('\\', '/')
    if gid.startswith('NPCs/'):
        npc_name = gid.split('/')[1].split('.')[0]
        content = entries[page][1]
        speaker = npc_name
        context = None
    else:
        speaker, content = entries[page]
        context = [f"{e[0]}: {e[1]}" for e in entries[max(0, page-5):page]] if page > 0 else None
    img_path = get_emote_image_path(group_id, page, denoise, unique_id)
    def run_emote_thread():
        from llm import run_emote
        run_emote(speaker, content, context, denoise, img_path, ckpt_name=ckpt_name)
    threading.Thread(target=run_emote_thread).start()
    return jsonify({'status': 'generating'})

# 查询生成图片状态
@app.route('/get_emote_image')
def get_emote_image():
    group_id = request.args.get('group_id')
    page = int(request.args.get('page', 0))
    denoise = float(request.args.get('denoise', 0.35))
    unique_id = request.args.get('unique_id')
    img_path = get_emote_image_path(group_id, page, denoise, unique_id)
    if Path(img_path).exists():
        return jsonify({'status': 'ready', 'url': get_emote_image_url(group_id, page, denoise, unique_id)})
    else:
        return jsonify({'status': 'generating'})

@app.route('/avatar/<filename>')
def avatar(filename):
    return send_from_directory('input3', filename)

@app.route('/get_prompt')
def get_prompt():
    group_id = request.args.get('group_id')
    page = int(request.args.get('page', 0))
    denoise = float(request.args.get('denoise', 0.35)) if 'denoise' in request.args else 0.35
    group = next((g for g in all_dialogue_groups if g['group_id'] == group_id), None)
    if not group:
        return jsonify({'positive_prompt': '', 'negative_prompt': ''})
    entries = list(group['entries'].items())
    page = max(0, min(page, len(entries)-1))
    gid = str(group['group_id']).replace('\\', '/').replace('\\', '/')
    if gid.startswith('NPCs/'):
        npc_name = gid.split('/')[1].split('.')[0]
        content = entries[page][1]
        speaker = npc_name
        context = None
    else:
        speaker, content = entries[page]
        context = [f"{e[0]}: {e[1]}" for e in entries[max(0, page-5):page]] if page > 0 else None
    from llm import get_emote_prompts
    prompts = get_emote_prompts(speaker, content, context)
    return jsonify({
        'positive_prompt': prompts.get('positive_prompt', ''),
        'negative_prompt': prompts.get('negative_prompt', '')
    })

if __name__ == '__main__':
    app.run(debug=True) 