import os
from supabase import create_client
from openai import OpenAI

# GitHubの環境変数から安全に秘密情報を取得する
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# OpenAIクライアントの初期化
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def main():
    print("AIダイナミックプライシング・Botの実行を開始します...")
    
    # データベースからメニュー情報を取得
    response = supabase.table("menu_prices").select("*").execute()
    data = response.data
    
    if not data:
        print("メニューデータが見つかりませんでした。")
        return

    print(f"取得したメニュー数: {len(data)}件")
    print("処理が正常に完了しました！")

if __name__ == "__main__":
    main()
