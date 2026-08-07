import os
from supabase import create_client

# Supabaseに接続
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# 「メニュー価格」テーブルからデータを取得
response = supabase.table("メニュー価格").select("*").execute()
rows = response.data

# ダイナミックプライシング計算ロジック
for row in rows:
    item_id = row['id']
    base = row['基本価格']
    stock = row['在庫数']
    expiry = row['有効期限日数']

    # ロジック：在庫が5個以上で、期限が1日以下なら20%OFF
    if stock >= 5 and expiry <= 1:
        new_price = int(base * 0.8)
    else:
        new_price = base

    # Supabaseの「現在の価格」を更新
    supabase.table("メニュー価格").update({"現在の価格": new_price}).eq("id", item_id).execute()
    print(f"更新完了: {row['アイテム名']} を {new_price} 円に設定しました")
