"""
Claude APIとの連携処理
テキスト分類・要約のためのサービス
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import anthropic
from pydantic import BaseModel

class ClassificationResult(BaseModel):
    """分類結果のデータモデル"""
    category: str
    confidence_score: float
    summary: str
    keywords: List[str]
    reasoning: str

class ClaudeService:
    """Claude APIサービス"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-haiku-20240307"  # 高速で安価なモデル
    
    def classify_text(self, text: str) -> ClassificationResult:
        """
        テキストを分類・要約する
        
        Args:
            text: 分類対象のテキスト
            
        Returns:
            ClassificationResult: 分類結果
        """
        try:
            prompt = self._create_classification_prompt(text)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            return self._parse_classification_response(response_text)
            
        except Exception as e:
            # エラー時のフォールバック
            return ClassificationResult(
                category="memo",
                confidence_score=0.0,
                summary=text[:100] + "..." if len(text) > 100 else text,
                keywords=[],
                reasoning=f"分類エラー: {str(e)}"
            )
    
    def _create_classification_prompt(self, text: str) -> str:
        """分類用のプロンプトを作成"""
        return f"""
あなたは家族のログを整理する専門家です。以下のテキストを分析し、適切なカテゴリに分類してください。

テキスト: {text}

利用可能なカテゴリ:
- schedule: 予定・イベント（病院の予約、学校行事、家族の予定など）
- emotion: 子どもの様子（感情、体調、発達、行動など）
- shopping: 買い物リスト（食材、日用品、子供用品など）
- todo: 家族のToDo（やるべきこと、タスク、手続きなど）
- memo: 雑談・メモ（日常の気づき、思いついたことなど）

以下のJSON形式で回答してください:
{{
    "category": "カテゴリ名",
    "confidence_score": 0.8,
    "summary": "簡潔な要約（50文字以内）",
    "keywords": ["キーワード1", "キーワード2"],
    "reasoning": "分類理由"
}}

注意事項:
- confidence_scoreは0.0-1.0の範囲で信頼度を示す
- summaryは要点を簡潔にまとめる
- keywordsは重要な単語を3つまで抽出
- reasoningは分類の根拠を説明
"""
    
    def _parse_classification_response(self, response: str) -> ClassificationResult:
        """Claude APIのレスポンスを解析"""
        try:
            # JSON部分を抽出
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            json_str = response[start_idx:end_idx]
            
            data = json.loads(json_str)
            
            return ClassificationResult(
                category=data.get('category', 'memo'),
                confidence_score=float(data.get('confidence_score', 0.5)),
                summary=data.get('summary', ''),
                keywords=data.get('keywords', []),
                reasoning=data.get('reasoning', '')
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # パース失敗時のフォールバック
            return ClassificationResult(
                category="memo",
                confidence_score=0.0,
                summary="分類できませんでした",
                keywords=[],
                reasoning=f"レスポンス解析エラー: {str(e)}"
            )

# 使用例
if __name__ == "__main__":
    # 環境変数からAPIキーを取得
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    service = ClaudeService(api_key)
    
    # テスト用のテキスト
    test_texts = [
        "明日は太郎の小学校の運動会です。お弁当を作らないと。",
        "牛乳、パン、卵、トマトを買う",
        "太郎が今日は機嫌が悪くて泣いてばかりいた。熱はないけど心配。",
        "来週までに子供の医療費助成の申請書を出す",
        "今日は良い天気だった。散歩が気持ちよかった。"
    ]
    
    for text in test_texts:
        result = service.classify_text(text)
        print(f"テキスト: {text}")
        print(f"カテゴリ: {result.category}")
        print(f"要約: {result.summary}")
        print(f"信頼度: {result.confidence_score}")
        print(f"キーワード: {result.keywords}")
        print(f"理由: {result.reasoning}")
        print("-" * 50)