import os
import streamlit as st  # もし使っていなければ削除してOKです
from supabase import create_client
from openai import OpenAI

# GitHubの環境変数、またはローカルのsecretsから安全に取得する
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 以降の処理...
print("接続テスト成功！")
