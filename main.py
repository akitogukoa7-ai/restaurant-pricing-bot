import os
import requests
from supabase import create_client, Client
import pandas as pd

# 環境変数の取得
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
LINE_TOKEN = os.environ.get("LINE_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

# Supabaseクライアントの初期化
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    print("ボットの実行を開始します...")
    
    # 1. Supabaseからメニューデータを取得
    response = supabase.table("menu_prices").select("*").execute()
    data = response.data
    
    if not data:
        print("データが見つかりませんでした。")
        return

    df = pd.DataFrame(data)
    print("取得したデータ:", df)
    
    # 2. LINE APIを通じた通知送信
    api_url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    
    message_text = "【飲食店メニュー価格最適化ボット】\n本日の自動チェックが正常に完了しました！"
    
    payload = {
        "to": LINE_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message_text
            }
        ]
    }
    
    response_line = requests.post(api_url, headers=headers, json=payload)
    if response_line.status_code == 200:
        print("LINE通知の送信に成功しました。")
    else:
        print(f"LINE通知の送信に失敗しました: {response_line.text}")

if __name__ == "__main__":
    main()
