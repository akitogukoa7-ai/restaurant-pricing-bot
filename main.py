import streamlit as st
from supabase import create_client
import pandas as pd
from openai import OpenAI

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# OpenAIクライアントの初期化
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🍽️ AI駆動型 飲食店メニュー価格最適化システム")

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

# 4. 生成AI（LLM）による高度な価格最適化
st.divider()
st.subheader("🤖 生成AI（LLM）による売れ行き予測＆ダイナミックプライシング")

col_cond1, col_cond2 = st.columns(2)
with col_cond1:
    day_of_week = st.selectbox("本日の曜日", ["土曜日", "日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日"])
with col_cond2:
    weather = st.selectbox("本日の天気", ["晴れ", "雨", "曇り", "雪", "台風"])

if st.button("AIに価格と売れ行きを予測・最適化させる"):
    if df.empty:
        st.warning("データが存在しません。")
    else:
        with st.spinner("AIが売上データ・在庫・天候を多角的に分析中..."):
            data_str = df.to_string(index=False)
            prompt = f"""
            あなたは飲食店のプロフェッショナルな収益管理・価格最適化AIです。
            以下のメニューデータ、本日の曜日（{day_of_week}）、天気（{weather}）を考慮して、
            各メニューの売れ行き予測と、フードロス削減および利益最大化のための最適な価格・アクションの提案を行ってください。

            【現在のメニューデータ】
            {data_str}

            出力は各メニューごとにわかりやすく、Markdown形式で日本語で出力してください。
            """
            
            try:
                response_ai = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "あなたは飲食店のダイナミックプライシングとフードロス削減のエキスパートです。"},
                        {"role": "user", "content": prompt}
                    ]
                )
                ai_analysis = response_ai.choices[0].message.content
                st.success("AI分析が完了しました！")
                st.markdown(ai_analysis)
            except Exception as e:
                st.error(f"AIの呼び出しに失敗しました。SecretsにOPENAI_API_KEYが正しく設定されているか確認してください。エラー: {e}")

# 5. グラフセクション
st.divider()
st.subheader("📈 データ分析・ビジュアル表示")

if not df.empty and 'item_name' in df.columns:
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
