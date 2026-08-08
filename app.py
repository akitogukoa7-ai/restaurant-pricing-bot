import streamlit as st
from supabase import create_client
import pandas as pd
import requests

# Supabaseの設定（エラーが出ないよう安全に取得）
url = st.secrets.get("SUPABASE_URL", "")
key = st.secrets.get("SUPABASE_KEY", "")

line_token = st.secrets.get("LINE_TOKEN", "")
line_user_id = st.secrets.get("LINE_USER_ID", "")

if not url or not key:
    st.error("⚠️ StreamlitのSecretsに SUPABASE_URL と SUPABASE_KEY を設定してください。")
    st.stop()

supabase = create_client(url, key)

# --- LINE通知送信関数 ---
def send_line_push(message):
    if not line_token or not line_user_id:
        return None, "LINEのトークンまたはユーザーIDがSecretsに設定されていません。"
    
    api_url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {line_token}"
    }
    payload = {
        "to": line_user_id,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(api_url, headers=headers, json=payload)
    return response, None

# --- サイドバーに管理者ツールを追加 ---
with st.sidebar:
    st.subheader("🛠️ 管理者ツール")
    if st.button("🔔 LINEテスト通知を送信"):
        test_msg = "これは飲食店メニュー価格最適化ロボットのテスト通知です。"
        res, err = send_line_push(test_msg)
        if err:
            st.error(err)
        elif res and res.status_code == 200:
            st.success("LINEにテスト送信しました！")
        else:
            code = res.status_code if res else "不明"
            st.error(f"送信失敗: {code}")

st.title("🍽️ 飲食店メニュー価格最適化ロボット")

# 1. データの取得
try:
    response = supabase.table("menu_prices").select("*").execute()
    df = pd.DataFrame(response.data)
except Exception as e:
    df = pd.DataFrame()
    st.warning("データベースからデータを取得できませんでした。テーブル名が 'menu_prices' になっているか確認してください。")

# 2. 検索・フィルター機能
st.subheader("メニュー価格・在庫の編集")
search_query = st.text_input("🔍 メニュー名で検索", "")
if search_query and not df.empty and 'item_name' in df.columns:
    filtered_df = df[df['item_name'].str.contains(search_query, na=False)]
else:
    filtered_df = df

if not filtered_df.empty:
    edited_df = st.data_editor(filtered_df, num_rows="dynamic", key="menu_editor")
else:
    edited_df = pd.DataFrame()
    st.info("データがありません。")

# 3. 更新ボタン
if st.button("変更を保存する") and not edited_df.empty:
    for index, row in edited_df.iterrows():
        supabase.table("menu_prices").update({
            "base_price": int(row['base_price']),
            "current_price": int(row['current_price']),
            "stock_count": int(row['stock_count'])
        }).eq("id", row['id']).execute()
    st.success("データベースを更新しました！")
    st.rerun()

# 4. AI価格最適化・提案機能
st.divider()
st.subheader("🤖 AI価格最適化・ダイナミックプライシング提案")

if not df.empty:
    only_alerts = st.checkbox("🚨 値下げ・処分が必要なメニューのみ表示する", value=False)
    st.markdown("在庫状況や賞味期限（残り日数）をもとに、AIが最適な価格とアクションを提案します。")
    
    for index, row in df.iterrows():
        item = row.get('item_name', '不明')
        stock = row.get('stock_count', 0)
        expiry = row.get('expiry_days', 7)
        base = row.get('base_price', 1000)
        current = row.get('current_price', base)
        
        # AIの提案ロジック
        if expiry <= 1:
            suggested_price = int(base * 0.5)
            suggestion_type = "alert"
            suggestion = f"⚠️ **【要処分】** 本日期限切れ間近です。半額（¥{suggested_price}）で早期完売を目指してください。"
        elif expiry <= 2 and stock > 5:
            suggested_price = int(base * 0.7)
            suggestion_type = "alert"
            suggestion = f"🚨 **【緊急値下げ推奨】** 賞味期限が残り{expiry}日で在庫が{stock}個あります。廃棄ロスを防ぐため、30%OFF（¥{suggested_price}）でのタイムセールを強く推奨します。"
        elif stock >= 10:
            suggested_price = int(base * 0.85)
            suggestion_type = "warning"
            suggestion = f"📦 **【在庫過多】** 在庫が多めです。15%OFF（¥{suggested_price}）にして回転率を上げましょう。"
        else:
            suggested_price = base
            suggestion_type = "normal"
            suggestion = f"✨ **【適正価格】** 現在の価格設定は安定しています。このまま様子を見ましょう。"
            
        if only_alerts and suggestion_type == "normal":
            continue
            
        with st.container(border=True):
            st.markdown(f"### 🏷️ {item}")
            cols = st.columns(3)
            cols[0].metric("現在の価格", f"¥{current}")
            cols[1].metric("推奨価格", f"¥{suggested_price}")
            cols[2].metric("在庫 / 期限", f"{stock}個 / {expiry}日")
            st.markdown(suggestion)

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
