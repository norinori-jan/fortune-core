'use client';

import React, { useState, useEffect } from 'react';

export type CardOrientation = 'UPRIGHT' | 'REVERSED';
export type ElementType = 'AIR' | 'FIRE' | 'WATER' | 'EARTH';

interface TarotCardProps {
  number: number;
  name: string;
  element: ElementType;
  orientation: CardOrientation;
  meaning: string;
  isFlipped?: boolean;
  onFlip?: (isFlipped: boolean) => void;
  interactive?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

interface CelticCrossPositionProps {
  position: number;
  positionName: string;
  card?: {
    number: number;
    name: string;
    element: ElementType;
    orientation: CardOrientation;
    meaning: string;
  };
}

const elementColors: Record<ElementType, { bg: string; border: string; glow: string }> = {
  AIR: {
    bg: 'from-cyan-900 to-blue-900',
    border: 'border-cyan-500',
    glow: 'shadow-cyan-500/50'
  },
  FIRE: {
    bg: 'from-red-900 to-orange-900',
    border: 'border-red-500',
    glow: 'shadow-red-500/50'
  },
  WATER: {
    bg: 'from-blue-900 to-indigo-900',
    border: 'border-blue-500',
    glow: 'shadow-blue-500/50'
  },
  EARTH: {
    bg: 'from-amber-900 to-yellow-900',
    border: 'border-amber-500',
    glow: 'shadow-amber-500/50'
  }
};

const elementSymbols: Record<ElementType, string> = {
  AIR: '⟡',
  FIRE: '⟡',
  WATER: '⟡',
  EARTH: '⟡'
};

const elementLabels: Record<ElementType, string> = {
  AIR: '風',
  FIRE: '火',
  WATER: '水',
  EARTH: '土'
};

export function TarotCard({
  number,
  name,
  element,
  orientation,
  meaning,
  isFlipped = false,
  onFlip,
  interactive = true,
  size = 'md',
  className = ''
}: TarotCardProps) {
  const [flipped, setFlipped] = useState(isFlipped);

  const sizeClasses = {
    sm: 'w-24 h-32',
    md: 'w-32 h-44',
    lg: 'w-40 h-56'
  };

  const handleFlip = () => {
    if (interactive) {
      setFlipped(!flipped);
      onFlip?.(!flipped);
    }
  };

  const colors = elementColors[element];
  const isReversed = orientation === 'REVERSED';

  return (
    <div
      className={`
        relative cursor-pointer perspective ${sizeClasses[size]} ${className}
      `}
      onClick={handleFlip}
      style={{ perspective: '1000px' }}
    >
      <div
        className={`
          relative w-full h-full transition-transform duration-500
          ${flipped ? '[transform:rotateY(180deg)]' : '[transform:rotateY(0deg)]'}
        `}
        style={{
          transformStyle: 'preserve-3d',
          transform: flipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
          transitionDuration: '500ms'
        }}
      >
        {/* Front of Card - Deck Back */}
        <div
          className={`
            absolute w-full h-full rounded-xl border-2 border-purple-500
            bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900
            shadow-lg shadow-purple-500/50 flex items-center justify-center
            p-4 backdrop-blur-sm
          `}
          style={{ backfaceVisibility: 'hidden' }}
        >
          <div className="text-center">
            <div className="text-3xl mb-2">✦</div>
            <div className="text-xs text-purple-300 font-serif tracking-wider">
              Fortune Core
            </div>
            <div className="text-xs text-purple-400 mt-2 font-serif">
              Tarot
            </div>
          </div>
        </div>

        {/* Back of Card - Card Face */}
        <div
          className={`
            absolute w-full h-full rounded-xl border-2 ${colors.border}
            bg-gradient-to-br ${colors.bg}
            ${!flipped && colors.glow} shadow-lg
            flex flex-col items-center justify-between p-3
            backdrop-blur-sm
          `}
          style={{
            backfaceVisibility: 'hidden',
            transform: 'rotateY(180deg)'
          }}
        >
          {/* Top Section */}
          <div className="w-full text-center">
            <div className="text-xs text-gray-300 font-serif tracking-widest mb-1">
              No. {String(number).padStart(2, '0')}
            </div>
            <div className="text-xl font-serif text-white font-bold leading-tight">
              {name}
            </div>
          </div>

          {/* Middle Section - Card Visual */}
          <div className="flex flex-col items-center justify-center flex-1 space-y-2">
            <div
              className={`
                text-3xl transform transition-transform
                ${isReversed ? 'rotate-180' : 'rotate-0'}
              `}
            >
              {elementSymbols[element]}
            </div>
            <div className="text-xs text-gray-200 font-serif">
              {orientation === 'UPRIGHT' ? '正位置' : '逆位置'}
            </div>
            <div className="px-2 py-1 rounded-full bg-black bg-opacity-40 border border-gray-400">
              <span className="text-xs text-gray-100">{elementLabels[element]}</span>
            </div>
          </div>

          {/* Bottom Section - Meaning Preview */}
          <div className="w-full text-center">
            <div className="text-xs text-gray-300 font-serif leading-tight line-clamp-2 max-h-8">
              {meaning.substring(0, 40)}
              {meaning.length > 40 ? '...' : ''}
            </div>
            <div className="text-xs text-gray-400 mt-1">
              タップで詳細を表示
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function CelticCrossPosition({
  position,
  positionName,
  card
}: CelticCrossPositionProps) {
  const [flipped, setFlipped] = useState(false);

  const positionLabels: Record<number, string> = {
    1: '現状',
    2: '障害',
    3: '顕在意識',
    4: '潜在意識',
    5: '過去',
    6: '未来',
    7: '本人の立場',
    8: '環境',
    9: '希望/不安',
    10: '最終結果'
  };

  const positionDescriptions: Record<number, string> = {
    1: '現在のあなたの状況',
    2: '立ちはだかる障害',
    3: '意識している側面',
    4: '無意識の基盤',
    5: '過去からの影響',
    6: '近い将来',
    7: 'あなた自身の立場',
    8: '周囲の環境や人物',
    9: 'あなたの願いや不安',
    10: '最終的な結果'
  };

  return (
    <div className="flex flex-col items-center space-y-2">
      {/* Position Label */}
      <div className="text-center">
        <div className="text-xs text-purple-400 font-serif tracking-widest">
          Position {position}
        </div>
        <div className="text-sm font-bold text-purple-200 font-serif">
          {positionLabels[position]}
        </div>
        <div className="text-xs text-gray-400 font-serif">
          {positionDescriptions[position]}
        </div>
      </div>

      {/* Card Display */}
      <div>
        {card ? (
          <TarotCard
            number={card.number}
            name={card.name}
            element={card.element}
            orientation={card.orientation}
            meaning={card.meaning}
            isFlipped={flipped}
            onFlip={setFlipped}
            interactive={true}
            size="sm"
          />
        ) : (
          <div className="w-24 h-32 rounded-xl border-2 border-dashed border-gray-600 bg-gray-900 bg-opacity-50 flex items-center justify-center">
            <span className="text-xs text-gray-600">空いています</span>
          </div>
        )}
      </div>
    </div>
  );
}

interface CelticCrossLayoutProps {
  cards: {
    [key: number]: {
      number: number;
      name: string;
      element: ElementType;
      orientation: CardOrientation;
      meaning: string;
    };
  };
}

export function CelticCrossLayout({ cards }: CelticCrossLayoutProps) {
  return (
    <div className="w-full max-w-3xl mx-auto p-8 bg-gradient-to-b from-gray-900 to-gray-950 rounded-2xl border border-purple-500 shadow-2xl shadow-purple-500/20">
      {/* Title */}
      <div className="text-center mb-12">
        <h2 className="text-2xl font-serif font-bold text-purple-300 mb-2">
          ケルト十字スプレッド
        </h2>
        <p className="text-sm text-gray-400 font-serif">
          10枚のカードがあなたの未来を映し出します
        </p>
      </div>

      {/* Layout */}
      <div className="relative w-full" style={{ aspectRatio: '16/10' }}>
        {/* Center Cross Formation */}
        <div className="absolute inset-0 flex items-center justify-center">
          {/* Vertical and Horizontal Center Line Visualization */}
          <svg
            className="absolute inset-0 w-full h-full opacity-20"
            viewBox="0 0 600 400"
            preserveAspectRatio="none"
          >
            <line x1="300" y1="50" x2="300" y2="350" stroke="rgb(168, 85, 247)" strokeWidth="1" />
            <line x1="100" y1="200" x2="500" y2="200" stroke="rgb(168, 85, 247)" strokeWidth="1" />
            <circle cx="300" cy="200" r="60" fill="none" stroke="rgb(168, 85, 247)" strokeWidth="1" />
          </svg>

          {/* Position 1 - Current Situation (Center) */}
          <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <CelticCrossPosition
              position={1}
              positionName="Current Situation"
              card={cards[1]}
            />
          </div>

          {/* Position 2 - Challenge (Cross overlay) */}
          <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div style={{ position: 'relative', width: '140px', height: '180px' }}>
              <div style={{ position: 'absolute', inset: 0 }}>
                <CelticCrossPosition
                  position={2}
                  positionName="Challenge"
                  card={cards[2]}
                />
              </div>
            </div>
          </div>

          {/* Position 3 - Distant Past (Left) */}
          <div className="absolute left-0 top-1/2 transform -translate-y-1/2 ml-4">
            <CelticCrossPosition
              position={3}
              positionName="Distant Past"
              card={cards[3]}
            />
          </div>

          {/* Position 4 - Foundation (Right) */}
          <div className="absolute right-0 top-1/2 transform -translate-y-1/2 mr-4">
            <CelticCrossPosition
              position={4}
              positionName="Foundation"
              card={cards[4]}
            />
          </div>

          {/* Position 5 - Past (Top) */}
          <div className="absolute left-1/2 top-0 transform -translate-x-1/2">
            <CelticCrossPosition
              position={5}
              positionName="Past"
              card={cards[5]}
            />
          </div>

          {/* Position 6 - Future (Bottom) */}
          <div className="absolute left-1/2 bottom-0 transform -translate-x-1/2">
            <CelticCrossPosition
              position={6}
              positionName="Future"
              card={cards[6]}
            />
          </div>
        </div>

        {/* Right Column - Positions 7-10 */}
        <div className="absolute right-0 top-0 w-1/3 h-full flex flex-col justify-around pr-4">
          <CelticCrossPosition
            position={7}
            positionName="Self"
            card={cards[7]}
          />
          <CelticCrossPosition
            position={8}
            positionName="Environment"
            card={cards[8]}
          />
          <CelticCrossPosition
            position={9}
            positionName="Hopes/Fears"
            card={cards[9]}
          />
          <CelticCrossPosition
            position={10}
            positionName="Outcome"
            card={cards[10]}
          />
        </div>
      </div>
    </div>
  );
}

interface TarotReadingDisplayProps {
  readingData: {
    reading_id: string;
    timestamp: string;
    query_text: string;
    user_seed: number | null;
    element_distribution: Record<ElementType, number>;
    positions: Record<string, any>;
  };
}

export function TarotReadingDisplay({ readingData }: TarotReadingDisplayProps) {
  const cardsMap: Record<number, any> = {};

  Object.entries(readingData.positions).forEach(([positionName, cardData]: [string, any]) => {
    const positionMap: Record<string, number> = {
      'CURRENT_SITUATION': 1,
      'CHALLENGE': 2,
      'DISTANT_PAST': 3,
      'FOUNDATION': 4,
      'PAST': 5,
      'FUTURE': 6,
      'SELF': 7,
      'ENVIRONMENT': 8,
      'HOPES_FEARS': 9,
      'OUTCOME': 10
    };
    const positionNum = positionMap[positionName];
    if (positionNum) {
      cardsMap[positionNum] = {
        number: cardData.number,
        name: cardData.name,
        element: cardData.element,
        orientation: cardData.orientation,
        meaning: cardData.meaning
      };
    }
  });

  const elementColors: Record<ElementType, string> = {
    AIR: 'text-cyan-400',
    FIRE: 'text-red-400',
    WATER: 'text-blue-400',
    EARTH: 'text-amber-400'
  };

  return (
    <div className="w-full space-y-8">
      {/* Reading Header */}
      <div className="bg-gradient-to-r from-purple-900 to-indigo-900 rounded-lg p-6 border border-purple-500">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h3 className="text-sm font-serif text-gray-400 mb-1">Reading ID</h3>
            <p className="text-lg font-mono text-purple-200">{readingData.reading_id}</p>
          </div>
          <div>
            <h3 className="text-sm font-serif text-gray-400 mb-1">時刻</h3>
            <p className="text-lg text-purple-200">
              {new Date(readingData.timestamp).toLocaleString('ja-JP')}
            </p>
          </div>
          <div className="md:col-span-2">
            <h3 className="text-sm font-serif text-gray-400 mb-1">相談内容</h3>
            <p className="text-lg text-purple-200">
              {readingData.query_text || '(指定なし)'}
            </p>
          </div>
          <div className="md:col-span-2">
            <h3 className="text-sm font-serif text-gray-400 mb-1">シンクロニシティシード</h3>
            <p className="text-lg font-mono text-purple-200">
              {readingData.user_seed !== null
                ? readingData.user_seed
                : 'ランダム'}
            </p>
          </div>
        </div>
      </div>

      {/* Celtic Cross Layout */}
      <CelticCrossLayout cards={cardsMap} />

      {/* Element Distribution */}
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-serif font-bold text-purple-300 mb-4">
          要素バランス分析
        </h3>
        <div className="grid grid-cols-4 gap-4">
          {Object.entries(readingData.element_distribution).map(([element, count]) => (
            <div
              key={element}
              className="bg-gray-800 rounded-lg p-4 text-center border border-gray-700"
            >
              <div className={`text-2xl font-bold ${elementColors[element as ElementType]} mb-2`}>
                {element === 'AIR' && '風'}
                {element === 'FIRE' && '火'}
                {element === 'WATER' && '水'}
                {element === 'EARTH' && '土'}
              </div>
              <div className="text-2xl font-bold text-white">{count}</div>
              <div className="text-xs text-gray-400 mt-1">{element}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Help Text */}
      <div className="text-xs text-gray-500 text-center font-serif">
        各カードをタップして詳細な解釈を確認してください
      </div>
    </div>
  );
}
