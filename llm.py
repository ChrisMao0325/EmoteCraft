from pathlib import Path
from main import generate_emote
import requests
import json
import os
import hashlib

_prompt_cache = {}

def get_prompt_cache_key(speaker, current_text, context):
    key_str = speaker + '||' + current_text + '||' + ("\n".join(context) if context else "")
    return hashlib.md5(key_str.encode('utf-8')).hexdigest()

def call_llm(prompt):
    """
    调用LLM API
    输入：
        prompt: 提示词
    输出：
        dict，包含positive_prompt和negative_prompt
    """
    # 从环境变量获取API配置
    api_base = os.getenv('LLM_API_BASE')
    api_key = os.getenv('LLM_API_KEY')
    model_name = os.getenv('LLM_MODEL_NAME')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    data = {
        'model': model_name,  # 或其他模型名称
        'messages': [
            {'role': 'system', 'content': '你是一个专业的AI图像生成提示词专家，擅长生成角色表情提示词。'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.7
    }
    
    try:
        response = requests.post(f'{api_base}/chat/completions', headers=headers, json=data)
        #print("LLM API response status:", response.status_code)
        #print("LLM API response text:", response.text)
        response.raise_for_status()
        result = response.json()
        
        # 解析返回的JSON字符串
        content = result['choices'][0]['message']['content']
        json_content=json.loads(content)
        return json_content
    except Exception as e:
        print(f'调用LLM API失败: {e}')
        # 返回默认值
        return ""

def get_emote_prompts(speaker, current_text, context=None):
    cache_key = get_prompt_cache_key(speaker, current_text, context)
    if cache_key in _prompt_cache:
        print("cache hit")
        return _prompt_cache[cache_key]
    # 构造大模型提示词
    prompt = f"角色：{speaker}\n"
    if context:
        prompt += "对话上下文：\n" + "\n".join(context) + "\n"
    prompt += f"当前说的话：{current_text}\n"
    prompt += f"请根据上述内容，生成适合驱动像素风格AI肖像生成生成{speaker}肖像的情绪相关的positive_prompt和negative_prompt。已有common positive prompt (best quality:1.3)，(<pixelart-stardew>:1.3)，(pure background:1.3),professional composition 和negative prompt watermark, text, blur, low quality,poorly drawn face, low quality, exaggerated features, flat colors, pixelated, excessive noise, unwanted artifacts, overexposed lighting, unnatural proportions, inconsistent shading, overly saturated colors, lack of detail, jagged edges, mismatched textures请把它拼接到你生成的情绪相关的prompt前面。你可以使用类似(best quality:1.3)来调整你的关键词的权重,为了使情绪表现明显，你的positive prompt 至少有一个需要达到1.5。你生成的提示词只需要关于情绪，不要有具体内容的描述.\n你只需要输出json字典，包含positive_prompt和negative_prompt，不要输出任何解释，不用使用markdown包裹。\n。"
    print(prompt)
    result = call_llm(prompt)
    _prompt_cache[cache_key] = result
    return result

def run_emote(speaker, content, context, denoise, img_path, ckpt_name="allInOnePixelModel_v1.ckpt"):
    """
    生成表情图片
    输入：
        speaker: 人物名
        content: 当前对话内容
        context: 对话上下文
        denoise: 风格变化强度
        img_path: 输出图片路径
        ckpt_name: checkpoint模型名
    """
    print('开始生成表情...')
    prompts = get_emote_prompts(speaker, content, context)
    # 移除已有 style
    for style in ["pixel style", "realistic style", "cartoon style"]:
        prompts["positive_prompt"] = prompts["positive_prompt"].replace(f",{style}", "").replace(style, "")
    # 只追加当前模型的 style
    if "ixel" in ckpt_name:
        prompts["positive_prompt"] += ",pixel style"
    elif "cartoon" in ckpt_name:
        prompts["positive_prompt"] += ",cartoon style"
    elif "realistic" in ckpt_name:
        prompts["positive_prompt"] += ",realistic style"
    print('获得prompt:', prompts)
    images = generate_emote(
        original_image_name=f"{speaker}.png",
        positive_prompt=prompts["positive_prompt"],
        negative_prompt=prompts["negative_prompt"],
        denoise=denoise,
        output_prefix=img_path[:-4],
        force_regenerate=True,
        ckpt_name=ckpt_name
    )
    print('生成图片结果: 成功' if images and len(images) > 0 else '生成图片结果: 失败')
    if images and len(images) > 0:
        Path(img_path).parent.mkdir(parents=True, exist_ok=True)
        with open(img_path, 'wb') as f:
            f.write(images[0])
        print('图片已保存:', img_path)
    else:
        print('图片生成失败')

# 示例用法
if __name__ == "__main__":
    result = get_emote_prompts("Abigail", "你让我的心都碎了……我不能再和你说话了。", context=None)
    print(result) 