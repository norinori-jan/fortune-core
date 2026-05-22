import { getRelation } from "../utils.js";
import dataRegistry from "../registries/dataRegistry.js";

// 時間スコープの判定
function judgeTimeScope(dateStr) {
  const now = new Date();
  const target = new Date(dateStr);
  const diffDays = (target - now) / (1000 * 60 * 60 * 24);
  if (Math.abs(diffDays) <= 31)  return "THIS_MONTH";
  if (Math.abs(diffDays) <= 365) return "THIS_YEAR";
  return "NOW";
}

// 体と用の五行から relation キーを決定
function judgeRelation(tiWuxing, youWuxing, tiStrength, youStrength) {
  if (tiWuxing === youWuxing) return "SAME_ELEMENT";

  const raw = getRelation(tiWuxing, youWuxing);

  if (raw === "相剋（克する）") {
    return tiStrength > youStrength ? "TAI_STRONG_YOU_WEAK" : "TAI_KOKU_YOU";
  }
  if (raw === "相剋（克される）") {
    return youStrength > tiStrength ? "YOU_STRONG_TAI_WEAK" : "YOU_KOKU_TAI";
  }
  if (raw === "相生（生じる）") return "TAI_SEI_YOU";
  if (raw === "相生（生まれる）") return "YOU_SEI_TAI";
  return "MIXED";
}

// メイン関数
export function calcJudgeKey({ benGua, zhiGua, domain, timestamp }) {
  const upper = dataRegistry.getHexagram(benGua.trigram_upper);
  const lower = dataRegistry.getHexagram(benGua.trigram_lower);

  if (!upper || !lower) return null;

  // 体卦=本卦上卦、用卦=之卦 として計算
  const tiWuxing  = upper.wuxing;
  const youWuxing = dataRegistry.getHexagram(zhiGua.name)?.wuxing ?? lower.wuxing;

  // 強さは卦番号で簡易代用（後で命式計算に差し替え可）
  const tiStrength  = upper.number;
  const youStrength = lower.number;

  const relation  = judgeRelation(tiWuxing, youWuxing, tiStrength, youStrength);
  const timeScope = judgeTimeScope(timestamp);

  return { relation, domain, timeScope, tiWuxing, youWuxing };
}
