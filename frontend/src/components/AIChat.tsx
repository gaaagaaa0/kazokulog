"use client";

import React, { useState, useEffect } from 'react';

interface AIChatProps {
  familyAccessKey: string;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: string;
}

const AIChat: React.FC<AIChatProps> = ({ familyAccessKey }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000');

  const sendMessage = async () => {
    if (!inputText.trim() || !familyAccessKey) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputText,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: inputText,
          family_access_key: familyAccessKey
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: data.response,
          timestamp: data.timestamp
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error('AI response failed');
      }
    } catch (error) {
      console.error('AI chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: '申し訳ございません。エラーが発生しました。しばらく時間をおいて再度お試しください。',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString('ja-JP', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '';
    }
  };

  if (!familyAccessKey) {
    return null;
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-orange-100">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-orange-800 flex items-center">
          🤖 AIコンシェルジュ
        </h2>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="px-4 py-2 bg-orange-200 text-orange-800 rounded-lg hover:bg-orange-300 transition-all text-sm"
        >
          {isOpen ? '閉じる' : 'チャット'}
        </button>
      </div>

      {isOpen && (
        <div className="space-y-4">
          {/* チャット履歴 */}
          <div className="h-64 overflow-y-auto border border-orange-200 rounded-xl p-4 bg-white/50">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <div className="text-4xl mb-2">💬</div>
                <p>AIコンシェルジュに何でも聞いてみてください</p>
                <p className="text-sm mt-1">家族のログを参考にアドバイスします</p>
              </div>
            ) : (
              <div className="space-y-3">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs px-4 py-2 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-gradient-to-r from-orange-400 to-rose-400 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <div className="text-sm">{message.content}</div>
                      <div className={`text-xs mt-1 opacity-70 ${
                        message.type === 'user' ? 'text-white' : 'text-gray-500'
                      }`}>
                        {formatTime(message.timestamp)}
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 px-4 py-2 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* 入力エリア */}
          <div className="flex gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="AIに質問してみてください..."
              className="flex-1 px-4 py-2 border border-orange-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400 bg-white/80"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!inputText.trim() || isLoading}
              className="px-4 py-2 bg-gradient-to-r from-orange-400 to-rose-400 text-white rounded-xl hover:from-orange-500 hover:to-rose-500 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all"
            >
              送信
            </button>
          </div>

          {/* 使用例 */}
          <div className="text-xs text-gray-600 bg-gray-50 px-3 py-2 rounded-lg">
            💡 質問例: 「最近ストレスが溜まっています」「週末どう過ごすのが良い？」「子どもの様子で気になることがあります」
          </div>
        </div>
      )}
    </div>
  );
};

export default AIChat;