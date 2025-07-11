# -*- coding: utf-8 -*-
"""
KazokuLog Flask バックエンド - テスト用
"""
import uuid
import os
from datetime import datetime, date
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import json

# 環境変数を読み込み
load_dotenv()

# Gemini APIの設定
gemini_api_key = os.getenv('GEMINI_API_KEY')
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    print("🤖 Gemini API連携が有効になりました")

app = Flask(__name__)
CORS(app)

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

def classify_text_with_gemini(text):
    """Gemini APIを使用してテキストを分類する"""
    try:
        prompt = """
以下のテキストを家族のログとして分析し、適切なカテゴリに分類してください。
また、要約とキーワードも抽出してください。

テキスト: "{}"

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
        """.format(text)
        
        response = gemini_model.generate_content(prompt)
        result_text = response.text
        
        # JSONの抽出を試行
        try:
            import re
            json_match = re.search(r'\{.*?\}', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                # 必要なフィールドの検証
                required_fields = ['category', 'confidence_score', 'summary', 'keywords', 'reasoning']
                for field in required_fields:
                    if field not in result:
                        raise ValueError("Missing required field: {}".format(field))
                
                return result
            else:
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            print("JSON parsing error: {}".format(e))
            return fallback_classify_text(text)
            
    except Exception as e:
        print("Gemini API error: {}".format(e))
        return fallback_classify_text(text)

def fallback_classify_text(text):
    """Gemini APIが使用できない場合のフォールバック分類"""
    if "買い物" in text or "買う" in text or "スーパー" in text or "購入" in text:
        return {
            "category": "shopping",
            "confidence_score": 0.9,
            "summary": "買い物: {}...".format(text[:20]),
            "keywords": ["買い物", "スーパー", "購入"],
            "reasoning": "買い物関連のキーワードが含まれているため"
        }
    elif "運動会" in text or "学校" in text or "病院" in text or "予定" in text:
        return {
            "category": "schedule",
            "confidence_score": 0.8,
            "summary": "予定: {}...".format(text[:20]),
            "keywords": ["予定", "イベント", "スケジュール"],
            "reasoning": "予定やイベントに関連するキーワードが含まれているため"
        }
    elif "子ども" in text or "太郎" in text or "機嫌" in text or "泣く" in text or "笑う" in text:
        return {
            "category": "emotion",
            "confidence_score": 0.7,
            "summary": "子どもの様子: {}...".format(text[:20]),
            "keywords": ["子ども", "様子", "感情"],
            "reasoning": "子どもの状態に関するキーワードが含まれているため"
        }
    elif "やる" in text or "申請" in text or "手続き" in text or "タスク" in text or "しなければ" in text:
        return {
            "category": "todo",
            "confidence_score": 0.6,
            "summary": "ToDo: {}...".format(text[:20]),
            "keywords": ["やること", "タスク", "手続き"],
            "reasoning": "やるべきことに関するキーワードが含まれているため"
        }
    else:
        return {
            "category": "memo",
            "confidence_score": 0.5,
            "summary": "メモ: {}...".format(text[:20]),
            "keywords": ["メモ", "雑談", "日常"],
            "reasoning": "特定のカテゴリに該当しないため"
        }

def get_ai_response_with_gemini(question, logs):
    """Gemini APIを使用してAI回答を生成"""
    try:
        # ログの要約を作成
        log_summary = create_log_summary(logs)
        
        prompt = """
あなたは家族のAIコンシェルジュです。過去のログを参考にして、家族の質問に答えてください。

過去のログ:
{}

質問: {}

以下の点を考慮して回答してください:
1. 過去のログから傾向を読み取る
2. 家族の状況を理解して適切な提案をする
3. 温かみのある、親しみやすい口調で回答する
4. 具体的で実践的なアドバイスを提供する
5. 200文字以内で回答する

回答:
        """.format(log_summary, question)
        
        response = gemini_model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print("Gemini AI response error: {}".format(e))
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
        summary_parts.append("[{}][{}] {}".format(date, category, summary))
    
    return "\n".join(summary_parts)

def fallback_get_ai_response(question, logs):
    """Gemini APIが使用できない場合のフォールバック回答"""
    # ログ数に基づく分析
    if len(logs) == 0:
        return "まだログが記録されていませんが、どのようなことでもお気軽にお聞かせください。家族の日常を記録していくことで、より良いアドバイスができるようになります。"
    
    # 質問内容に基づく回答
    if "ストレス" in question or "疲れ" in question:
        return "最近のログを拝見すると、お忙しそうですね。家族でゆっくりと過ごす時間を作ってみてはいかがでしょうか。週末に公園でのんびり過ごしたり、みんなで映画を見たりするのもおすすめです。"
    elif "週末" in question or "過ごす" in question:
        return "週末は家族の絆を深める素晴らしい機会ですね。これまでのログを見ると、お子さんとの時間を大切にされているようです。天気が良ければ外で遊んだり、雨の日は家でゲームや読書を楽しむのはいかがでしょうか。"
    elif "子ども" in question or "子供" in question:
        return "お子さんの成長を記録されていて素晴らしいですね。子どもたちの変化や成長を見守り続けることが大切です。何か心配事があれば、いつでも相談してください。"
    elif "買い物" in question or "食事" in question:
        return "家族の食事管理、お疲れ様です。バランスの良い食事と、時には家族みんなで料理を作ることも楽しい思い出になりますよ。"
    else:
        return "家族の日常を大切に記録されていて素晴らしいですね。何かお困りのことがあれば、いつでもお聞かせください。家族の幸せをサポートさせていただきます。"

def get_suggestions_with_gemini(logs):
    """Gemini APIを使用してAI提案を生成"""
    try:
        log_summary = create_log_summary(logs)
        
        prompt = """
以下の家族のログを分析して、3つの有用な提案をしてください。

過去のログ:
{}

以下の形式で3つの提案を出してください:
1. [提案1]
2. [提案2]
3. [提案3]

提案の内容:
- 家族の健康や幸福につながる提案
- 実践しやすい具体的な内容
- ログから読み取れる傾向に基づく提案
- 各提案は50文字以内で簡潔に
        """.format(log_summary)
        
        response = gemini_model.generate_content(prompt)
        suggestions_text = response.text
        
        # 提案を抽出
        suggestions = []
        for line in suggestions_text.split('\n'):
            if line.strip() and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                suggestion = line.split('.', 1)[1].strip()
                suggestions.append(suggestion)
        
        return suggestions[:3] if suggestions else fallback_get_suggestions(logs)
        
    except Exception as e:
        print("Gemini suggestions error: {}".format(e))
        return fallback_get_suggestions(logs)

def fallback_get_suggestions(logs):
    """Gemini APIが使用できない場合のフォールバック提案"""
    if len(logs) == 0:
        return [
            "家族の日常を記録して、素敵な思い出を残しましょう",
            "子どもたちとの時間を大切にして、コミュニケーションを増やしましょう",
            "家族の健康管理に気をつけて、バランスの良い食事を心がけましょう"
        ]
    
    # ログの内容に基づく提案
    suggestions = []
    
    # 感情ログが多い場合
    emotion_logs = [log for log in logs if log.get('category') == 'emotion']
    if len(emotion_logs) > 0:
        suggestions.append("お子さんの感情の変化を記録されていますね。家族で話し合う時間を作ってみましょう")
    
    # 買い物ログが多い場合
    shopping_logs = [log for log in logs if log.get('category') == 'shopping']
    if len(shopping_logs) > 0:
        suggestions.append("買い物リストを効率的に管理されていますね。週1回のまとめ買いを検討してみてはいかがでしょうか")
    
    # スケジュールログが多い場合
    schedule_logs = [log for log in logs if log.get('category') == 'schedule']
    if len(schedule_logs) > 0:
        suggestions.append("予定管理がしっかりされていますね。家族カレンダーを活用してみましょう")
    
    # 基本的な提案を追加
    if len(suggestions) < 3:
        default_suggestions = [
            "家族でゆっくりと過ごす時間を作ってみませんか？",
            "子どもたちとの会話を増やしてみるのはいかがでしょうか？",
            "家族の健康管理に気をつけましょう"
        ]
        suggestions.extend(default_suggestions)
    
    return suggestions[:3]

@app.route('/')
def root():
    """ヘルスチェック"""
    return jsonify({"message": "KazokuLog API is running in TEST MODE"})

@app.route('/api/families', methods=['POST'])
def create_family():
    """家族を作成し、アクセスキーを発行"""
    data = request.get_json()
    
    family_id = str(uuid.uuid4())
    access_key = str(uuid.uuid4())
    
    family_data = {
        "id": family_id,
        "name": data["name"],
        "access_key": access_key,
        "created_at": datetime.now().isoformat()
    }
    
    test_families[access_key] = family_data
    
    return jsonify(family_data)

@app.route('/api/logs', methods=['POST'])
def create_log_entry():
    """ログエントリを作成（テストモード）"""
    data = request.get_json()
    
    # 家族の存在確認
    if data["family_access_key"] not in test_families:
        return jsonify({"error": "Family not found"}), 404
    
    # Gemini APIを使用した分類
    if gemini_api_key:
        classification = classify_text_with_gemini(data["text"])
    else:
        classification = fallback_classify_text(data["text"])
    
    # エントリ日付の設定
    entry_date = data.get("entry_date", date.today().isoformat())
    
    # ログエントリを作成
    log_id = str(uuid.uuid4())
    log_data = {
        "id": log_id,
        "original_text": data["text"],
        "category": classification["category"],
        "summary": classification["summary"],
        "date": entry_date,
        "keywords": classification["keywords"],
        "confidence_score": classification["confidence_score"],
        "created_at": datetime.now().isoformat()
    }
    
    if data["family_access_key"] not in test_log_entries:
        test_log_entries[data["family_access_key"]] = []
    
    test_log_entries[data["family_access_key"]].append(log_data)
    
    return jsonify(log_data)

@app.route('/api/logs/<family_access_key>', methods=['GET'])
def get_log_entries(family_access_key):
    """指定された家族のログエントリを取得"""
    if family_access_key not in test_families:
        return jsonify({"error": "Family not found"}), 404
    
    entries = test_log_entries.get(family_access_key, [])
    
    date_filter = request.args.get('date_filter')
    if date_filter:
        entries = [entry for entry in entries if entry["date"] == date_filter]
    
    # 作成日時の降順でソート
    entries.sort(key=lambda x: x["created_at"], reverse=True)
    
    return jsonify(entries)

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """利用可能なカテゴリ一覧を取得"""
    return jsonify(test_categories)

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """AIチャット機能"""
    data = request.get_json()
    
    # 家族の存在確認
    if data["family_access_key"] not in test_families:
        return jsonify({"error": "Family not found"}), 404
    
    question = data["question"]
    logs = test_log_entries.get(data["family_access_key"], [])
    
    # AIからの回答を生成
    if gemini_api_key:
        response = get_ai_response_with_gemini(question, logs)
    else:
        response = fallback_get_ai_response(question, logs)
    
    return jsonify({
        "response": response,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/ai/suggestions/<family_access_key>', methods=['GET'])
def ai_suggestions(family_access_key):
    """AIからの提案を取得"""
    if family_access_key not in test_families:
        return jsonify({"error": "Family not found"}), 404
    
    logs = test_log_entries.get(family_access_key, [])
    if gemini_api_key:
        suggestions = get_suggestions_with_gemini(logs)
    else:
        suggestions = fallback_get_suggestions(logs)
    
    return jsonify({
        "suggestions": suggestions,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """テスト用エンドポイント"""
    return jsonify({
        "message": "Test endpoint working",
        "families_count": len(test_families),
        "log_entries_count": sum(len(entries) for entries in test_log_entries.values()),
        "categories_count": len(test_categories)
    })

if __name__ == '__main__':
    print("🚀 Starting KazokuLog API in TEST MODE")
    print("📝 Environment variables are NOT required in test mode")
    print("🌐 API will be available at: http://localhost:8000")
    print("🧪 Test endpoint: http://localhost:8000/test")
    
    app.run(host='0.0.0.0', port=8000, debug=True)