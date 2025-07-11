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
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000');

  useEffect(() => {
    // 音声認識サポートチェック
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setSpeechSupported(true);
    }
    
    // 音声合成サポートチェック  
    if ('speechSynthesis' in window) {
      setVoiceEnabled(true);
    }
  }, []);

  const sendVoiceMessage = async (message: string) => {
    if (!message.trim() || !familyAccessKey) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
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
          question: message,
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
        
        // 音声読み上げ
        if (voiceEnabled) {
          speakText(data.response);
        }
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
        
        // 音声読み上げ
        if (voiceEnabled) {
          speakText(data.response);
        }
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

  // 音声認識機能
  const startSpeechRecognition = () => {
    if (!speechSupported || isRecording) return;

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const newRecognition = new SpeechRecognition();
    
    newRecognition.lang = 'ja-JP';
    newRecognition.continuous = false;
    newRecognition.interimResults = false;

    newRecognition.onstart = () => {
      setIsRecording(true);
    };

    newRecognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInputText(transcript);
      setIsRecording(false);
      
      // 音声入力後に自動送信
      setTimeout(() => {
        if (transcript.trim()) {
          sendVoiceMessage(transcript);
        }
      }, 500);
    };

    newRecognition.onerror = (event: any) => {
      console.error('音声認識エラー:', event.error);
      setIsRecording(false);
    };

    newRecognition.onend = () => {
      setIsRecording(false);
    };

    setRecognition(newRecognition);
    newRecognition.start();
  };

  const stopSpeechRecognition = () => {
    if (recognition && isRecording) {
      recognition.stop();
      setIsRecording(false);
    }
  };

  // 音声合成機能
  const speakText = (text: string) => {
    if (!voiceEnabled || !text) return;

    // 既存の音声を停止
    speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ja-JP';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 0.8;

    // 日本語の声を優先的に選択
    const voices = speechSynthesis.getVoices();
    const japaneseVoice = voices.find(voice => voice.lang.includes('ja'));
    if (japaneseVoice) {
      utterance.voice = japaneseVoice;
    }

    speechSynthesis.speak(utterance);
  };

  const stopSpeech = () => {
    speechSynthesis.cancel();
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
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-orange-100">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-orange-800 flex items-center">
            💬 AIチャット
          </h3>
        </div>
        <div className="text-center py-8 text-orange-500">
          <div className="text-4xl mb-3">🤖</div>
          <p className="text-sm">家族を設定するとAIチャットが利用できます</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-orange-100">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-orange-800 flex items-center">
          🤖 AIコンシェルジュ
          {voiceEnabled && (
            <span className="ml-2 text-xs bg-green-100 text-green-600 px-2 py-1 rounded-full">
              🔊 音声対応
            </span>
          )}
        </h2>
        <div className="flex items-center gap-2">
          {voiceEnabled && (
            <button
              onClick={stopSpeech}
              className="text-sm px-2 py-1 bg-red-100 text-red-600 hover:bg-red-200 rounded-lg transition-colors"
              title="音声読み上げを停止"
            >
              🔇
            </button>
          )}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="px-4 py-2 bg-orange-200 text-orange-800 rounded-lg hover:bg-orange-300 transition-all text-sm"
          >
            {isOpen ? '閉じる' : 'チャット'}
          </button>
        </div>
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
          <div className="space-y-2">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="AIに質問してみてください..."
                  className="w-full px-4 py-2 border border-orange-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400 bg-white/80"
                  disabled={isLoading}
                />
                {speechSupported && (
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                    {!isRecording ? (
                      <button
                        type="button"
                        onClick={startSpeechRecognition}
                        className="p-1 text-orange-600 hover:text-orange-800 transition-colors"
                        title="音声入力を開始"
                      >
                        🎤
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={stopSpeechRecognition}
                        className="p-1 text-red-600 hover:text-red-800 transition-colors animate-pulse"
                        title="音声入力を停止"
                      >
                        ⏹️
                      </button>
                    )}
                  </div>
                )}
              </div>
              <button
                onClick={sendMessage}
                disabled={!inputText.trim() || isLoading}
                className="px-4 py-2 bg-gradient-to-r from-orange-400 to-rose-400 text-white rounded-xl hover:from-orange-500 hover:to-rose-500 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all"
              >
                送信
              </button>
            </div>
            
            {/* 音声機能の説明 */}
            {speechSupported && voiceEnabled && (
              <div className="text-xs text-green-600 bg-green-50 px-3 py-1 rounded-lg">
                🎙️ 音声入力: マイクボタンを押して話してください | 🔊 AI回答は自動で読み上げます
              </div>
            )}
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