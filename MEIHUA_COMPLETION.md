# 梅花心易 実装完成 - 動作確認ガイド

## ✅ 実装完了

### Step 1: meihuaEngine.js 完全実装 ✓
- [x] `time_support.json` 作成
- [x] `getRelationKey()` - 体用の相生相剋判定
- [x] `getHuGuaKey()` - 互卦判定
- [x] `getBianGuaKey()` - 変卦判定
- [x] `calcPolarity()` - スコア計算（-1.0 ～ +1.0）
- [x] `buildDanzi()` - 梅花心易断辞生成
- [x] `getLayerText()` - テンプレート展開
- [x] `WANG_XIANG_TABLE` - 旺相休囚死テーブル

### Step 2: index.html 梅花心易統合 ✓
- [x] `buildMeihuaDanzi()` - 梅花処理（月支・日支対応）
- [x] `getMonthBranch()` / `getDayBranch()` - 時支算出
- [x] `buildUserPrompt()` 修正 - 初段断辞を AIプロンプトに組み込み
- [x] `renderResult()` 修正 - 吉凶バッジ・スコアバー・スコア表示

### Step 3: GitHub Pages デプロイ ✓
- [x] git commit -m "feat: complete meihuaEngine and integrate into index.html"
- [x] git push
- [x] https://norinori-jan.github.io/fortune-core/index.html で確認

---

## 🧪 テスト確認手順

### 環境
- iPhone Safari または デスクトップ Chrome/Safari
- Anthropic API キー（https://console.anthropic.com から取得）

### テスト流程

#### 1️⃣ ページを開く
```
URL: https://norinori-jan.github.io/fortune-core/index.html
```

#### 2️⃣ APIキーを入力
-「sk-ant-...」形式の有効なキーを入力
- 「続ける」をクリック

#### 3️⃣ 占術選択
- 「☯️ 梅花心易」をタップ

#### 4️⃣ 質問入力
- 例：「新しい仕事に転職すべき？」
- 「次へ」をタップ

#### 5️⃣ 数字入力
- 1つ目の数字：1～8（例：3 → 離卦）
- 2つ目の数字：1～8（例：5 → 巽卦）
- 「鑑定する」をタップ

#### 6️⃣ 結果表示確認
- ✅ **吉凶バッジが表示される**
  - 大吉（A）：金色 🟡
  - 吉（B）：緑色 🟢
  - 中平（D）：橙色 🟠
  - 凶（C）：赤色 🔴
  
- ✅ **スコアバーが表示される**
  - -1.0 ～ +1.0 の範囲を 0～100% にマップ
  
- ✅ **上卦・下卦・変爻が表示される**
  - 例：上卦：离 / 下卦：巽 / 変爻：3爻
  
- ✅ **初段断辞が表示される**
  - 体・用の相生相剋に基づいた断辞
  
- ✅ **AI による最終鑑定文が表示される**
  - 初段断辞と高亨四分類を組み込んだ詳細な鑑定

#### 7️⃣ コピー機能確認
- 「📋 コピー」をタップ
- iPhone: メモアプリに貼り付け可能
- Desktop: 任意のテキストエディタに貼り付け可能

---

## 📊 吉凶スコアの計算式

### 総合スコア
```
体・用相生/相剋 (重み3)
+ 変卦吉凶 (重み2)
+ 月支支援 (重み2)
+ 互卦吉凶 (重み1)
+ 日支支援 (重み1)
= -1.0 ～ +1.0
```

### 判定基準
| スコア | 判定 | ラベル |
|--------|------|--------|
| ≥ 0.5 | 大吉 | A |
| ≥ 0.15 | 吉 | B |
| ≥ -0.14 | 中平 | D |
| ≥ -0.49 | 凶 | C |
| < -0.49 | 大凶 | C |

---

## 📂 実装ファイル一覧

```
fortune-core/
├── index.html                           ← SPA（梅花統合済み）
├── src/meihua/
│   ├── meihuaEngine.js                 ← 完全実装
│   ├── data/
│   │   ├── time_support.json           ← 新規作成
│   │   ├── relations.json              ← 体用テンプレート
│   │   ├── hu_gua.json                 ← 互卦テンプレート
│   │   ├── bian_gua.json               ← 変卦テンプレート
│   │   └── hexagram_wuxing.json        ← 八卦マップ
```

---

## 🎯 完成の定義

✅ **以下がすべて成功していれば完成**

1. ✅ iPhone Safari で URL を開く → ページ表示される
2. ✅ API キー入力 → 「続ける」でスキップ可能
3. ✅ 梅花心易選択 → 質問入力画面表示
4. ✅ 質問 + 数字入力 → ローディング表示
5. ✅ **吉凶バッジ表示** → 色分けされたバッジが表示される
6. ✅ **スコアバー表示** → -1.0 ～ +1.0 のバーが表示される
7. ✅ **断辞・鑑定文表示** → AI による断占が表示される
8. ✅ **コピー機能** → テキストをコピー可能

---

## 📌 備考

- **オフライン機能**: APIキーは localStorage に保存（オフライン時もキー保持）
- **ダークモード対応**: prefers-color-scheme で自動判定
- **モバイルファースト**: 44px タップターゲット、16px 最小フォント
- **外部依存なし**: CDN不要、1ファイル実装

---

**デプロイURL**: https://norinori-jan.github.io/fortune-core/index.html

**GitHub**: https://github.com/norinori-jan/fortune-core
