import os
import requests
import json

# --- 設定區 ---
# 1015537 是星穹鐵道官方, 172534910 是原神官方
HOYO_CONFIG = {
    "172534910": {"name": "原神官方", "color": 65490, "icon": "🍀"},
    "1015537": {"name": "星穹鐵道官方", "color": 16768768, "icon": "🚂"}
}

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
MEMORY_FILE = "hoyo_memory.json"

def get_hoyo_posts(uid):
    api_url = f"https://bbs-api-os.hoyolab.com/community/post/wapi/userPost?uid={uid}"
    try:
        res = requests.get(api_url)
        return res.json().get("data", {}).get("list", [])
    except:
        return []

# 1. 讀取記憶
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
else:
    memory = {}

# 2. 巡邏帳號
for uid, info in HOYO_CONFIG.items():
    posts = get_hoyo_posts(uid)
    if not posts: continue
    
    latest_post = posts[0]
    post_id = latest_post["post"]["post_id"]
    title = latest_post["post"]["subject"]
    img_url = latest_post["post"]["cover"] or latest_post["post"].get("f_forum_id") # 抓封面圖
    link = f"https://www.hoyolab.com/article/{post_id}"

    # 3. 發現新貼文
    if memory.get(uid) != post_id:
        print(f"發現 {info['name']} 新貼文！")
        
        # 設定角色台詞
        quote = "「派蒙肚子餓了...欸不對，是提瓦特有新動態了！」" if uid == "172534910" else "「開拓者快看！三月七剛拍到了新的開拓情報喔！」"

        payload = {
            "embeds": [{
                "title": f"{info['icon']} {info['name']} 最新情報",
                "description": f"{quote}\n\n**{title}**",
                "url": link,
                "color": info["color"],
                "image": {"url": img_url},
                "footer": {"text": "米哈遊情報站 · 自動巡邏中"}
            }]
        }
        
        requests.post(WEBHOOK_URL, json=payload)
        memory[uid] = post_id

# 4. 存回記憶
with open(MEMORY_FILE, "w") as f:
    json.dump(memory, f)
