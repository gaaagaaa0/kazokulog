# 環境変数設定ガイド

## 必要な環境変数

KazokuLogを動作させるために以下の環境変数を設定する必要があります。

### 1. Supabase環境変数

#### Supabaseプロジェクトの作成
1. [Supabase](https://supabase.com/) にアクセス
2. 「New Project」をクリック
3. プロジェクト名: `kazokulog`
4. データベースパスワードを設定（強力なパスワードを推奨）
5. リージョン: `Northeast Asia (Tokyo)`を選択
6. 「Create new project」をクリック

#### 環境変数の取得
1. プロジェクト作成後、「Settings」→「API」をクリック
2. 以下の値をコピー:
   - **URL**: プロジェクトのURL（例: `https://abcdefghijklmnop.supabase.co`）
   - **anon public**: 匿名公開キー（例: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`）

### 2. Claude API キー

#### Anthropicアカウントの作成
1. [Anthropic Console](https://console.anthropic.com/) にアクセス
2. アカウント作成（電話番号認証が必要）
3. 「API Keys」をクリック
4. 「Create Key」をクリック
5. キー名を入力（例: `kazokulog-development`）
6. 生成されたキーをコピー（例: `sk-ant-api03-...`）

#### 重要：クレジットの購入
- Claude APIは従量課金制です
- 使用前に$5-10程度のクレジットを購入してください
- 「Billing」→「Credits」で購入できます

### 3. 環境変数ファイルの作成

#### backend/.envファイル
`backend/.env`ファイルを作成し、以下の内容を記入してください：

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...（実際のキーに置き換え）

# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-api03-...（実際のキーに置き換え）
```

### 4. データベースの初期化

#### SQLスキーマの実行
1. Supabaseプロジェクトで「SQL Editor」をクリック
2. 「New query」をクリック
3. `database/schema.sql`の内容をコピー&ペースト
4. 「RUN」をクリック

実行が成功すると、以下のテーブルが作成されます：
- `families` - 家族データ
- `log_entries` - ログエントリ
- `categories` - カテゴリマスタ
- `classification_details` - 分類詳細

### 5. 設定の確認

#### 環境変数の確認
```bash
cd backend
source venv/bin/activate
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('SUPABASE_URL:', os.getenv('SUPABASE_URL'))
print('SUPABASE_ANON_KEY:', os.getenv('SUPABASE_ANON_KEY')[:20] + '...')
print('ANTHROPIC_API_KEY:', os.getenv('ANTHROPIC_API_KEY')[:20] + '...')
"
```

#### データベース接続の確認
```bash
python -c "
import os
from dotenv import load_dotenv
from supabase import create_client
load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))
result = supabase.table('categories').select('*').execute()
print('Categories count:', len(result.data))
"
```

### 6. セキュリティ注意事項

- **絶対に`.env`ファイルをGitにコミットしないでください**
- APIキーは他人と共有しないでください
- 本番環境では追加のセキュリティ対策を実装してください
- 定期的にAPIキーをローテーションしてください

### 7. トラブルシューティング

#### よくあるエラー

1. **"Environment variables are missing"**
   - `.env`ファイルが存在するか確認
   - 環境変数の値が正しく設定されているか確認

2. **Supabase接続エラー**
   - プロジェクトURLが正しいか確認
   - 匿名キーが正しいか確認
   - データベーススキーマが実行されているか確認

3. **Claude API エラー**
   - APIキーが正しいか確認
   - クレジットが残っているか確認
   - API利用制限に達していないか確認

#### ログの確認
```bash
# バックエンドのログを確認
cd backend
source venv/bin/activate
python app/main.py
```

これで環境変数の設定が完了です。次にアプリケーションを起動してテストしましょう。