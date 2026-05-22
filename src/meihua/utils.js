// 五行の相生・相克判定
export const WUXING_SHENG = {
  木: "火", 火: "土", 土: "金", 金: "水", 水: "木"
};
export const WUXING_KE = {
  木: "土", 火: "金", 土: "水", 金: "木", 水: "火"
};

export function getRelation(a, b) {
  if (WUXING_SHENG[a] === b) return "相生（生じる）";
  if (WUXING_SHENG[b] === a) return "相生（生まれる）";
  if (WUXING_KE[a] === b) return "相克（克する）";
  if (WUXING_KE[b] === a) return "相克（克される）";
  return "比和";
}
