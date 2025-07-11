"use client";

import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { ja } from 'date-fns/locale';
import FamilySettings from '@/components/FamilySettings';
import AIFeedback from '@/components/AIFeedback';
import AIChat from '@/components/AIChat';
import AISuggestions from '@/components/AISuggestions';

// 型定義
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

interface Category {
  name: string;
  display_name: string;
  color: string;
  icon: string;
}

interface FamilyMember {
  id: string;
  name: string;
  age: number;
  relationship: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const KazokuLogApp: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [familyAccessKey, setFamilyAccessKey] = useState('');
  const [logEntries, setLogEntries] = useState<LogEntry[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(format(new Date(), 'yyyy-MM-dd'));
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([]);
  const [recognition, setRecognition] = useState<any>(null);

  // 音声認識のサポート確認
  const [speechSupported, setSpeechSupported] = useState(false);
  
  useEffect(() => {
    loadCategories();
    loadFamilyMembers();
    
    // 音声認識サポートチェック
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setSpeechSupported(true);
    }
    
    // ローカルストレージから家族アクセスキーを読み込み
    const savedAccessKey = localStorage.getItem('familyAccessKey');
    if (savedAccessKey) {
      setFamilyAccessKey(savedAccessKey);
      loadLogEntries(savedAccessKey);
    }

    // クリーンアップ：コンポーネントアンマウント時に音声認識を停止
    return () => {
      if (recognition) {
        recognition.stop();
      }
    };
  }, [recognition]);

  const loadCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/categories`);
      const data = await response.json();
      setCategories(data);
    } catch (err) {
      console.error('カテゴリ取得エラー:', err);
    }
  };

  const loadFamilyMembers = () => {
    const savedMembers = localStorage.getItem('familyMembers');
    if (savedMembers) {
      setFamilyMembers(JSON.parse(savedMembers));
    }
  };

  const updateFamilyMembers = (members: FamilyMember[]) => {
    setFamilyMembers(members);
    localStorage.setItem('familyMembers', JSON.stringify(members));
  };

  const loadLogEntries = async (accessKey: string) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/logs/${accessKey}?date_filter=${selectedDate}`);
      if (response.ok) {
        const data = await response.json();
        setLogEntries(data);
      } else {
        setError('ログの取得に失敗しました');
      }
    } catch (err) {
      setError('ログの取得中にエラーが発生しました');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || !familyAccessKey) return;

    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/api/logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          family_access_key: familyAccessKey,
          entry_date: selectedDate
        }),
      });

      if (response.ok) {
        const newEntry = await response.json();
        setLogEntries([newEntry, ...logEntries]);
        setInputText('');
        localStorage.setItem('familyAccessKey', familyAccessKey);
      } else {
        setError('ログの保存に失敗しました');
      }
    } catch (err) {
      setError('ログの保存中にエラーが発生しました');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const createFamily = async () => {
    try {
      const familyName = prompt('家族名を入力してください:');
      if (!familyName) return;

      const response = await fetch(`${API_BASE_URL}/api/families`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: familyName }),
      });

      if (response.ok) {
        const family = await response.json();
        setFamilyAccessKey(family.access_key);
        localStorage.setItem('familyAccessKey', family.access_key);
        alert(`家族「${family.name}」を作成しました。\nアクセスキー: ${family.access_key}`);
      } else {
        setError('家族の作成に失敗しました');
      }
    } catch (err) {
      setError('家族の作成中にエラーが発生しました');
      console.error(err);
    }
  };

  const getCategoryInfo = (categoryName: string) => {
    return categories.find(cat => cat.name === categoryName) || {
      name: categoryName,
      display_name: categoryName,
      color: '#6B7280',
      icon: 'file-text'
    };
  };

  const handleDateChange = (newDate: string) => {
    setSelectedDate(newDate);
    if (familyAccessKey) {
      loadLogEntries(familyAccessKey);
    }
  };

  // 音声認識機能
  const startSpeechRecognition = () => {
    if (!speechSupported || isRecording) return;

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const newRecognition = new SpeechRecognition();
    
    newRecognition.lang = 'ja-JP';
    newRecognition.continuous = true;  // 連続音声認識
    newRecognition.interimResults = true;  // 途中結果も表示

    newRecognition.onstart = () => {
      setIsRecording(true);
      setError(null);
    };

    newRecognition.onresult = (event: any) => {
      let finalTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        }
      }

      // 最終的な認識結果をテキストエリアに追加
      if (finalTranscript) {
        setInputText(prev => prev + finalTranscript);
      }
    };

    newRecognition.onerror = (event: any) => {
      console.error('音声認識エラー:', event.error);
      setError('音声認識でエラーが発生しました');
      setIsRecording(false);
    };

    newRecognition.onend = () => {
      // 手動停止でない場合は自動的に再開（連続認識）
      if (isRecording && recognition) {
        setTimeout(() => {
          try {
            recognition.start();
          } catch (error) {
            console.error('音声認識再開エラー:', error);
            setIsRecording(false);
          }
        }, 100);
      }
    };

    setRecognition(newRecognition);
    newRecognition.start();
  };

  const stopSpeechRecognition = () => {
    if (recognition && isRecording) {
      setIsRecording(false);
      recognition.stop();
      setRecognition(null);
    }
  };

  // カテゴリフィルタリング
  const filteredEntries = selectedCategory === 'all' 
    ? logEntries 
    : logEntries.filter(entry => entry.category === selectedCategory);

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-rose-50 to-pink-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* ヘッダー */}
        <header className="mb-8 text-center">
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-lg border border-orange-100">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-rose-600 bg-clip-text text-transparent mb-3">
              🏠 KazokuLog
            </h1>
            <p className="text-orange-700 text-lg">あなたの家族専属のAIコンシェルジュ</p>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左側：設定エリア */}
          <div className="lg:col-span-1 space-y-6">
            {/* 家族アクセスキー設定 */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-orange-100">
              <h2 className="text-xl font-bold text-orange-800 mb-4 flex items-center">
                👨‍👩‍👧‍👦 家族設定
              </h2>
              <div className="space-y-3">
                <input
                  type="text"
                  value={familyAccessKey}
                  onChange={(e) => setFamilyAccessKey(e.target.value)}
                  placeholder="家族アクセスキーを入力"
                  className="w-full px-4 py-3 border border-orange-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400 bg-white/80"
                />
                <button
                  onClick={createFamily}
                  className="w-full px-6 py-3 bg-gradient-to-r from-orange-400 to-rose-400 text-white rounded-xl hover:from-orange-500 hover:to-rose-500 transition-all shadow-lg transform hover:scale-105"
                >
                  ✨ 新しい家族を作成
                </button>
              </div>
            </div>

            {/* 日付・カテゴリ選択 */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-orange-100">
              <h2 className="text-xl font-bold text-orange-800 mb-4 flex items-center">
                📅 表示設定
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-orange-700 mb-2">日付選択</label>
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => handleDateChange(e.target.value)}
                    className="w-full px-4 py-3 border border-orange-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400 bg-white/80"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-orange-700 mb-2">カテゴリフィルタ</label>
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="w-full px-4 py-3 border border-orange-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400 bg-white/80"
                  >
                    <option value="all">すべて表示</option>
                    {categories.map(cat => (
                      <option key={cat.name} value={cat.name}>{cat.display_name}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* 家族構成設定 */}
            <FamilySettings
              familyMembers={familyMembers}
              onUpdateMembers={updateFamilyMembers}
            />

            {/* AIフィードバック */}
            <AIFeedback logEntries={logEntries} />

            {/* AIチャット */}
            <AIChat familyAccessKey={familyAccessKey} />

            {/* AI提案 */}
            <AISuggestions familyAccessKey={familyAccessKey} />
          </div>

          {/* 右側：ログエリア */}
          <div className="lg:col-span-2 space-y-6">
            {/* ログ入力フォーム */}
            <form onSubmit={handleSubmit} className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-orange-100">
              <h2 className="text-xl font-bold text-orange-800 mb-4 flex items-center">
                ✍️ ログ入力
              </h2>
              <div className="space-y-4">
                <div className="relative">
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="今日の出来事や気づいたことを入力してください..."
                    className="w-full px-4 py-3 border border-orange-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400 resize-none bg-white/80"
                    rows={4}
                  />
                  {speechSupported && (
                    <div className="absolute right-3 top-3 flex gap-2">
                      {!isRecording ? (
                        <button
                          type="button"
                          onClick={startSpeechRecognition}
                          className="px-3 py-1 bg-orange-200 text-orange-700 hover:bg-orange-300 rounded-lg transition-all text-sm"
                          title="音声入力を開始"
                        >
                          🎤 開始
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={stopSpeechRecognition}
                          className="px-3 py-1 bg-red-500 text-white hover:bg-red-600 rounded-lg transition-all text-sm animate-pulse"
                          title="音声入力を停止"
                        >
                          ⏹️ 停止
                        </button>
                      )}
                    </div>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={!inputText.trim() || !familyAccessKey || isLoading}
                  className="w-full px-6 py-3 bg-gradient-to-r from-rose-400 to-pink-400 text-white rounded-xl hover:from-rose-500 hover:to-pink-500 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-lg transform hover:scale-105"
                >
                  {isLoading ? '🔄 記録中...' : '💾 記録する'}
                </button>
              </div>
            </form>

            {/* エラー表示 */}
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-xl">
                ⚠️ {error}
              </div>
            )}

            {/* ログ一覧 */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-orange-100">
              <h2 className="text-xl font-bold text-orange-800 mb-4 flex items-center">
                📖 {format(new Date(selectedDate), 'yyyy年MM月dd日', { locale: ja })}のログ
                {selectedCategory !== 'all' && (
                  <span className="ml-2 text-sm bg-orange-200 text-orange-800 px-2 py-1 rounded-full">
                    {categories.find(cat => cat.name === selectedCategory)?.display_name}
                  </span>
                )}
              </h2>
              
              {isLoading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"></div>
                  <p className="mt-4 text-orange-700">読み込み中...</p>
                </div>
              ) : filteredEntries.length === 0 ? (
                <div className="text-center py-12 text-orange-500">
                  <div className="text-6xl mb-4">📝</div>
                  <p>この日のログはまだありません</p>
                  <p className="text-sm mt-2">上のフォームから記録を始めましょう</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredEntries.map((entry) => {
                    const categoryInfo = getCategoryInfo(entry.category);
                    return (
                      <div
                        key={entry.id}
                        className="bg-white/60 border border-orange-100 rounded-xl p-4 hover:bg-white/80 transition-all shadow-sm"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <span
                              className="px-3 py-1 rounded-full text-sm font-medium text-white shadow-md"
                              style={{ backgroundColor: categoryInfo.color }}
                            >
                              {categoryInfo.display_name}
                            </span>
                            <span className="text-xs text-orange-600 bg-orange-100 px-2 py-1 rounded-full">
                              信頼度: {Math.round(entry.confidence_score * 100)}%
                            </span>
                          </div>
                          <span className="text-xs text-orange-500 bg-orange-50 px-2 py-1 rounded-full">
                            {format(new Date(entry.created_at), 'HH:mm')}
                          </span>
                        </div>
                        <p className="text-gray-900 mb-2 font-medium">{entry.summary}</p>
                        <p className="text-sm text-gray-600 mb-3 leading-relaxed">{entry.original_text}</p>
                        {entry.keywords.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {entry.keywords.map((keyword, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 bg-orange-100 text-xs text-orange-700 rounded-full"
                              >
                                #{keyword}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KazokuLogApp;