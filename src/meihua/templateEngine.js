const TIME_SCOPE_TEXT = {
  THIS_MONTH: "今月",
  THIS_YEAR:  "今年",
  NOW:        "現在"
};

export function findTemplate(rules, key) {
  return rules.find(rule =>
    Object.entries(rule.match ?? { key: rule.key }).every(([k, v]) => key[k] === v)
  ) ?? null;
}

export function renderTemplate(template, vars) {
  return template.replace(/{{(.*?)}}/g, (_, name) => vars[name.trim()] ?? "");
}

export function generateFortuneText(judgeKey, relations) {
  const rule = findTemplate(relations, judgeKey);
  if (!rule) return "現在の配置に対する断辞が見つかりませんでした。";

  const vars = {
    timeScopeText: TIME_SCOPE_TEXT[judgeKey.timeScope] ?? "現在",
    tiWuxing:      judgeKey.tiWuxing  ?? "",
    youWuxing:     judgeKey.youWuxing ?? "",
    domain:        judgeKey.domain    ?? ""
  };

  return renderTemplate(rule.template, vars);
}
