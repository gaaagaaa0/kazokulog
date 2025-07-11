"use client";

import React, { useState, useEffect } from 'react';

interface LogEntry {
  id: string;
  original_text: string;
  category: string;
  summary: string;
  date: string;
  keywords: string[];
  confidence_score: number;
  created_at: string;
}

interface AIFeedbackProps {
  logEntries: LogEntry[];
}

interface FeedbackInsight {
  type: 'positive' | 'neutral' | 'suggestion';
  title: string;
  message: string;
  icon: string;
}

const AIFeedback: React.FC<AIFeedbackProps> = ({ logEntries }) => {
  const [insights, setInsights] = useState<FeedbackInsight[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    generateInsights();
  }, [logEntries]);

  const generateInsights = () => {
    if (logEntries.length === 0) {
      setInsights([{
        type: 'neutral',
        title: '記録を始めましょう',
        message: 'ログを記録すると、AIが家族の様子を分析してフィードバックを提供します。',
        icon: '📝'
      }]);
      return;
    }

    const newInsights: FeedbackInsight[] = [];
    
    // 最近7日のログを分析
    const recentLogs = logEntries.slice(0, 7);
    const categoryCount = recentLogs.reduce((acc, log) => {
      acc[log.category] = (acc[log.category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // カテゴリ別の傾向分析
    const emotionLogs = recentLogs.filter(log => log.category === 'emotion');
    const scheduleLogs = recentLogs.filter(log => log.category === 'schedule');
    const shoppingLogs = recentLogs.filter(log => log.category === 'shopping');
    const todoLogs = recentLogs.filter(log => log.category === 'todo');

    // 感情ログの分析
    if (emotionLogs.length > 0) {
      const negativeKeywords = ['泣', '機嫌', '心配', '疲れ', '困', '怒'];
      const hasNegativeEmotion = emotionLogs.some(log => 
        negativeKeywords.some(keyword => log.original_text.includes(keyword))
      );
      
      if (hasNegativeEmotion) {
        newInsights.push({
          type: 'suggestion',
          title: '感情ケアの提案',
          message: '最近お子さんの感情に関する記録が見られます。週末に家族で散歩や公園遊びをしてみてはいかがでしょうか？',
          icon: '🌟'
        });
      } else {
        newInsights.push({
          type: 'positive',
          title: '家族の様子',
          message: 'お子さんの様子を丁寧に記録されていますね。継続的な観察が素晴らしいです！',
          icon: '👨‍👩‍👧‍👦'
        });
      }
    }

    // スケジュール管理の分析
    if (scheduleLogs.length >= 2) {
      newInsights.push({
        type: 'positive',
        title: 'スケジュール管理',
        message: '家族の予定をしっかりと管理されていますね。計画的な生活が素晴らしいです！',
        icon: '📅'
      });
    }

    // 買い物リストの分析
    if (shoppingLogs.length >= 2) {
      newInsights.push({
        type: 'suggestion',
        title: '買い物の最適化',
        message: '買い物リストを頻繁に記録されていますね。週1回まとめて買い物をすると時短になるかもしれません。',
        icon: '🛒'
      });
    }

    // ToDoの分析
    if (todoLogs.length >= 2) {
      newInsights.push({
        type: 'neutral',
        title: 'タスク管理',
        message: 'やることリストをしっかりと管理されていますね。完了したタスクも記録すると達成感が得られます。',
        icon: '✅'
      });
    }

    // 全体的な記録習慣の分析
    if (recentLogs.length >= 5) {
      newInsights.push({
        type: 'positive',
        title: '記録習慣',
        message: '継続的にログを記録されていて素晴らしいです！家族の成長記録として貴重な資料になりますね。',
        icon: '📝'
      });
    } else if (recentLogs.length === 0) {
      newInsights.push({
        type: 'suggestion',
        title: '記録を始めましょう',
        message: 'まずは今日の出来事を何か一つ記録してみませんか？小さなことでも大丈夫です。',
        icon: '🌱'
      });
    }

    setInsights(newInsights);
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'positive': return 'bg-green-100 border-green-200 text-green-800';
      case 'suggestion': return 'bg-blue-100 border-blue-200 text-blue-800';
      case 'neutral': return 'bg-orange-100 border-orange-200 text-orange-800';
      default: return 'bg-gray-100 border-gray-200 text-gray-800';
    }
  };

  if (insights.length === 0) {
    return null;
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-orange-100">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-orange-800 flex items-center">
          🤖 AIからのフィードバック
        </h2>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="px-4 py-2 bg-orange-200 text-orange-800 rounded-lg hover:bg-orange-300 transition-all text-sm"
        >
          {isOpen ? '閉じる' : '表示する'}
        </button>
      </div>

      {isOpen && (
        <div className="space-y-3">
          {insights.map((insight, index) => (
            <div
              key={index}
              className={`border rounded-xl p-4 ${getInsightColor(insight.type)}`}
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl flex-shrink-0">{insight.icon}</span>
                <div>
                  <h3 className="font-semibold mb-1">{insight.title}</h3>
                  <p className="text-sm leading-relaxed">{insight.message}</p>
                </div>
              </div>
            </div>
          ))}
          
          <div className="mt-4 p-3 bg-orange-50 rounded-lg text-sm text-orange-700">
            💡 このフィードバックは最近のログの傾向を分析して自動生成されています。
          </div>
        </div>
      )}
    </div>
  );
};

export default AIFeedback;