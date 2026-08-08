import streamlit as st
from supabase import create_client
import pandas as pd
import os

# Supabase接続情報（環境変数がない場合は直接書いてもOKですが、非公開に注意！）
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

st.title("🍽️ 飲食店メニュー管理ダッシュボード")

# 1. データの取得
response = supabase.table("menu_prices").select("*").execute()
df = pd.DataFrame(response.data)

# 2. 編集可能なテーブルを表示
st.subheader("メニュー価格・在庫の編集")
edited_df = st.data_editor(df, num_rows="dynamic")

# 3. 更新ボタン
if st.button("保存する"):
    # 変更があった行だけをSupabaseに反映させる簡易的なロジック
    for index, row in edited_df.iterrows():
        supabase.table("menu_prices").update({
            "base_price": int(row['base_price']),
            "stock_count": int(row['stock_count'])
        }).eq("id", row['id']).execute()
    st.success("データベースを更新しました！")
