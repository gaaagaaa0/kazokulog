#!/bin/bash

# KazokuLog Frontend Vercel デプロイスクリプト

echo "🚀 KazokuLog フロントエンドのデプロイを開始します..."

# Vercel CLI をインストール (必要に応じて)
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI をインストールしています..."
    npm install -g vercel
fi

# 本番環境の API URL を設定
echo "本番環境の API URL を設定してください:"
read -p "Railway にデプロイしたバックエンドの URL を入力してください: " BACKEND_URL

# .env.production ファイルを更新
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > .env.production

# Vercel にログイン
echo "Vercel にログインしてください..."
vercel login

# デプロイ
echo "デプロイを開始しています..."
vercel --prod

echo "✅ デプロイが完了しました！"
echo "🌐 アプリケーションのURLは Vercel のダッシュボードで確認できます。"