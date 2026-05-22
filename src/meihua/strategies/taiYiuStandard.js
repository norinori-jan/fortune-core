import { getRelation } from "../utils.js";
import dataRegistry from "../registries/dataRegistry.js";

export function divinate({ upperName, lowerName, changingLine }) {
  const upper = dataRegistry.getHexagram(upperName);
  const lower = dataRegistry.getHexagram(lowerName);
  if (!upper || !lower) return { error: "卦が見つかりません" };
  const relation = getRelation(upper.wuxing, lower.wuxing);
  return { upper: { name: upperName, ...upper }, lower: { name: lowerName, ...lower }, changingLine, relation };
}
