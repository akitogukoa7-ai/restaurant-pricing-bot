import os
import requests
from supabase import create_client
import pandas as pd

# 1. 接続設定
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# アクセストークンとユーザーIDを直接設定
line_token = "IOWuTJ9k5hVlRun/wMv0I4UFAzS0LhnkwQbUzsAggMaZTUT0rh+N3UDFlUnXR4APPbwnx4ryo+9fhaTGAgQcscAY3jRGgegLV0slv2uAQJjUhZDMWyQX0YzYJuGrDEUkYy5DdcyJ33JYJ2mCYOoOLgdB04t89/1O/w1cDnyilFU="
line_user_id = "U17b891ca13af6478619f62720380c44d"

supabase = create_client(url, key)

# 2. LINEにプッシュ通知を送る関数
def send_line_push(message):
    api_url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {line_token}"
    }
    payload = {
        "to": line_user_id,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        print("LINE通知の送信に成功しました！")
    else:
        print(f"LINE通知エラー: {response.status_code}, {response.text}")

# 3. メニュー価格を取得して判定
menu_response = supabase.table("menu_prices").select("*").execute()
menu_rows = menu_response.data

for row in menu_rows:
    item_id = row['id']
    item_name = row['item_name']
    base_price = row['base_price']
    stock_count = row['stock_count']
    expiry_days = row['expiry_days']

    predicted_sales = 5 

    # 価格決定AIロジック
    if stock_count > predicted_sales * 1.5 and expiry_days <= 2:
        new_price = int(base_price * 0.8) # 20%オフ
        reason = "在庫過多＆期限間近のためAIが自動値下げ"
    elif stock_count > predicted_sales * 2:
        new_price = int(base_price * 0.9) # 10%オフ
        reason = "在庫が多いためAIが微調整値下げ"
    else:
        new_price = base_price
        reason = "適正価格を維持"

    # Supabaseを更新
    supabase.table("menu_prices").update({"current_price": new_price}).eq("id", item_id).execute()
    print(f"更新: {item_name} -> {new_price}円 ({reason})")

    # 価格が下がった場合のみLINEに通知
    if new_price < base_price:
        msg = f"【価格自動更新通知】\n{item_name}がAIにより割引されました！\n定価: {base_price}円 ➔ 現在: {new_price}円\n理由: {reason}"
        send_line_push(msg)
