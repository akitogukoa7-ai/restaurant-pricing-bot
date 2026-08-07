import os
from supabase import create_client

# Supabaseに接続
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# テーブルからデータを取得
response = supabase.table("menu_prices").select("*").execute()
rows = response.data

# ダイナミックプライシング計算ロジック
for row in rows:
    item_id = row['id']
    base = row['base_price']
    stock = row['stock_count']
    expiry = row['expiry_days']

    # ロジック：在庫が5個以上で、期限が1日以下なら20%OFF
    if stock >= 5 and expiry <= 1:
        new_price = int(base * 0.8)
    else:
        new_price = base

    # Supabaseを更新
    supabase.table("menu_prices").update({"current_price": new_price}).eq("id", item_id).execute()
    print(f"更新完了: {row['item_name']} を {new_price} 円に設定しました")
