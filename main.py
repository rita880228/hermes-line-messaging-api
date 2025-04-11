import requests
from bs4 import BeautifulSoup
import os
import hashlib

# Hermes 商品頁
URL = 'https://www.hermes.com/tw/zh/category/women/bags-and-small-leather-goods/all-bags/'

# LINE Messaging API
LINE_CHANNEL_TOKEN = os.environ.get("LINE_CHANNEL_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")

LAST_HASH_FILE = 'last_hash.txt'

def fetch_product_list():
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(URL, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.select('li.product-item')

    products = []
    for item in items:
        name = item.select_one('.product-item-name')
        img = item.select_one('img')
        link = item.find('a', href=True)
        if name and img and link:
            products.append({
                'name': name.text.strip(),
                'img': img['src'],
                'link': 'https://www.hermes.com' + link['href']
            })
    return products

def get_products_hash(products):
    joined = ''.join([p['name'] for p in products])
    return hashlib.md5(joined.encode()).hexdigest()

def load_last_hash():
    try:
        with open(LAST_HASH_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ''

def save_current_hash(h):
    with open(LAST_HASH_FILE, 'w') as f:
        f.write(h)

def send_line_message(text):
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": text}]
    }
    r = requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=body)
    print("發送結果：", r.status_code, r.text)

def notify_new_products(products):
    for p in products[:5]:
        message = f"【新品上架】{p['name']}
{p['link']}
圖片：{p['img']}"
        send_line_message(message)

def check_update():
    print("檢查新品中...")
    products = fetch_product_list()
    if not products:
        print("找不到商品")
        return
    new_hash = get_products_hash(products)
    old_hash = load_last_hash()

    if new_hash != old_hash:
        print("有新商品上架！")
        notify_new_products(products)
        save_current_hash(new_hash)
    else:
        print("沒有新品")

if __name__ == '__main__':
    check_update()

with open("last_hash.txt", "r") as f:
        last_hash = f.read().strip()
except FileNotFoundError:
    last_hash = ""
