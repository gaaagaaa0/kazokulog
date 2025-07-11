"""
KazokuLog Gemini API Service
"""
import os
import json
from typing import Dict, List, Any
import google.generativeai as genai
from datetime import datetime

class GeminiService:
    def __init__(self):
        """Initialize Gemini API service"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def classify_text(self, text: str) -> Dict[str, Any]:
        """
        Classify text using Gemini API
        
        Args:
            text: The text to classify
            
        Returns:
            Dictionary containing classification results
        """
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
            
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # JSONの抽出を試行
            try:
                # レスポンスからJSONを抽出
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    result = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                    
                # 必要なフィールドの検証
                required_fields = ['category', 'confidence_score', 'summary', 'keywords', 'reasoning']
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Missing required field: {field}")
                
                return result
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"JSON parsing error: {e}")
                # フォールバック：基本的な分類
                return self._fallback_classification(text)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._fallback_classification(text)
    
    def _fallback_classification(self, text: str) -> Dict[str, Any]:
        """Fallback classification when Gemini API fails"""
        keywords = ["メモ", "雑談"]
        category = "memo"
        confidence = 0.3
        
        # 簡単なキーワードベースの分類
        if any(word in text for word in ["買い物", "買う", "スーパー", "購入"]):
            category = "shopping"
            keywords = ["買い物", "リスト"]
            confidence = 0.7
        elif any(word in text for word in ["運動会", "学校", "病院", "予定"]):
            category = "schedule"
            keywords = ["予定", "イベント"]
            confidence = 0.7
        elif any(word in text for word in ["子ども", "機嫌", "泣く", "笑う"]):
            category = "emotion"
            keywords = ["子ども", "様子"]
            confidence = 0.7
        elif any(word in text for word in ["やる", "申請", "手続き", "タスク"]):
            category = "todo"
            keywords = ["やること", "タスク"]
            confidence = 0.7
        
        return {
            "category": category,
            "confidence_score": confidence,
            "summary": f"{text[:20]}...",
            "keywords": keywords,
            "reasoning": "フォールバック分類"
        }
    
    def get_ai_response(self, question: str, logs: List[Dict[str, Any]]) -> str:
        """
        Get AI response based on question and past logs
        
        Args:
            question: User's question
            logs: Past log entries
            
        Returns:
            AI response string
        """
        try:
            # ログの要約を作成
            log_summary = self._create_log_summary(logs)
            
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

回答:
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"AI response error: {e}")
            return "申し訳ございません。現在AIからの回答を取得できません。しばらく時間をおいて再度お試しください。"
    
    def _create_log_summary(self, logs: List[Dict[str, Any]]) -> str:
        """Create a summary of logs for AI context"""
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
    
    def get_suggestions(self, logs: List[Dict[str, Any]]) -> List[str]:
        """
        Get suggestions based on recent logs
        
        Args:
            logs: Recent log entries
            
        Returns:
            List of suggestions
        """
        try:
            log_summary = self._create_log_summary(logs)
            
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
            """
            
            response = self.model.generate_content(prompt)
            suggestions_text = response.text
            
            # 提案を抽出
            suggestions = []
            for line in suggestions_text.split('\n'):
                if line.strip() and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                    suggestion = line.split('.', 1)[1].strip()
                    suggestions.append(suggestion)
            
            return suggestions[:3]  # 最大3つまで
            
        except Exception as e:
            print(f"Suggestions error: {e}")
            return [
                "家族でゆっくりと過ごす時間を作ってみませんか？",
                "子どもたちとの会話を増やしてみるのはいかがでしょうか？",
                "家族の健康管理に気をつけましょう。"
            ]