-- KazokuLog データベーススキーマ

-- 家族テーブル（将来的な拡張用）
CREATE TABLE families (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    access_key VARCHAR(255) UNIQUE NOT NULL, -- URLアクセス用キー
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ログエントリテーブル
CREATE TABLE log_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID REFERENCES families(id),
    original_text TEXT NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'schedule', 'emotion', 'shopping', 'todo', 'memo'
    summary TEXT,
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- カテゴリマスタテーブル
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#6B7280', -- Hex color code
    icon VARCHAR(50), -- Icon name
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 分類結果詳細テーブル（Claude APIのレスポンス詳細保存用）
CREATE TABLE classification_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    log_entry_id UUID REFERENCES log_entries(id) ON DELETE CASCADE,
    confidence_score FLOAT,
    keywords TEXT[], -- 抽出されたキーワード
    ai_reasoning TEXT, -- AI分類の理由
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX idx_log_entries_family_id ON log_entries(family_id);
CREATE INDEX idx_log_entries_date ON log_entries(date);
CREATE INDEX idx_log_entries_category ON log_entries(category);
CREATE INDEX idx_log_entries_created_at ON log_entries(created_at);

-- 初期データ挿入
INSERT INTO categories (name, display_name, color, icon) VALUES
('schedule', '予定・イベント', '#3B82F6', 'calendar'),
('emotion', '子どもの様子', '#EF4444', 'heart'),
('shopping', '買い物リスト', '#10B981', 'shopping-cart'),
('todo', '家族のToDo', '#F59E0B', 'check-square'),
('memo', '雑談・メモ', '#8B5CF6', 'file-text');

-- 更新時刻の自動更新トリガー
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_families_updated_at 
    BEFORE UPDATE ON families 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_log_entries_updated_at 
    BEFORE UPDATE ON log_entries 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) 設定（将来的な認証対応）
ALTER TABLE families ENABLE ROW LEVEL SECURITY;
ALTER TABLE log_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE classification_details ENABLE ROW LEVEL SECURITY;

-- 一時的なアクセス許可ポリシー（認証なし）
CREATE POLICY "Allow all access" ON families FOR ALL USING (true);
CREATE POLICY "Allow all access" ON log_entries FOR ALL USING (true);
CREATE POLICY "Allow all access" ON classification_details FOR ALL USING (true);
CREATE POLICY "Allow all access" ON categories FOR ALL USING (true);