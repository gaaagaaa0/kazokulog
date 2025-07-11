"""
KazokuLog FastAPI バックエンド - Gemini API版
テキスト入力 → 分類 → 保存 → 表示の一連の処理
"""
import os
import json
import re
from datetime import datetime, date
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import uuid
from dotenv import load_dotenv
import google.generativeai as genai

# 環境変数を読み込み
load_dotenv()

app = FastAPI(title="KazokuLog API", version="1.0.0")

# CORS設定 - 本番用に更新
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では適切なドメインに制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 環境変数設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini APIの設定
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("🤖 Gemini API連携が有効になりました")
else:
    print("⚠️ Gemini APIキーが設定されていません。フォールバック機能を使用します。")

# Supabaseクライアント（オプション）
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("📊 Supabase連携が有効になりました")
else:
    print("⚠️ Supabase設定が不完全です。メモリベースで動作します。")

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
    """ログエントリ作成用モデル"""
    text: str
    family_access_key: str
    entry_date: Optional[date] = None

class LogEntryResponse(BaseModel):
    """ログエントリレスポンス用モデル"""
    id: str
    original_text: str
    category: str
    summary: str
    date: date
    keywords: List[str]
    confidence_score: float
    created_at: datetime

class FamilyCreate(BaseModel):
    """家族作成用モデル"""
    name: str

class FamilyResponse(BaseModel):
    """家族レスポンス用モデル"""
    id: str
    name: str
    access_key: str
    created_at: datetime

class ChatRequest(BaseModel):
    """AIチャットリクエスト用モデル"""
    question: str
    family_access_key: str

class ChatResponse(BaseModel):
    """AIチャットレスポンス用モデル"""
    response: str
    timestamp: datetime

class SuggestionsResponse(BaseModel):
    """AI提案レスポンス用モデル"""
    suggestions: List[str]
    timestamp: datetime

# Gemini API関数
def classify_text_with_gemini(text):
    """Gemini APIを使用してテキストを分類する"""
    try:
        prompt = f"""
以下のテキストを家族のログとして分析し、適切なカテゴリに分類してください。
また、要約とキーワードも抽出してください。

テキスト: "{text}"

分類カテゴリ:
- schedule: 予定・イベント（運動会、病院、学校行事など）
- emotion: 子どもの様子・感情（機嫌、体調、行動など）
- shopping: 買い物リスト（食材、日用品など）
- todo: 家族のやること（手続き、申請、タスクなど）
- memo: 雑談・メモ（その他、日常の出来事など）

以下のJSON形式で回答してください:
{{
    "category": "分類したカテゴリ名",
    "confidence_score": 0.0-1.0の信頼度,
    "summary": "30文字以内の要約",
    "keywords": ["キーワード1", "キーワード2", "キーワード3"],
    "reasoning": "分類の理由"
}}
        """
        
        response = genai.generate_text(prompt=prompt, model='models/text-bison-001')
        result_text = response.result if response.result else ""
        
        # JSONの抽出を試行
        try:
            json_match = re.search(r'\{.*?\}', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                # 必要なフィールドの検証
                required_fields = ['category', 'confidence_score', 'summary', 'keywords', 'reasoning']
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Missing required field: {field}")
                
                return result
            else:
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            return fallback_classify_text(text)
            
    except Exception as e:
        return fallback_classify_text(text)

def fallback_classify_text(text):
    """Gemini APIが使用できない場合のフォールバック分類"""
    if "買い物" in text or "買う" in text or "スーパー" in text or "購入" in text:
        return {
            "category": "shopping",
            "confidence_score": 0.9,
            "summary": f"買い物: {text[:20]}...",
            "keywords": ["買い物", "スーパー", "購入"],
            "reasoning": "買い物関連のキーワードが含まれているため"
        }
    elif "運動会" in text or "学校" in text or "病院" in text or "予定" in text:
        return {
            "category": "schedule",
            "confidence_score": 0.8,
            "summary": f"予定: {text[:20]}...",
            "keywords": ["予定", "イベント", "スケジュール"],
            "reasoning": "予定やイベントに関連するキーワードが含まれているため"
        }
    elif "子ども" in text or "太郎" in text or "機嫌" in text or "泣く" in text or "笑う" in text:
        return {
            "category": "emotion",
            "confidence_score": 0.7,
            "summary": f"子どもの様子: {text[:20]}...",
            "keywords": ["子ども", "様子", "感情"],
            "reasoning": "子どもの状態に関するキーワードが含まれているため"
        }
    elif "やる" in text or "申請" in text or "手続き" in text or "タスク" in text or "しなければ" in text:
        return {
            "category": "todo",
            "confidence_score": 0.6,
            "summary": f"ToDo: {text[:20]}...",
            "keywords": ["やること", "タスク", "手続き"],
            "reasoning": "やるべきことに関するキーワードが含まれているため"
        }
    else:
        return {
            "category": "memo",
            "confidence_score": 0.5,
            "summary": f"メモ: {text[:20]}...",
            "keywords": ["メモ", "雑談", "日常"],
            "reasoning": "特定のカテゴリに該当しないため"
        }

def get_ai_response_with_gemini(question, logs):
    """Gemini APIを使用してAI回答を生成"""
    try:
        # ログの要約を作成
        log_summary = create_log_summary(logs)
        
        prompt = f"""
あなたは家族のAIコンシェルジュです。過去のログを参考にして、家族の質問に答えてください。

過去のログ:
{log_summary}

質問: {question}

以下の点を考慮して回答してください:
1. 過去のログから傾向を読み取る
2. 家族の状況を理解して適切な提案をする
3. 温かみのある、親しみやすい口調で回答する
4. 具体的で実践的なアドバイスを提供する
5. 200文字以内で回答する

回答:
        """
        
        response = genai.generate_text(prompt=prompt, model='models/text-bison-001')
        return response.result if response.result else ""
        
    except Exception as e:
        return fallback_get_ai_response(question, logs)

def create_log_summary(logs):
    """ログの要約を作成"""
    if not logs:
        return "過去のログはありません。"
    
    # 最新の10件のログを要約
    recent_logs = logs[:10]
    summary_parts = []
    
    for log in recent_logs:
        date = log.get('date', '')
        category = log.get('category', '')
        summary = log.get('summary', '')
        summary_parts.append(f"[{date}][{category}] {summary}")
    
    return "\n".join(summary_parts)

def fallback_get_ai_response(question, logs):
    """Gemini APIが使用できない場合のフォールバック回答"""
    if len(logs) == 0:
        return "まだログが記録されていませんが、どのようなことでもお気軽にお聞かせください。家族の日常を記録していくことで、より良いアドバイスができるようになります。"
    
    # 質問内容に基づく回答
    if "ストレス" in question or "疲れ" in question:
        return "最近のログを拝見すると、お忙しそうですね。家族でゆっくりと過ごす時間を作ってみてはいかがでしょうか。"
    elif "週末" in question or "過ごす" in question:
        return "週末は家族の絆を深める素晴らしい機会ですね。これまでのログを見ると、お子さんとの時間を大切にされているようです。"
    elif "子ども" in question or "子供" in question:
        return "お子さんの成長を記録されていて素晴らしいですね。子どもたちの変化や成長を見守り続けることが大切です。"
    else:
        return "家族の日常を大切に記録されていて素晴らしいですね。何かお困りのことがあれば、いつでもお聞かせください。"

def get_suggestions_with_gemini(logs):
    """Gemini APIを使用してAI提案を生成"""
    try:
        log_summary = create_log_summary(logs)
        
        prompt = f"""
以下の家族のログを分析して、3つの有用な提案をしてください。

過去のログ:
{log_summary}

以下の形式で3つの提案を出してください:
1. [提案1]
2. [提案2]
3. [提案3]

提案の内容:
- 家族の健康や幸福につながる提案
- 実践しやすい具体的な内容
- ログから読み取れる傾向に基づく提案
- 各提案は50文字以内で簡潔に
        """
        
        response = genai.generate_text(prompt=prompt, model='models/text-bison-001')
        suggestions_text = response.text
        
        # 提案を抽出
        suggestions = []
        for line in suggestions_text.split('\n'):
            if line.strip() and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                suggestion = line.split('.', 1)[1].strip()
                suggestions.append(suggestion)
        
        return suggestions[:3] if suggestions else fallback_get_suggestions(logs)
        
    except Exception as e:
        return fallback_get_suggestions(logs)

def fallback_get_suggestions(logs):
    """Gemini APIが使用できない場合のフォールバック提案"""
    if len(logs) == 0:
        return [
            "家族の日常を記録して、素敵な思い出を残しましょう",
            "子どもたちとの時間を大切にして、コミュニケーションを増やしましょう",
            "家族の健康管理に気をつけて、バランスの良い食事を心がけましょう"
        ]
    
    suggestions = []
    
    # 感情ログが多い場合
    emotion_logs = [log for log in logs if log.get('category') == 'emotion']
    if len(emotion_logs) > 0:
        suggestions.append("お子さんの感情の変化を記録されていますね。家族で話し合う時間を作ってみましょう")
    
    # 買い物ログが多い場合
    shopping_logs = [log for log in logs if log.get('category') == 'shopping']
    if len(shopping_logs) > 0:
        suggestions.append("買い物リストを効率的に管理されていますね。週1回のまとめ買いを検討してみてはいかがでしょうか")
    
    # 基本的な提案を追加
    if len(suggestions) < 3:
        default_suggestions = [
            "家族でゆっくりと過ごす時間を作ってみませんか？",
            "子どもたちとの会話を増やしてみるのはいかがでしょうか？",
            "家族の健康管理に気をつけましょう"
        ]
        suggestions.extend(default_suggestions)
    
    return suggestions[:3]

# API エンドポイント
@app.post("/api/families", response_model=FamilyResponse)
async def create_family(family: FamilyCreate):
    """家族を作成し、アクセスキーを発行"""
    try:
        family_id = str(uuid.uuid4())
        access_key = str(uuid.uuid4())
        
        if supabase:
            result = supabase.table("families").insert({
                "name": family.name,
                "access_key": access_key
            }).execute()
            
            if result.data:
                data = result.data[0]
                return FamilyResponse(
                    id=data["id"],
                    name=data["name"],
                    access_key=data["access_key"],
                    created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
                )
            else:
                raise HTTPException(status_code=500, detail="Family creation failed")
        else:
            # メモリベースのフォールバック
            family_data = {
                "id": family_id,
                "name": family.name,
                "access_key": access_key,
                "created_at": datetime.now()
            }
            
            test_families[access_key] = family_data
            
            return FamilyResponse(
                id=family_id,
                name=family.name,
                access_key=access_key,
                created_at=datetime.now()
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating family: {str(e)}")

@app.post("/api/logs", response_model=LogEntryResponse)
async def create_log_entry(log_entry: LogEntryCreate):
    """
    ログエントリを作成
    1. Gemini APIでテキストを分類
    2. データベースに保存
    3. 結果を返す
    """
    try:
        # 家族の存在確認
        if supabase:
            family_result = supabase.table("families").select("id").eq("access_key", log_entry.family_access_key).execute()
            if not family_result.data:
                raise HTTPException(status_code=404, detail="Family not found")
            
            family_id = family_result.data[0]["id"]
        else:
            # メモリベースのフォールバック
            if log_entry.family_access_key not in test_families:
                raise HTTPException(status_code=404, detail="Family not found")
            family_id = test_families[log_entry.family_access_key]["id"]
        
        # Gemini APIでテキストを分類
        if GEMINI_API_KEY:
            classification = classify_text_with_gemini(log_entry.text)
        else:
            classification = fallback_classify_text(log_entry.text)
        
        # エントリ日付の設定
        entry_date = log_entry.entry_date or date.today()
        
        # ログエントリをデータベースに保存
        log_id = str(uuid.uuid4())
        log_data = {
            "id": log_id,
            "original_text": log_entry.text,
            "category": classification["category"],
            "summary": classification["summary"],
            "date": entry_date.isoformat(),
            "keywords": classification["keywords"],
            "confidence_score": classification["confidence_score"],
            "created_at": datetime.now().isoformat()
        }
        
        if supabase:
            # Supabaseに保存
            log_result = supabase.table("log_entries").insert({
                "family_id": family_id,
                "original_text": log_entry.text,
                "category": classification["category"],
                "summary": classification["summary"],
                "date": entry_date.isoformat()
            }).execute()
            
            if not log_result.data:
                raise HTTPException(status_code=500, detail="Log entry creation failed")
            
            log_id = log_result.data[0]["id"]
            
            # 分類詳細を保存
            classification_data = {
                "log_entry_id": log_id,
                "confidence_score": classification["confidence_score"],
                "keywords": classification["keywords"],
                "ai_reasoning": classification["reasoning"]
            }
            
            supabase.table("classification_details").insert(classification_data).execute()
            
            created_at = datetime.fromisoformat(log_result.data[0]["created_at"].replace("Z", "+00:00"))
        else:
            # メモリベースのフォールバック
            if log_entry.family_access_key not in test_log_entries:
                test_log_entries[log_entry.family_access_key] = []
            
            test_log_entries[log_entry.family_access_key].append(log_data)
            created_at = datetime.now()
        
        # レスポンスを作成
        return LogEntryResponse(
            id=log_id,
            original_text=log_entry.text,
            category=classification["category"],
            summary=classification["summary"],
            date=entry_date,
            keywords=classification["keywords"],
            confidence_score=classification["confidence_score"],
            created_at=created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating log entry: {str(e)}")

@app.get("/api/logs/{family_access_key}", response_model=List[LogEntryResponse])
async def get_log_entries(family_access_key: str, date_filter: Optional[str] = None):
    """
    指定された家族のログエントリを取得
    date_filterがある場合は特定の日付のみ返す
    """
    try:
        # 家族の存在確認
        if supabase:
            family_result = supabase.table("families").select("id").eq("access_key", family_access_key).execute()
            if not family_result.data:
                raise HTTPException(status_code=404, detail="Family not found")
            
            family_id = family_result.data[0]["id"]
            
            # ログエントリを取得
            query = supabase.table("log_entries").select("*, classification_details(*)").eq("family_id", family_id)
            
            if date_filter:
                query = query.eq("date", date_filter)
            
            result = query.order("created_at", desc=True).execute()
            
            # レスポンスを作成
            log_entries = []
            for data in result.data:
                classification_detail = data.get("classification_details", [{}])[0] if data.get("classification_details") else {}
                
                log_entries.append(LogEntryResponse(
                    id=data["id"],
                    original_text=data["original_text"],
                    category=data["category"],
                    summary=data["summary"],
                    date=datetime.fromisoformat(data["date"]).date(),
                    keywords=classification_detail.get("keywords", []),
                    confidence_score=classification_detail.get("confidence_score", 0.0),
                    created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
                ))
            
            return log_entries
        else:
            # メモリベースのフォールバック
            if family_access_key not in test_families:
                raise HTTPException(status_code=404, detail="Family not found")
            
            entries = test_log_entries.get(family_access_key, [])
            
            if date_filter:
                entries = [entry for entry in entries if entry["date"] == date_filter]
            
            # 作成日時の降順でソート
            entries.sort(key=lambda x: x["created_at"], reverse=True)
            
            log_entries = []
            for entry in entries:
                log_entries.append(LogEntryResponse(
                    id=entry["id"],
                    original_text=entry["original_text"],
                    category=entry["category"],
                    summary=entry["summary"],
                    date=datetime.fromisoformat(entry["date"]).date(),
                    keywords=entry["keywords"],
                    confidence_score=entry["confidence_score"],
                    created_at=datetime.fromisoformat(entry["created_at"])
                ))
            
            return log_entries
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving log entries: {str(e)}")

@app.get("/api/categories")
async def get_categories():
    """利用可能なカテゴリ一覧を取得"""
    try:
        if supabase:
            result = supabase.table("categories").select("*").execute()
            return result.data
        else:
            # メモリベースのフォールバック
            return test_categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")

@app.post("/api/ai/chat", response_model=ChatResponse)
async def ai_chat(chat_request: ChatRequest):
    """AIチャット機能"""
    try:
        # 家族の存在確認
        if supabase:
            family_result = supabase.table("families").select("id").eq("access_key", chat_request.family_access_key).execute()
            if not family_result.data:
                raise HTTPException(status_code=404, detail="Family not found")
        else:
            # メモリベースのフォールバック
            if chat_request.family_access_key not in test_families:
                raise HTTPException(status_code=404, detail="Family not found")
        
        # ログデータを取得
        if supabase:
            # Supabaseから取得（実装略）
            logs = []
        else:
            logs = test_log_entries.get(chat_request.family_access_key, [])
        
        # AIからの回答を生成
        if GEMINI_API_KEY:
            response = get_ai_response_with_gemini(chat_request.question, logs)
        else:
            response = fallback_get_ai_response(chat_request.question, logs)
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in AI chat: {str(e)}")

@app.get("/api/ai/suggestions/{family_access_key}", response_model=SuggestionsResponse)
async def ai_suggestions(family_access_key: str):
    """AIからの提案を取得"""
    try:
        # 家族の存在確認
        if supabase:
            family_result = supabase.table("families").select("id").eq("access_key", family_access_key).execute()
            if not family_result.data:
                raise HTTPException(status_code=404, detail="Family not found")
        else:
            # メモリベースのフォールバック
            if family_access_key not in test_families:
                raise HTTPException(status_code=404, detail="Family not found")
        
        # ログデータを取得
        if supabase:
            # Supabaseから取得（実装略）
            logs = []
        else:
            logs = test_log_entries.get(family_access_key, [])
        
        # AIからの提案を生成
        if GEMINI_API_KEY:
            suggestions = get_suggestions_with_gemini(logs)
        else:
            suggestions = fallback_get_suggestions(logs)
        
        return SuggestionsResponse(
            suggestions=suggestions,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in AI suggestions: {str(e)}")

@app.get("/")
async def root():
    """ヘルスチェック"""
    return {"message": "KazokuLog API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)