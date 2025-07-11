# KazokuLog デプロイメントガイド

このドキュメントでは、KazokuLog アプリケーションをプロダクション環境にデプロイする方法について説明します。

## 🏗️ アーキテクチャ

- **バックエンド**: FastAPI + Gemini API (Railway にデプロイ)
- **フロントエンド**: Next.js (Vercel にデプロイ)
- **AI**: Google Gemini API
- **データベース**: メモリベース (Supabase オプション)

## 📋 前提条件

- Node.js (v18 以上)
- Python 3.9 以上
- Railway アカウント
- Vercel アカウント
- Google Cloud アカウント (Gemini API キー)

## 🚀 デプロイ手順

### 1. バックエンドのデプロイ (Railway)

```bash
cd backend

# Railway CLI をインストール
npm install -g @railway/cli

# Railway にログイン
railway login

# 新しいプロジェクトを作成
railway new

# 環境変数を設定
railway variables set GEMINI_API_KEY=AIzaSyByfM06uWfl_N86SIfAx4QN9G8mC0fH5lE

# デプロイ
railway up
```

または、提供されているスクリプトを使用:

```bash
./deploy_railway.sh
```

### 2. フロントエンドのデプロイ (Vercel)

```bash
cd frontend

# Vercel CLI をインストール
npm install -g vercel

# Vercel にログイン
vercel login

# 本番環境の API URL を設定
echo "NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app" > .env.production

# デプロイ
vercel --prod
```

または、提供されているスクリプトを使用:

```bash
./deploy_vercel.sh
```

## 🔧 設定ファイル

### Backend 設定

#### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Procfile
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### requirements.txt
```
fastapi==0.116.0
uvicorn==0.35.0
pydantic==2.11.7
python-multipart==0.0.6
supabase==2.16.0
python-dotenv==1.0.0
google-generativeai==0.2.0
```

### Frontend 設定

#### .env.local (開発環境)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### .env.production (本番環境)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

## 🌐 環境変数

### Backend (Railway)
- `GEMINI_API_KEY`: Google Gemini API キー
- `SUPABASE_URL`: Supabase プロジェクト URL (オプション)
- `SUPABASE_ANON_KEY`: Supabase 匿名キー (オプション)

### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL`: バックエンド API の URL

## 🔍 デプロイ確認

### バックエンド
```bash
curl https://your-backend-url.railway.app/
```

レスポンス例:
```json
{"message": "KazokuLog API is running"}
```

### フロントエンド
ブラウザでアクセス:
```
https://your-frontend-url.vercel.app
```

## 🚨 トラブルシューティング

### よくある問題

1. **CORS エラー**
   - `app/main.py` の CORS 設定を確認
   - 本番環境では適切なオリジンを設定

2. **API キーエラー**
   - Gemini API キーが正しく設定されているか確認
   - Railway の環境変数が正しく設定されているか確認

3. **環境変数の問題**
   - フロントエンドの API URL が正しく設定されているか確認
   - `NEXT_PUBLIC_` プレフィックスが付いているか確認

## 📊 モニタリング

### Railway
- Railway ダッシュボードでログとメトリクスを確認
- `/` エンドポイントでヘルスチェック

### Vercel
- Vercel ダッシュボードでデプロイメント状況を確認
- アナリティクスでパフォーマンスを監視

## 🔐 セキュリティ

1. **API キーの保護**
   - 環境変数として設定
   - コードにハードコーディングしない

2. **CORS の設定**
   - 本番環境では適切なオリジンのみを許可

3. **HTTPS の使用**
   - Railway と Vercel は自動的に HTTPS を提供

## 📈 スケーリング

### バックエンド
- Railway Pro プランでより多くのリソースを利用可能
- 必要に応じてデータベースを外部化 (Supabase など)

### フロントエンド
- Vercel は自動的にスケーリング
- Edge Functions の活用を検討

## 🤝 サポート

問題が発生した場合:
1. ログを確認
2. 環境変数を確認
3. API エンドポイントをテスト
4. GitHub Issues で報告

---

🎉 デプロイが完了したら、KazokuLog を本番環境で使用できます！