#!/bin/bash

# KazokuLog Railway デプロイスクリプト

echo "🚀 KazokuLog バックエンドのデプロイを開始します..."

# Railway CLI をインストール (必要に応じて)
if ! command -v railway &> /dev/null; then
    echo "Railway CLI をインストールしています..."
    npm install -g @railway/cli
fi

# Railway にログイン
echo "Railway にログインしてください..."
railway login

# プロジェクトを作成
echo "新しいプロジェクトを作成しています..."
railway new

# 環境変数を設定
echo "環境変数を設定しています..."
railway variables set GEMINI_API_KEY=AIzaSyByfM06uWfl_N86SIfAx4QN9G8mC0fH5lE

# デプロイ
echo "デプロイを開始しています..."
railway up

echo "✅ デプロイが完了しました！"
echo "🌐 アプリケーションのURLは Railway のダッシュボードで確認できます。"