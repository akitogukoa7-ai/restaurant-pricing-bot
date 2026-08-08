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
    st.rerun()

# 4. グラフや分析機能の追加
st.divider()
st.subheader("📈 データ分析・ビジュアル表示")

if not df.empty and 'item_name' in df.columns:
    # グラフ描画用にメニュー名をインデックスに設定
    chart_df = df.set_index('item_name')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 メニュー別 在庫数")
        if 'stock_count' in chart_df.columns:
            st.bar_chart(chart_df['stock_count'])
            
    with col2:
        st.markdown("### 💰 メニュー別 価格比較")
        price_cols = [c for c in ['base_price', 'current_price'] if c in chart_df.columns]
        if price_cols:
            st.bar_chart(chart_df[price_cols])
