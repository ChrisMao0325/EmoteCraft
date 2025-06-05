import time
import websocket # 需要: pip install websocket-client
import uuid
import json
import urllib.request
import urllib.parse
import os
import random # 确保导入 random

# --- ComfyUI服务器配置 ---
server_address = "127.0.0.1:8188" 
client_id = str(uuid.uuid4())

# --- ComfyUI API 交互函数 ---

def queue_prompt(prompt_workflow):
    """向ComfyUI服务器提交一个工作流任务"""
    p = {"prompt": prompt_workflow, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(e.read().decode())
        return None

def get_image(filename, subfolder, folder_type):
    """从ComfyUI的输出目录获取图片"""
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()

# ----------------------------------------------------
# 这是新增的、之前遗漏的函数
def get_history(prompt_id):
    """获取指定任务ID的执行历史"""
    try:
        with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"获取历史记录时出错: {e}")
        return {} # 返回空字典以避免后续错误
# ----------------------------------------------------

def get_images_from_websocket(prompt_id):
    """通过websocket连接，实时等待任务完成并获取最终图片 (已优化缓存处理)"""
    # 首先，尝试直接查询一次历史记录，处理任务秒完成的情况
    history = get_history(prompt_id)
    if prompt_id in history and history[prompt_id].get('outputs'):
        print("任务已从缓存中秒完成，直接获取结果。")
    else:
        print("任务正在执行，等待 Websocket 消息...")
        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
        while True:
            try:
                out = ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message['type'] == 'executing':
                        data = message['data']
                        if data.get('node') is None and data.get('prompt_id') == prompt_id:
                            print("Websocket 监听到任务执行完毕。")
                            break 
                else:
                    continue
            except websocket.WebSocketConnectionClosedException:
                print("Websocket connection closed.")
                break
            except Exception as e:
                print(f"An error occurred in websocket: {e}")
                break
        ws.close()
        # 再次获取最终历史记录
        history = get_history(prompt_id)

    images = []
    if prompt_id in history:
        for node_id, node_output in history[prompt_id].get('outputs', {}).items():
            if 'images' in node_output:
                for image_data in node_output['images']:
                    image_bytes = get_image(image_data['filename'], image_data['subfolder'], image_data['type'])
                    images.append(image_bytes)
    return images


def generate_emote(original_image_name, positive_prompt, negative_prompt, 
                   denoise=0.35, output_prefix="EmoteCraft_Result", force_regenerate=True, ckpt_name="allInOnePixelModel_v1.ckpt"):
    """封装了整个EmoteCraft工作流的函数。"""
    try:
        with open('EmoteCraftv1-4.json', 'r', encoding='utf-8') as f:
            prompt_workflow = json.load(f)
    except FileNotFoundError:
        print("错误: 未找到 'EmoteCraftv1-4.json'。")
        return []

    prompt_workflow["10"]["inputs"]["image"] = original_image_name
    prompt_workflow["6"]["inputs"]["text"] = positive_prompt
    prompt_workflow["7"]["inputs"]["text"] = negative_prompt
    prompt_workflow["3"]["inputs"]["denoise"] = denoise
    prompt_workflow["9"]["inputs"]["filename_prefix"] = output_prefix
    # 动态替换模型名
    if "14" in prompt_workflow and "inputs" in prompt_workflow["14"]:
        prompt_workflow["14"]["inputs"]["ckpt_name"] = ckpt_name
    # 如果需要强制重新生成，就设置一个随机种子
    if force_regenerate:
        prompt_workflow["3"]["inputs"]["seed"] = random.randint(0, 999999999999999)

    prompt_data = queue_prompt(prompt_workflow)
    if not prompt_data:
        return []
    
    prompt_id = prompt_data['prompt_id']
    images = get_images_from_websocket(prompt_id)
    
    return images

# --- 如何使用这个封装好的函数 ---
if __name__ == '__main__':
    start_time = time.time()
    source_image_filename = "Pam.png" 
    ee={'positive_prompt': '(best quality:1.3), pixel style, (<pixelart-stardew>:1.3), pure background , professional composition, cheerful expression, warm smile, friendly demeanor, kind eyes, (appreciative:1.2), (grateful:1.1), soft lighting, pastel colors, (happy:1.1), (content:1.1), (helpful:1.1)', 'negative_prompt': 'watermark, text, blur, low quality, poorly drawn face, low quality, exaggerated features, flat colors, pixelated, excessive noise, unwanted artifacts, overexposed lighting, unnatural proportions, inconsistent shading, overly saturated colors, lack of detail, jagged edges, mismatched textures, angry, sad, frowning, upset, gloomy, dark, harsh lighting'}
    pos_prompt = ee['positive_prompt']
    neg_prompt = ee['negative_prompt']
    output_filename_prefix = "Emily_Happy_Expression"

    print("正在向 ComfyUI 提交生成任务...")
    
    generated_images = generate_emote(
        original_image_name=source_image_filename,
        positive_prompt=pos_prompt,
        negative_prompt=neg_prompt,
        denoise=0.4
    )
    
    if generated_images:
        print(f"成功生成 {len(generated_images)} 张图片！")
        for i, img_bytes in enumerate(generated_images):
            output_path = f"{output_filename_prefix}_{i}.png"
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            print(f"图片已保存到: {os.path.abspath(output_path)}")
    else:
        print("生成失败，未能从 ComfyUI 获取到图片。")
        
    end_time = time.time()
    print(f"总耗时: {end_time - start_time:.2f} 秒")