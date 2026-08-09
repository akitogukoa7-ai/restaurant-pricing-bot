import os
import requests
from supabase import create_client

# 1. 接続設定
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
line_token = os.environ.get("LINE_TOKEN")
line_user_id = os.environ.get("LINE_USER_ID")

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

# 値下げされた商品の通知文を溜めておくリスト
discounted_messages = []

for row in menu_rows:
    item_id = row.get('id')
    item_name = row.get('item_name', '不明')
    base_price = row.get('base_price', 1000)
    stock_count = row.get('stock_count', 0)
    expiry_days = row.get('expiry_days', 7)

    predicted_sales = 5 

    # 価格決定AIロジック（緊急度の高い順に評価）
    if expiry_days <= 1:
        new_price = int(base_price * 0.5)
        reason = "本日期限切れ間近のためAIが半額に自動調整"
    elif stock_count > predicted_sales * 1.5 and expiry_days <= 2:
        new_price = int(base_price * 0.8)
        reason = "在庫過多＆期限間近のためAIが20%OFFに自動値下げ"
    elif stock_count > predicted_sales * 2:
        new_price = int(base_price * 0.9)
        reason = "在庫が多いためAIが10%OFFに微調整値下げ"
    else:
        new_price = base_price
        reason = "適正価格を維持"

    # Supabaseの current_price を更新
    supabase.table("menu_prices").update({"current_price": new_price}).eq("id", item_id).execute()
    print(f"更新: {item_name} -> {new_price}円 ({reason})")

    # 価格が下がった場合は、通知用リストに追加
    if new_price < base_price:
        item_msg = f"・{item_name}\n  定価: {base_price}円 ➔ 現在: {new_price}円\n  理由: {reason}"
        discounted_messages.append(item_msg)

# 4. 価格が下がった商品がある場合、1通にまとめてLINEに通知
if discounted_messages:
    joined_msg = "\n\n".join(discounted_messages)
    full_msg = f"【価格自動更新通知】\nAIにより以下のメニューが割引されました！\n\n{joined_msg}"
    send_line_push(full_msg)
