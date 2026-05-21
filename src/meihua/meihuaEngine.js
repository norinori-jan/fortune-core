import strategyRegistry from "./registries/strategyRegistry.js";
import { divinate } from "./strategies/taiYiuStandard.js";

strategyRegistry.register("taiYiuStandard", divinate);

export function run({ strategy = "taiYiuStandard", ...params }) {
  const fn = strategyRegistry.get(strategy);
  if (!fn) return { error: `戦略 "${strategy}" が見つかりません` };
  return fn(params);
}
