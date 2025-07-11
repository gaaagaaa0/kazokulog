"use client";

import React, { useState } from 'react';

interface FamilyMember {
  id: string;
  name: string;
  age: number;
  relationship: string;
}

interface FamilySettingsProps {
  familyMembers: FamilyMember[];
  onUpdateMembers: (members: FamilyMember[]) => void;
}

const FamilySettings: React.FC<FamilySettingsProps> = ({ familyMembers, onUpdateMembers }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [newMember, setNewMember] = useState({ name: '', age: '', relationship: '' });

  const relationshipOptions = [
    { value: 'father', label: 'お父さん' },
    { value: 'mother', label: 'お母さん' },
    { value: 'son', label: '息子' },
    { value: 'daughter', label: '娘' },
    { value: 'grandfather', label: 'おじいちゃん' },
    { value: 'grandmother', label: 'おばあちゃん' },
    { value: 'other', label: 'その他' }
  ];

  const addMember = () => {
    if (!newMember.name || !newMember.age || !newMember.relationship) return;

    const member: FamilyMember = {
      id: Date.now().toString(),
      name: newMember.name,
      age: parseInt(newMember.age),
      relationship: newMember.relationship
    };

    const updatedMembers = [...familyMembers, member];
    onUpdateMembers(updatedMembers);
    setNewMember({ name: '', age: '', relationship: '' });
  };

  const removeMember = (id: string) => {
    const updatedMembers = familyMembers.filter(member => member.id !== id);
    onUpdateMembers(updatedMembers);
  };

  const getRelationshipLabel = (relationship: string) => {
    const option = relationshipOptions.find(opt => opt.value === relationship);
    return option ? option.label : relationship;
  };

  const getRelationshipEmoji = (relationship: string) => {
    const emojiMap: { [key: string]: string } = {
      father: '👨',
      mother: '👩',
      son: '👦',
      daughter: '👧',
      grandfather: '👴',
      grandmother: '👵',
      other: '👤'
    };
    return emojiMap[relationship] || '👤';
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-orange-100">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-orange-800 flex items-center">
          👨‍👩‍👧‍👦 家族構成
        </h2>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="px-4 py-2 bg-orange-200 text-orange-800 rounded-lg hover:bg-orange-300 transition-all text-sm"
        >
          {isOpen ? '閉じる' : '設定する'}
        </button>
      </div>

      {/* 家族メンバー一覧 */}
      <div className="space-y-2 mb-4">
        {familyMembers.length === 0 ? (
          <p className="text-orange-600 text-sm">まだ家族メンバーが登録されていません</p>
        ) : (
          familyMembers.map(member => (
            <div key={member.id} className="flex items-center justify-between bg-orange-50 p-3 rounded-xl">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getRelationshipEmoji(member.relationship)}</span>
                <div>
                  <span className="font-medium text-orange-800">{member.name}</span>
                  <span className="text-orange-600 text-sm ml-2">
                    {member.age}歳 - {getRelationshipLabel(member.relationship)}
                  </span>
                </div>
              </div>
              <button
                onClick={() => removeMember(member.id)}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                削除
              </button>
            </div>
          ))
        )}
      </div>

      {/* 家族メンバー追加フォーム */}
      {isOpen && (
        <div className="border-t border-orange-200 pt-4">
          <h3 className="text-lg font-semibold text-orange-700 mb-3">新しい家族メンバーを追加</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-orange-700 mb-1">名前</label>
              <input
                type="text"
                value={newMember.name}
                onChange={(e) => setNewMember({ ...newMember, name: e.target.value })}
                placeholder="例: 太郎"
                className="w-full px-3 py-2 border border-orange-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 bg-white/80"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-orange-700 mb-1">年齢</label>
              <input
                type="number"
                value={newMember.age}
                onChange={(e) => setNewMember({ ...newMember, age: e.target.value })}
                placeholder="例: 8"
                className="w-full px-3 py-2 border border-orange-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 bg-white/80"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-orange-700 mb-1">関係性</label>
              <select
                value={newMember.relationship}
                onChange={(e) => setNewMember({ ...newMember, relationship: e.target.value })}
                className="w-full px-3 py-2 border border-orange-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400 bg-white/80"
              >
                <option value="">選択してください</option>
                {relationshipOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={addMember}
              disabled={!newMember.name || !newMember.age || !newMember.relationship}
              className="w-full px-4 py-2 bg-gradient-to-r from-orange-400 to-rose-400 text-white rounded-lg hover:from-orange-500 hover:to-rose-500 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all"
            >
              追加
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FamilySettings;