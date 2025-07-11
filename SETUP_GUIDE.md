# KazokuLog セットアップガイド

## 1. Supabaseプロジェクトの作成

### 1.1 Supabaseアカウント作成
1. [Supabase](https://supabase.com/)にアクセス
2. 「Start your project」をクリック
3. GitHubアカウントでサインアップ

### 1.2 新しいプロジェクトを作成
1. 「New Project」をクリック
2. プロジェクト名: `kazokulog`
3. データベースパスワードを設定（覚えておいてください）
4. リージョン: `Northeast Asia (Tokyo)`を選択
5. プランは「Free」を選択
6. 「Create new project」をクリック

### 1.3 データベーススキーマの作成
1. プロジェクトが作成されたら、左サイドバーの「SQL Editor」をクリック
2. 「+ New query」をクリック
3. `database/schema.sql`の内容をコピー＆ペースト
4. 「RUN」をクリックしてスキーマを実行

### 1.4 環境変数の取得
1. 左サイドバーの「Settings」→「API」をクリック
2. 以下の情報をコピー:
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## 2. Claude API キーの取得

### 2.1 Anthropicアカウント作成
1. [Anthropic Console](https://console.anthropic.com/)にアクセス
2. アカウントを作成してログイン
3. 「API Keys」セクションに移動
4. 「Create Key」をクリック
5. キー名を入力（例: `kazokulog-dev`）
6. 生成されたAPIキーをコピー（一度しか表示されません）

### 2.2 クレジット購入
- Claude APIは従量課金制です
- 最初に$5-10程度チャージすることをお勧めします

## 3. 環境変数の設定

### 3.1 バックエンドの環境変数
`backend/.env`ファイルを編集:

```env
# KazokuLog Environment Variables - バックエンド用

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Anthropic Claude API
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

実際の値に置き換えてください。

## 4. アプリケーションの起動

### 4.1 バックエンドの起動
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

### 4.2 フロントエンドの起動（別ターミナル）
```bash
cd frontend
npm run dev
```

## 5. 動作確認

1. **フロントエンド**: http://localhost:3000
2. **バックエンドAPI**: http://localhost:8000
3. **API仕様書**: http://localhost:8000/docs

## 6. 初回使用

1. フロントエンドにアクセス
2. 「新規作成」ボタンをクリック
3. 家族名を入力（例: `田中家`）
4. 生成されたアクセスキーをコピーして保存
5. テキストを入力して「記録する」をクリック
6. AIが自動的に分類して表示されることを確認

## トラブルシューティング

### バックエンドが起動しない
- 環境変数が正しく設定されているか確認
- Python仮想環境が有効になっているか確認
- 依存関係が正しくインストールされているか確認

### フロントエンドが起動しない
- Node.jsのバージョンが18以上か確認
- `npm install`が正常に完了しているか確認

### APIエラーが発生する
- Supabaseプロジェクトが正しく作成されているか確認
- データベーススキーマが正しく実行されているか確認
- Claude APIキーが有効で、クレジットが残っているか確認

## セキュリティ注意事項

- `.env`ファイルは絶対にGitにコミットしないでください
- APIキーは適切に管理し、他人と共有しないでください
- 本番環境では追加の認証機能を実装することを強く推奨します