import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import time

def download_avatar(name):
    url = f"https://stardewvalleywiki.com/{name}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        div = soup.find('div', class_='floatnone')
        if not div:
            print(f"未找到头像div: {name}")
            return False
        img = div.find('img')
        if not img or not img.get('src'):
            print(f"未找到头像img: {name}")
            return False
        img_url = img['src']
        if img_url.startswith('/'):
            img_url = 'https://stardewvalleywiki.com' + img_url
        # 下载图片
        input_dir = Path('input')
        input_dir.mkdir(exist_ok=True)
        img_path = input_dir / f"{name}.png"
        img_data = requests.get(img_url, headers=headers, timeout=10).content
        with open(img_path, 'wb') as f:
            f.write(img_data)
        print(f"已下载: {img_path}")
        return True
    except Exception as e:
        print(f"下载{name}头像失败: {e}")
        return False

def download_all_avatars():
    # 读取角色名
    with open('output/character_names.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    names = data.get('characters', [])
    print(f"共需下载{len(names)}个角色头像...")
    for name in names:
        download_avatar(name)
        time.sleep(1)  # 防止请求过快被封

if __name__ == "__main__":
    download_all_avatars() 