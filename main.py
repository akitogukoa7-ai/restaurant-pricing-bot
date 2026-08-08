import os
from supabase import create_client
import pandas as pd

# 1. Supabaseに接続
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# 2. 過去の売上データ（sales_data）を読み込んでAI（予測の基準）を作る
sales_response = supabase.table("sales_data").select("*").execute()
df_sales = pd.DataFrame(sales_response.data)

# 例として、今日の天気は「雨」と仮定してシミュレーションします
todays_weather = "雨" 

# 天気ごとの平均売上数を計算（簡単な機械学習・統計モデルの代わり）
if not df_sales.empty:
    weather_avg = df_sales.groupby(['item_name', 'weather'])['sales_count'].mean().reset_index()
else:
    weather_avg = pd.DataFrame()

# 3. 「メニュー価格」テーブルから現在の在庫や賞味期限を取得
menu_response = supabase.table("menu_prices").select("*").execute()
menu_rows = menu_response.data

# 4. 需要予測とダイナミックプライシングの計算
for row in menu_rows:
    item_id = row['id']
    item_name = row['item_name']
    base_price = row['base_price']
    stock_count = row['stock_count']
    expiry_days = row['expiry_days']

    # 過去データから「今日の天気（雨など）」における予測売上数を割り出す
    predicted_sales = 5 # デフォルト値
    if not weather_avg.empty:
        matched = weather_avg[(weather_avg['item_name'] == item_name) & (weather_avg['weather'] == todays_weather)]
        if not matched.empty:
            predicted_sales = matched['sales_count'].values[0]

    print(f"【AI予測】{item_name}（天気: {todays_weather}）の予測販売数: {predicted_sales}食 / 現在の在庫: {stock_count}個")

    # 【価格決定AIロジック】
    # 「予測販売数」に対して「在庫」が多すぎる（かつ賞味期限が近い）場合、自動値下げ
    if stock_count > predicted_sales * 1.5 and expiry_days <= 2:
        new_price = int(base_price * 0.8) # 20%オフ
        reason = "在庫過多＆期限間近のためAIが自動値下げ"
    elif stock_count > predicted_sales * 2:
        new_price = int(base_price * 0.9) # 10%オフ
        reason = "在庫が多いためAIが微調整値下げ"
    else:
        new_price = base_price
        reason = "適正価格を維持"

    # 5. Supabaseの「current_price」を更新
    supabase.table("menu_prices").update({"current_price": new_price}).eq("id", item_id).execute()
    print(f"➔ 更新結果: {item_name} を {new_price} 円に設定しました（理由: {reason}）\n")
