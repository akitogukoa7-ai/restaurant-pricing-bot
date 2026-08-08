name: ボット 2号機を実行

on:
  schedule:
    - cron: '0 9 * * *'
  workflow_dispatch:

jobs:
  run-bot:
    runs-on: ubuntu-latest

    steps:
      - name: チェックアウトコード
        uses: actions/checkout@v4

      - name: Pythonをセットアップする
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: 依存関係をインストールします
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: main.pyを実行します。
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python main.py
