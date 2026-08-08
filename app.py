import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Supabase接続情報の取得
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("飲食店メニュー価格最適化ダッシュボード")

# 英語のテーブル名でデータを取得
response = supabase.table("menu_prices").select("*").execute()
data = response.data

if data:
    df = pd.DataFrame(data)
    
    st.subheader("メニュー一覧")
    
    # 検索機能
    search_query = st.text_input("メニュー名で検索")
    if search_query:
        filtered_df = df[df['item_name'].str.contains(search_query, na=False)]
    else:
        filtered_df = df
        
    st.dataframe(filtered_df)
else:
    st.info("データがありません。")
