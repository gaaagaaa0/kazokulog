"use client";

import React, { useState, useEffect } from 'react';

interface AISuggestionsProps {
  familyAccessKey: string;
}

const AISuggestions: React.FC<AISuggestionsProps> = ({ familyAccessKey }) => {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const loadSuggestions = async () => {
    if (!familyAccessKey) return;

    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/ai/suggestions/${familyAccessKey}`);
      
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      } else {
        console.error('Failed to load suggestions');
      }
    } catch (error) {
      console.error('Error loading suggestions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (familyAccessKey && isOpen) {
      loadSuggestions();
    }
  }, [familyAccessKey, isOpen]);

  if (!familyAccessKey) {
    return null;
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-orange-100">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-orange-800 flex items-center">
          💡 AIからの提案
        </h2>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="px-4 py-2 bg-orange-200 text-orange-800 rounded-lg hover:bg-orange-300 transition-all text-sm"
        >
          {isOpen ? '閉じる' : '提案を見る'}
        </button>
      </div>

      {isOpen && (
        <div className="space-y-4">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
              <p className="mt-2 text-orange-700">AIが提案を考えています...</p>
            </div>
          ) : suggestions.length > 0 ? (
            <div className="space-y-3">
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="p-4 bg-gradient-to-r from-orange-50 to-rose-50 rounded-xl border border-orange-200"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-gradient-to-r from-orange-400 to-rose-400 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-800 leading-relaxed">{suggestion}</p>
                    </div>
                  </div>
                </div>
              ))}
              <button
                onClick={loadSuggestions}
                className="w-full px-4 py-2 bg-orange-200 text-orange-800 rounded-lg hover:bg-orange-300 transition-all text-sm"
              >
                🔄 新しい提案を取得
              </button>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">💭</div>
              <p>まだ提案がありません</p>
              <p className="text-sm mt-1">ログを記録すると、AIが提案をしてくれます</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AISuggestions;