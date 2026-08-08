import os
from supabase import create_client
import pandas as pd

# 1. Supabaseに接続
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# 2. 「メニュー価格」テーブルから現在の在庫や賞味期限を取得
menu_response = supabase.table("menu_prices").select("*").execute()
menu_rows = menu_response.data

# 3. ダイナミックプライシングの計算
for row in menu_rows:
    item_id = row['id']
    item_name = row['item_name']
    base_price = row['base_price']
    stock_count = row['stock_count']
    expiry_days = row['expiry_days']

    # AIの予測販売数（ここでは安全に基本データから5食と設定）
    predicted_sales = 5 

    print(f"【AI予測】{item_name} の予測販売数: {predicted_sales}食 / 現在の在庫: {stock_count}個")

    # 【価格決定AIロジック】
    # 在庫が予測より多く、賞味期限が近い場合は自動値下げ
    if stock_count > predicted_sales * 1.5 and expiry_days <= 2:
        new_price = int(base_price * 0.8) # 20%オフ
        reason = "在庫過多＆期限間近のためAIが自動値下げ"
    elif stock_count > predicted_sales * 2:
        new_price = int(base_price * 0.9) # 10%オフ
        reason = "在庫が多いためAIが微調整値下げ"
    else:
        new_price = base_price
        reason = "適正価格を維持"

    # 4. Supabaseの「current_price」を更新
    supabase.table("menu_prices").update({"current_price": new_price}).eq("id", item_id).execute()
    print(f"➔ 更新結果: {item_name} を {new_price} 円に設定しました（理由: {reason}）\n")
