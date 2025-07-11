# KazokuLog

家族の日々を記録・整理するAIダッシュボード

## 機能

- テキスト入力による日記・ログの記録
- Claude AIによる自動カテゴリ分類（予定、子どもの様子、買い物、ToDo、メモ）
- 日付別のログ表示
- 家族単位でのデータ管理
- シンプルな認証なしアクセス

## 技術スタック

- **フロントエンド**: Next.js 14, React, TypeScript, Tailwind CSS
- **バックエンド**: FastAPI, Python
- **データベース**: Supabase (PostgreSQL)
- **AI**: Claude API (Anthropic)

## セットアップ

### 1. 依存関係のインストール

```bash
# バックエンド
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# フロントエンド
cd ../frontend
npm install
```

### 2. 環境変数の設定

1. `.env.example`を参考に`.env`ファイルを作成
2. Supabase プロジェクトを作成し、データベースURLと匿名キーを設定
3. Anthropic Claude API キーを取得・設定

### 3. データベースの初期化

Supabaseの SQL Editor で`database/schema.sql`を実行

### 4. アプリケーションの起動

```bash
# バックエンド (ターミナル1)
cd backend
python app/main.py

# フロントエンド (ターミナル2)
cd frontend
npm run dev
```

## アクセス

- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- API仕様: http://localhost:8000/docs

## 使い方

1. ブラウザで http://localhost:3000 にアクセス
2. 「新規作成」ボタンで家族を作成
3. 生成されたアクセスキーを保存
4. テキストを入力して「記録する」ボタンをクリック
5. AIが自動的にカテゴリ分類して保存

## ディレクトリ構成

```
kazokulog/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── services/
│   │       └── claude_service.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx
│   │       └── layout.tsx
│   └── package.json
├── database/
│   └── schema.sql
└── README.md
```

## 注意事項

- APIキーは適切に管理してください
- 本番環境では認証機能の追加を推奨
- CORS設定は本番環境に応じて調整