import streamlit as st
from supabase import create_client
import pandas as pd

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
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
    for index, row in edited_df.iterrows():
        supabase.table("menu_prices").update({
            "base_price": int(row['base_price']),
            "stock_count": int(row['stock_count'])
        }).eq("id", row['id']).execute()
    st.success("データベースを更新しました！")
