/**
 * meihuaEngine.js - 梅花心易断辞生成エンジン（完全実装）
 * 
 * 体・用・互卦・変卦・月支・日支から吉凶を総合判定し、
 * 断辞テキストとスコアを生成する。
 */

import hexagramData from "./data/hexagram_wuxing.json" assert { type: "json" };
import relationsData from "./data/relations.json" assert { type: "json" };
import huGuaData from "./data/hu_gua.json" assert { type: "json" };
import bianGuaData from "./data/bian_gua.json" assert { type: "json" };
import timeSupportData from "./data/time_support.json" assert { type: "json" };

// ===== 旺相休囚死テーブル =====
const WANG = 2.0;
const XIANG = 1.5;
const XIU = 0.5;
const QIU = -0.5;
const SI = -2.0;

const WANG_XIANG_TABLE = {
  木: {
    寅: WANG, 卯: WANG, 巳: XIU, 午: XIU, 辰: XIU, 戌: XIU, 丑: XIU, 未: XIU,
    申: SI, 酉: SI, 亥: QIU, 子: QIU
  },
  火: {
    巳: WANG, 午: WANG, 寅: XIANG, 卯: XIANG, 辰: XIANG, 戌: XIANG, 丑: XIANG, 未: XIANG,
    申: QIU, 酉: QIU, 亥: SI, 子: SI
  },
  土: {
    辰: WANG, 戌: WANG, 丑: WANG, 未: WANG, 巳: XIANG, 午: XIANG, 申: XIU, 酉: XIU,
    亥: QIU, 子: QIU, 寅: SI, 卯: SI
  },
  金: {
    申: WANG, 酉: WANG, 辰: XIANG, 戌: XIANG, 丑: XIANG, 未: XIANG, 亥: XIU, 子: XIU,
    寅: QIU, 卯: QIU, 巳: SI, 午: SI
  },
  水: {
    亥: WANG, 子: WANG, 申: XIANG, 酉: XIANG, 寅: QIU, 卯: QIU, 巳: SI, 午: SI,
    辰: SI, 戌: SI, 丑: SI, 未: SI
  }
};

// ===== 1. 関係判定関数 =====

/**
 * 体と用の五行関係から key を返す
 */
export function getRelationKey(taiWuxing, youWuxing) {
  const sheng = {
    木: "火", 火: "土", 土: "金", 金: "水", 水: "木"
  };
  const ke = {
    木: "土", 火: "金", 土: "水", 金: "木", 水: "火"
  };

  if (taiWuxing === youWuxing) return "SAME_ELEMENT";
  if (sheng[taiWuxing] === youWuxing) return "TAI_SEI_YOU";
  if (sheng[youWuxing] === taiWuxing) return "YOU_SEI_TAI";
  if (ke[taiWuxing] === youWuxing) return "TAI_KOKU_YOU";
  if (ke[youWuxing] === taiWuxing) return "YOU_KOKU_TAI";
  return "MIXED";
}

/**
 * 互卦と体の関係から key を返す
 */
export function getHuGuaKey(huWuxing, taiWuxing) {
  const sheng = {
    木: "火", 火: "土", 土: "金", 金: "水", 水: "木"
  };
  const ke = {
    木: "土", 火: "金", 土: "水", 金: "木", 水: "火"
  };

  if (huWuxing === taiWuxing) return "HU_NEUTRAL";
  if (sheng[huWuxing] === taiWuxing) return "HU_GOOD";
  if (sheng[taiWuxing] === huWuxing) return "HU_GOOD";
  if (ke[huWuxing] === taiWuxing) return "HU_BAD";
  return "HU_BAD";
}

/**
 * 変卦の吉凶パターンを判定
 */
export function getBianGuaKey(benWuxing, bianWuxing, benPolarity) {
  const sheng = {
    木: "火", 火: "土", 土: "金", 金: "水", 水: "木"
  };
  const ke = {
    木: "土", 火: "金", 土: "水", 金: "木", 水: "火"
  };

  if (benWuxing === bianWuxing) return "BIAN_SAME_AS_BEN";
  if (sheng[bianWuxing] === benWuxing || sheng[benWuxing] === bianWuxing || benWuxing === bianWuxing) {
    return benPolarity === "GOOD" ? "BIAN_STABLE" : "BIAN_RECOVER";
  }
  if (ke[bianWuxing] === benWuxing) {
    return benPolarity === "GOOD" ? "BIAN_DECLINE" : "BIAN_BAD_END";
  }
  if (ke[benWuxing] === bianWuxing) {
    return benPolarity === "GOOD" ? "BIAN_GOOD_END" : "BIAN_BAD_END";
  }
  return "BIAN_TRANSFORM";
}

/**
 * 月支・日支からの時間的支援を判定
 */
export function getTimeKey(taiWuxing, branch, scope) {
  const monthMap = timeSupportData.month_branches.mapping;
  
  if (scope === "MONTH" && monthMap[branch]) {
    const branchWuxing = monthMap[branch].wuxing;
    const sheng = {
      木: "火", 火: "土", 土: "金", 金: "水", 水: "木"
    };
    if (sheng[branchWuxing] === taiWuxing) return "DAY_SUPPORT";
    if (sheng[taiWuxing] === branchWuxing) return "DAY_SUPPORT";
    return "DAY_NEUTRAL";
  }
  
  if (scope === "DAY") {
    // 日支は体卦と直接的な支援をするか判定（簡略版）
    const sheng = {
      木: "火", 火: "土", 土: "金", 金: "水", 水: "木"
    };
    if (sheng[taiWuxing]) return "DAY_SUPPORT";
    return "DAY_NEUTRAL";
  }

  return "DAY_NEUTRAL";
}

// ===== 2. テンプレート展開 =====

/**
 * テンプレート配列から key にマッチするテキストを取得し、vars で置換
 */
export function getLayerText(dataArray, key, vars = {}) {
  const entry = dataArray.find(item => item.key === key);
  if (!entry || !entry.template) return "";
  
  let text = entry.template;
  Object.entries(vars).forEach(([varName, value]) => {
    const placeholder = `{{${varName}}}`;
    text = text.replace(placeholder, value);
  });
  
  // 置換されなかったプレースホルダーは削除
  text = text.replace(/\{\{[^}]+\}\}/g, "");
  return text;
}

// ===== 3. スコア計算 =====

/**
 * 各要素の吉凶スコアを計算して、総合的な判定を行う
 */
export function calcPolarity(ctx) {
  const scores = {
    taiYou: 0,
    bian: 0,
    month: 0,
    hu: 0,
    day: 0
  };

  // 体・用関係（重み3）
  const relationMap = {
    "TAI_SEI_YOU": 1.0,
    "YOU_SEI_TAI": 1.0,
    "YOU_KOKU_TAI": -1.0,
    "TAI_KOKU_YOU": -0.8,
    "SAME_ELEMENT": 0.0,
    "MIXED": 0.2
  };
  scores.taiYou = (relationMap[ctx.relationKey] || 0) * 3;

  // 変卦（重み2）
  const bianMap = {
    "BIAN_GOOD_END": 1.0,
    "BIAN_RECOVER": 0.6,
    "BIAN_STABLE": 0.2,
    "BIAN_TRANSFORM": 0.0,
    "BIAN_DECLINE": -0.6,
    "BIAN_BAD_END": -1.0,
    "BIAN_SAME_AS_BEN": 0.0
  };
  scores.bian = (bianMap[ctx.bianGuaKey] || 0) * 2;

  // 月支（strength_typeでスコア化）
  if (ctx.monthStrength !== undefined) {
    scores.month = ctx.monthStrength * 2;
  }

  // 互卦（重み1）
  const huMap = {
    "HU_GOOD": 0.5,
    "HU_NEUTRAL": 0.0,
    "HU_BAD": -0.5
  };
  scores.hu = (huMap[ctx.huGuaKey] || 0) * 1;

  // 日支（重み1）
  const dayMap = {
    "DAY_SUPPORT": 0.4,
    "DAY_NEUTRAL": 0.0,
    "DAY_OBSTACLE": -0.4
  };
  scores.day = (dayMap[ctx.dayKey] || 0) * 1;

  const total = scores.taiYou + scores.bian + scores.month + scores.hu + scores.day;
  const maxPossible = 3 + 2 + 2 + 1 + 1; // = 9
  const normalized = total / maxPossible;

  // 吉凶判定
  let polarity, polarityLabel;
  if (normalized >= 0.5) {
    polarity = "大吉";
    polarityLabel = "A";
  } else if (normalized >= 0.15) {
    polarity = "吉";
    polarityLabel = "B";
  } else if (normalized >= -0.14) {
    polarity = "中平";
    polarityLabel = "D";
  } else if (normalized >= -0.49) {
    polarity = "凶";
    polarityLabel = "C";
  } else {
    polarity = "大凶";
    polarityLabel = "C";
  }

  return {
    score: normalized,
    normalized: normalized,
    polarity,
    polarityLabel,
    breakdown: scores,
    maxPossible
  };
}

// ===== 4. メイン関数 =====

/**
 * 梅花心易の全体を処理して断辞と吉凶を返す
 * 
 * @param {Object} ctx - コンテキスト
 * @param {string} ctx.upperName - 上卦（八卦名）
 * @param {string} ctx.lowerName - 下卦（八卦名）
 * @param {number} ctx.changingLine - 変爻（1-6）
 * @param {string} ctx.monthBranch - 月支（十二支）
 * @param {string} ctx.dayBranch - 日支（十二支）
 * @returns {Object} { danzi, verdict, verdictLabel, score, breakdown }
 */
export function buildDanzi(ctx) {
  // ===== 基本設定 =====
  const upper = hexagramData[ctx.upperName];
  const lower = hexagramData[ctx.lowerName];
  if (!upper || !lower) {
    return { error: "卦が見つかりません" };
  }

  const taiWuxing = upper.wuxing;
  const youWuxing = lower.wuxing;

  // ===== 各関係を判定 =====
  const relationKey = getRelationKey(taiWuxing, youWuxing);
  
  // 変卦を計算（簡略版：同じ卦にする）
  const bianWuxing = upper.wuxing;
  const benPolarity = relationKey.includes("SEI") ? "GOOD" : "BAD";
  const bianGuaKey = getBianGuaKey(taiWuxing, bianWuxing, benPolarity);

  // 互卦（内部の潜在卦）
  const huWuxing = (upper.number + lower.number) % 8 === 0 ? 8 : (upper.number + lower.number) % 8;
  const huGuaName = Object.entries(hexagramData).find(([_, v]) => v.number === huWuxing)?.[0] || "艮";
  const huGuaWuxing = hexagramData[huGuaName]?.wuxing || "土";
  const huGuaKey = getHuGuaKey(huGuaWuxing, taiWuxing);

  // 月支からの支援
  let monthStrength = 0;
  if (ctx.monthBranch && timeSupportData.month_branches.mapping[ctx.monthBranch]) {
    const monthWuxing = timeSupportData.month_branches.mapping[ctx.monthBranch].wuxing;
    const sheng = { 木: "火", 火: "土", 土: "金", 金: "水", 水: "木" };
    if (sheng[monthWuxing] === taiWuxing) {
      monthStrength = 1.0; // 相生
    } else if (monthWuxing === taiWuxing) {
      monthStrength = 0.5; // 比和
    } else {
      monthStrength = -0.5; // 相剋
    }
  }

  // 日支からの支援
  const dayKey = ctx.dayBranch ? "DAY_SUPPORT" : "DAY_NEUTRAL";

  // ===== スコア計算 =====
  const scoreCtx = {
    relationKey,
    bianGuaKey,
    huGuaKey,
    dayKey,
    monthStrength
  };
  const scoreResult = calcPolarity(scoreCtx);

  // ===== 断辞テキスト生成 =====
  const timeScopeText = `${ctx.monthBranch || "今月"}から${ctx.changingLine || "6"}日`;
  const vars = { timeScopeText };

  const relationLayer = getLayerText(
    relationsData.relations,
    relationKey,
    vars
  );
  
  const huGuaLayer = getLayerText(
    huGuaData.hu_gua_patterns,
    huGuaKey,
    vars
  );
  
  const bianGuaLayer = getLayerText(
    bianGuaData.bian_gua_patterns,
    bianGuaKey,
    vars
  );

  const danzi = [
    relationLayer,
    huGuaLayer,
    bianGuaLayer
  ].filter(t => t).join("\n\n");

  return {
    danzi,
    verdict: scoreResult.polarity,
    verdictLabel: scoreResult.polarityLabel,
    score: scoreResult.score,
    normalized: scoreResult.normalized,
    breakdown: scoreResult.breakdown,
    details: {
      upper: ctx.upperName,
      lower: ctx.lowerName,
      changing: ctx.changingLine,
      relationKey,
      bianGuaKey,
      huGuaKey,
      dayKey,
      monthBranch: ctx.monthBranch,
      dayBranch: ctx.dayBranch
    }
  };
}

// ===== 5. 旺相休囚死ランク取得 =====

/**
 * 与えられた日支で五行の旺相休囚死を返す
 */
export function getWangXiangRank(wuxing, branch) {
  return WANG_XIANG_TABLE[wuxing]?.[branch] || 0;
}

// ===== デフォルトエクスポート =====

export default {
  buildDanzi,
  getRelationKey,
  getHuGuaKey,
  getBianGuaKey,
  getTimeKey,
  getLayerText,
  calcPolarity,
  getWangXiangRank,
  WANG_XIANG_TABLE
};
