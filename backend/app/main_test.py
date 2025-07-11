"""
KazokuLog FastAPI バックエンド - テスト用（環境変数なしで起動可能）
"""
import os
from datetime import datetime, date
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

app = FastAPI(title="KazokuLog API - Test Mode", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js開発サーバー
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# テスト用のメモリデータベース
test_families = {}
test_log_entries = {}
test_categories = [
    {"id": str(uuid.uuid4()), "name": "schedule", "display_name": "予定・イベント", "color": "#3B82F6", "icon": "calendar"},
    {"id": str(uuid.uuid4()), "name": "emotion", "display_name": "子どもの様子", "color": "#EF4444", "icon": "heart"},
    {"id": str(uuid.uuid4()), "name": "shopping", "display_name": "買い物リスト", "color": "#10B981", "icon": "shopping-cart"},
    {"id": str(uuid.uuid4()), "name": "todo", "display_name": "家族のToDo", "color": "#F59E0B", "icon": "check-square"},
    {"id": str(uuid.uuid4()), "name": "memo", "display_name": "雑談・メモ", "color": "#8B5CF6", "icon": "file-text"},
]

# データモデル
class LogEntryCreate(BaseModel):
    text: str
    family_access_key: str
    entry_date: Optional[date] = None

class LogEntryResponse(BaseModel):
    id: str
    original_text: str
    category: str
    summary: str
    date: date
    keywords: List[str]
    confidence_score: float
    created_at: datetime

class FamilyCreate(BaseModel):
    name: str

class FamilyResponse(BaseModel):
    id: str
    name: str
    access_key: str
    created_at: datetime

# テスト用のテキスト分類関数
def mock_classify_text(text: str) -> dict:
    """テキストをモック分類する"""
    if "買い物" in text or "買う" in text or "スーパー" in text:
        return {
            "category": "shopping",
            "confidence_score": 0.9,
            "summary": f"買い物: {text[:30]}...",
            "keywords": ["買い物", "スーパー"],
            "reasoning": "買い物関連のキーワードが含まれているため"
        }
    elif "運動会" in text or "学校" in text or "病院" in text:
        return {
            "category": "schedule",
            "confidence_score": 0.8,
            "summary": f"予定: {text[:30]}...",
            "keywords": ["予定", "イベント"],
            "reasoning": "予定やイベントに関連するキーワードが含まれているため"
        }
    elif "子ども" in text or "太郎" in text or "機嫌" in text:
        return {
            "category": "emotion",
            "confidence_score": 0.7,
            "summary": f"子どもの様子: {text[:30]}...",
            "keywords": ["子ども", "様子"],
            "reasoning": "子どもの状態に関するキーワードが含まれているため"
        }
    elif "やる" in text or "申請" in text or "手続き" in text:
        return {
            "category": "todo",
            "confidence_score": 0.6,
            "summary": f"ToDo: {text[:30]}...",
            "keywords": ["やること", "タスク"],
            "reasoning": "やるべきことに関するキーワードが含まれているため"
        }
    else:
        return {
            "category": "memo",
            "confidence_score": 0.5,
            "summary": f"メモ: {text[:30]}...",
            "keywords": ["メモ", "雑談"],
            "reasoning": "特定のカテゴリに該当しないため"
        }

# API エンドポイント
@app.post("/api/families", response_model=FamilyResponse)
async def create_family(family: FamilyCreate):
    """家族を作成し、アクセスキーを発行"""
    family_id = str(uuid.uuid4())
    access_key = str(uuid.uuid4())
    
    family_data = {
        "id": family_id,
        "name": family.name,
        "access_key": access_key,
        "created_at": datetime.now()
    }
    
    test_families[access_key] = family_data
    
    return FamilyResponse(**family_data)

@app.post("/api/logs", response_model=LogEntryResponse)
async def create_log_entry(log_entry: LogEntryCreate):
    """ログエントリを作成（テストモード）"""
    # 家族の存在確認
    if log_entry.family_access_key not in test_families:
        raise HTTPException(status_code=404, detail="Family not found")
    
    # モック分類
    classification = mock_classify_text(log_entry.text)
    
    # エントリ日付の設定
    entry_date = log_entry.entry_date or date.today()
    
    # ログエントリを作成
    log_id = str(uuid.uuid4())
    log_data = {
        "id": log_id,
        "original_text": log_entry.text,
        "category": classification["category"],
        "summary": classification["summary"],
        "date": entry_date,
        "keywords": classification["keywords"],
        "confidence_score": classification["confidence_score"],
        "created_at": datetime.now()
    }
    
    if log_entry.family_access_key not in test_log_entries:
        test_log_entries[log_entry.family_access_key] = []
    
    test_log_entries[log_entry.family_access_key].append(log_data)
    
    return LogEntryResponse(**log_data)

@app.get("/api/logs/{family_access_key}", response_model=List[LogEntryResponse])
async def get_log_entries(family_access_key: str, date_filter: Optional[str] = None):
    """指定された家族のログエントリを取得"""
    if family_access_key not in test_families:
        raise HTTPException(status_code=404, detail="Family not found")
    
    entries = test_log_entries.get(family_access_key, [])
    
    if date_filter:
        entries = [entry for entry in entries if entry["date"].isoformat() == date_filter]
    
    # 作成日時の降順でソート
    entries.sort(key=lambda x: x["created_at"], reverse=True)
    
    return [LogEntryResponse(**entry) for entry in entries]

@app.get("/api/categories")
async def get_categories():
    """利用可能なカテゴリ一覧を取得"""
    return test_categories

@app.get("/")
async def root():
    """ヘルスチェック"""
    return {"message": "KazokuLog API is running in TEST MODE"}

@app.get("/test")
async def test_endpoint():
    """テスト用エンドポイント"""
    return {
        "message": "Test endpoint working",
        "families_count": len(test_families),
        "log_entries_count": sum(len(entries) for entries in test_log_entries.values()),
        "categories_count": len(test_categories)
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting KazokuLog API in TEST MODE")
    print("📝 Environment variables are NOT required in test mode")
    print("🌐 API will be available at: http://localhost:8000")
    print("📖 API documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)