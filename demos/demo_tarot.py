# ==============================================================================
# demo_tarot.py
# ==============================================================================
# 【TarotEngine 単体動作検証デモ】
# src/fortune_core/tarot_engine.py と data/tarot_cards.json が正しく
# 動作するかをターミナル上で確認するためのデモ実行スクリプト。
#
# 実行方法:
#     # リポジトリルートから
#     python src/fortune_core/demo_tarot.py
#
#     # または fortune_core パッケージとしてインポート済みの場合
#     python -m fortune_core.demo_tarot
#
# 動作確認項目:
#     1. TarotEngine の初期化
#     2. タイムスタンプ（ミリ秒）をシードとして draw_celtic_cross を実行
#     3. ケルト十字（10 枚）の結果を整形表示（カードデザイン選択可）
#     4. スプレッド全体の元素分布バランスを分析・出力
# ==============================================================================

import sys
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# パス解決: 直接実行 / パッケージ実行 どちらでも動くように
# ---------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
_SRC_DIR   = _THIS_FILE.parent.parent   # src/
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from fortune_core.tarot_engine import TarotEngine  # noqa: E402

# ---------------------------------------------------------------------------
# 表示用定数
# ---------------------------------------------------------------------------
WIDTH      = 72
DIVIDER    = "─" * WIDTH
THICK_LINE = "═" * WIDTH
STAR_LINE  = "★" * WIDTH

# ケルト十字 各ポジションの意味（英名 → 日本語）
POSITION_MEANING: dict[str, str] = {
    "present":       "現在の状況",
    "challenge":     "課題・交差するもの",
    "past":          "過去の影響",
    "future":        "近未来の方向性",
    "above":         "意識・目標",
    "below":         "潜在意識・基盤",
    "advice":        "アドバイス",
    "external":      "外部環境・他者の影響",
    "hopes_fears":   "希望と恐れ",
    "outcome":       "最終的な結末",
    # engine が別のキー名を使う場合に備えた追加マッピング
    "significator":  "本人・中心テーマ",
    "crossing":      "課題・交差するもの",
    "foundation":    "潜在意識・基盤",
    "recent_past":   "過去の影響",
    "crowning":      "意識・目標",
    "near_future":   "近未来の方向性",
    "self":          "アドバイス",
    "environment":   "外部環境・他者の影響",
    "inner_hopes":   "希望と恐れ",
    "final_outcome": "最終的な結末",
}

# 元素の日本語ラベル
ELEMENT_LABEL: dict[str, str] = {
    "fire":   "🔥 火（ワンド）",
    "water":  "💧 水（カップ）",
    "air":    "🌬 風（ソード）",
    "earth":  "🌿 地（ペンタクル）",
    "spirit": "✨ 霊（大アルカナ）",
    "major":  "✨ 大アルカナ",
    # 日本語キーにも対応
    "火":     "🔥 火（ワンド）",
    "水":     "💧 水（カップ）",
    "風":     "🌬 風（ソード）",
    "地":     "🌿 地（ペンタクル）",
    "霊":     "✨ 霊（大アルカナ）",
}

BAR_MAX_WIDTH = 30

# ---------------------------------------------------------------------------
# カードデザイン定義
# ---------------------------------------------------------------------------
CARD_DESIGNS: dict[str, dict] = {
    "1": {
        "label":      "✦ クラシック（Standard）",
        "border":     "─",
        "vborder":    "│",
        "corner_tl":  "┌",
        "corner_tr":  "┐",
        "corner_bl":  "└",
        "corner_br":  "┘",
        "deco_top":   "  ～ ✧ ～  ",
        "deco_bot":   "  ～ ✧ ～  ",
        "header_icon": "🃏",
        "orient_up":  "[ 正位置 ↑ ]",
        "orient_rev": "[ 逆位置 ↓ ]",
    },
    "2": {
        "label":      "🌙 ミスティック（Mystic Moon）",
        "border":     "═",
        "vborder":    "║",
        "corner_tl":  "╔",
        "corner_tr":  "╗",
        "corner_bl":  "╚",
        "corner_br":  "╝",
        "deco_top":   "  ☽ ✦ ☾  ",
        "deco_bot":   "  ☾ ✦ ☽  ",
        "header_icon": "🌙",
        "orient_up":  "≪ 正位置 ✦ ≫",
        "orient_rev": "≪ 逆位置 ☽ ≫",
    },
    "3": {
        "label":      "🔮 サイバー（Cyber Neon）",
        "border":     "━",
        "vborder":    "┃",
        "corner_tl":  "┏",
        "corner_tr":  "┓",
        "corner_bl":  "┗",
        "corner_br":  "┛",
        "deco_top":   "  ◈ ▸▸ ◈  ",
        "deco_bot":   "  ◈ ◂◂ ◈  ",
        "header_icon": "⬡",
        "orient_up":  "▲ UPRIGHT ▲",
        "orient_rev": "▼ REVERSED ▼",
    },
    "4": {
        "label":      "🌸 和風（Japanese Style）",
        "border":     "＝",
        "vborder":    "｜",
        "corner_tl":  "【",
        "corner_tr":  "】",
        "corner_bl":  "【",
        "corner_br":  "】",
        "deco_top":   "  ❁ ✿ ❁  ",
        "deco_bot":   "  ❀ ✿ ❀  ",
        "header_icon": "🌸",
        "orient_up":  "〔 正位置 〕",
        "orient_rev": "〔 逆位置 〕",
    },
    "5": {
        "label":      "⚡ シンプル（Plain ASCII）",
        "border":     "-",
        "vborder":    "|",
        "corner_tl":  "+",
        "corner_tr":  "+",
        "corner_bl":  "+",
        "corner_br":  "+",
        "deco_top":   "  * * *  ",
        "deco_bot":   "  * * *  ",
        "header_icon": ">",
        "orient_up":  "(upright)",
        "orient_rev": "(reversed)",
    },
}

# ---------------------------------------------------------------------------
# ユーティリティ
# ---------------------------------------------------------------------------

def display_width(text: str) -> int:
    """全角文字を幅 2、半角を幅 1 として表示幅を返す"""
    return sum(2 if ord(c) > 0x7F else 1 for c in text)


def center_text(text: str, width: int = WIDTH) -> str:
    """表示幅を考慮してセンタリングした文字列を返す"""
    dw  = display_width(text)
    pad = max(0, width - dw)
    return " " * (pad // 2) + text + " " * (pad - pad // 2)


def ljust_display(text: str, width: int) -> str:
    """表示幅を考慮した左揃えパディングを返す"""
    pad = max(0, width - display_width(text))
    return text + " " * pad


def wrap_text(text: str, max_display_width: int = 52) -> list[str]:
    """
    全角/半角混在テキストを表示幅で折り返してリストで返す。
    バグ修正: words / current_len の未使用・未初期化を解消。
    """
    lines:         list[str] = []
    current_line:  str       = ""
    current_width: int       = 0

    for char in str(text):
        cw = 2 if ord(char) > 0x7F else 1
        if current_width + cw > max_display_width:
            lines.append(current_line)
            current_line  = char
            current_width = cw
        else:
            current_line  += char
            current_width += cw

    if current_line:
        lines.append(current_line)

    return lines


def make_bar(ratio: float, max_width: int = BAR_MAX_WIDTH) -> str:
    filled = round(ratio * max_width)
    return "█" * filled + "░" * (max_width - filled)


# ---------------------------------------------------------------------------
# カードデータ正規化（dict / object 両対応）
# ---------------------------------------------------------------------------

def _getval(card, *keys):
    """card が dict でもオブジェクトでも最初に非 None な値を返す"""
    for k in keys:
        v = card.get(k) if isinstance(card, dict) else getattr(card, k, None)
        if v is not None and v != "":
            return v
    return None


def extract_card_fields(card, index: int) -> dict:
    """card（dict / オブジェクト）から表示に必要なフィールドをまとめて返す"""
    pos_key   = str(_getval(card, "position_key", "position") or "").lower()
    pos_name  = str(_getval(card, "position_name", "position") or f"Position {index}")
    card_name = str(_getval(card, "name", "card_name")         or "（不明）")
    element   = str(_getval(card, "element", "suit")           or "—")
    meaning_u = str(_getval(card, "meaning_upright", "meaning") or "")
    meaning_r = str(_getval(card, "meaning_reversed")          or "")
    keywords  = _getval(card, "keywords", "key_themes")        or ""

    if isinstance(card, dict):
        is_reversed = bool(card.get("is_reversed", card.get("reversed", False)))
    else:
        is_reversed = bool(
            getattr(card, "is_reversed", getattr(card, "reversed", False))
        )

    if isinstance(keywords, list):
        keywords = "・".join(str(k) for k in keywords)
    else:
        keywords = str(keywords)

    display_meaning = (meaning_r if (is_reversed and meaning_r) else meaning_u) or meaning_r

    return {
        "pos_key":     pos_key,
        "pos_name":    pos_name,
        "card_name":   card_name,
        "is_reversed": is_reversed,
        "element":     element,
        "keywords":    keywords,
        "meaning":     display_meaning,
    }


def resolve_position_ja(pos_key: str) -> str:
    """ポジションキーから日本語説明を引く（部分一致フォールバック付き）"""
    ja = POSITION_MEANING.get(pos_key, "")
    if not ja:
        for k, v in POSITION_MEANING.items():
            if k in pos_key or pos_key in k:
                return v
    return ja


# ---------------------------------------------------------------------------
# draw_celtic_cross 戻り値の正規化
# ---------------------------------------------------------------------------

def normalize_result(result) -> list:
    """
    draw_celtic_cross の戻り値を list[card] に正規化する。
    バグ修正: dict の全 values() をそのまま返す危険なフォールバックを除去。
    """
    if isinstance(result, list):
        return result

    if isinstance(result, dict):
        for key in ("cards", "spread"):
            candidate = result.get(key)
            if isinstance(candidate, list) and candidate:
                return candidate
        return []

    for attr in ("cards", "spread"):
        candidate = getattr(result, attr, None)
        if isinstance(candidate, list) and candidate:
            return candidate

    return []


# ---------------------------------------------------------------------------
# カード枠描画
# ---------------------------------------------------------------------------

def draw_card(
    pos_index:   int,
    pos_name:    str,
    pos_ja:      str,
    card_name:   str,
    is_reversed: bool,
    element:     str,
    keywords:    str,
    meaning:     str,
    design:      dict,
) -> None:
    """指定デザインでカード 1 枚分をターミナルに描画する"""
    b   = design["border"]
    vb  = design["vborder"]
    tl  = design["corner_tl"]
    tr  = design["corner_tr"]
    bl  = design["corner_bl"]
    br  = design["corner_br"]
    ico = design["header_icon"]
    ori = design["orient_rev"] if is_reversed else design["orient_up"]

    # 枠の横幅（両端のコーナー文字を除いたぶん）
    corner_w = display_width(tl) + display_width(tr)
    fill_len = WIDTH - corner_w
    # inner 行：コーナー幅 + vborder × 2 + 両端スペース × 2 = 内部幅
    inner_w = WIDTH - display_width(tl) - display_width(tr) - display_width(vb) * 2 - 2

    def hline(left_corner: str, right_corner: str) -> str:
        lw  = display_width(left_corner)
        rw  = display_width(right_corner)
        rep = WIDTH - lw - rw
        return left_corner + b * rep + right_corner

    def inner_line(content: str = "") -> str:
        cw  = display_width(content)
        pad = max(0, inner_w - cw)
        return f"{vb} {content}{' ' * pad} {vb}"

    elem_label = ELEMENT_LABEL.get(element, element)

    # ── 描画 ──
    print()
    print(hline(tl, tr))
    print(inner_line(design["deco_top"]))

    pos_str = f"  {pos_index:2d}. {pos_name}"
    if pos_ja:
        pos_str += f"  /  {pos_ja}"
    print(inner_line(pos_str))
    print(inner_line())
    print(inner_line(f"{ico}  {card_name}"))
    print(inner_line(f"     {ori}"))
    print(inner_line(f"     🌊 {elem_label}"))

    if keywords:
        print(inner_line(f"     🔑 {keywords}"))

    if meaning:
        print(inner_line())
        print(inner_line("  📖 解釈:"))
        for line in wrap_text(meaning, max_display_width=inner_w - 6):
            print(inner_line(f"     {line}"))

    print(inner_line(design["deco_bot"]))
    print(hline(bl, br))


# ---------------------------------------------------------------------------
# カードデザイン選択インタラクション
# ---------------------------------------------------------------------------

def choose_design() -> dict:
    """ターミナルでデザイン番号を入力させ、選択した design dict を返す"""
    print()
    print(THICK_LINE)
    print(center_text("🎨  カードデザインを選んでください  🎨"))
    print(THICK_LINE)
    for key, d in CARD_DESIGNS.items():
        print(f"  [{key}]  {d['label']}")
    print(DIVIDER)

    while True:
        try:
            choice = input("  番号を入力してください（デフォルト: 1）> ").strip()
        except (EOFError, KeyboardInterrupt):
            choice = ""

        if choice == "":
            choice = "1"

        if choice in CARD_DESIGNS:
            selected = CARD_DESIGNS[choice]
            print(f"  ✅ 選択されたデザイン: {selected['label']}")
            return selected

        print(f"  ⚠️  '{choice}' は無効です。1〜{len(CARD_DESIGNS)} の番号を入力してください。")


# ---------------------------------------------------------------------------
# 元素分布バランス表示
# ---------------------------------------------------------------------------

def show_element_analysis(cards: list) -> None:
    """スプレッド全体の元素分布を集計・表示する"""
    print()
    print(STAR_LINE)
    print(center_text("📊  元素分布バランス分析"))
    print(STAR_LINE)

    element_counter: dict[str, int] = {}
    for card in cards:
        if isinstance(card, dict):
            elem = card.get("element") or card.get("suit") or "不明"
        else:
            elem = getattr(card, "element", None) or getattr(card, "suit", None) or "不明"
        elem = str(elem).strip()
        element_counter[elem] = element_counter.get(elem, 0) + 1

    total = sum(element_counter.values())

    if total == 0:
        print("  元素データを取得できませんでした。")
        return

    print()
    print(f"  スプレッド合計: {total} 枚")
    print()

    # ヘッダー（全角考慮で手動パディング）
    print(
        f"  {ljust_display('元素', 18)}"
        f"  {ljust_display('枚数', 6)}"
        f"  {ljust_display('割合', 7)}"
        f"  グラフ"
    )
    print(f"  {'─' * 18}  {'─' * 6}  {'─' * 7}  {'─' * BAR_MAX_WIDTH}")

    for elem, count in sorted(element_counter.items(), key=lambda x: -x[1]):
        ratio = count / total
        pct   = ratio * 100
        label = ELEMENT_LABEL.get(elem, f"  {elem}")
        bar   = make_bar(ratio)
        print(
            f"  {ljust_display(label, 18)}"
            f"  {ljust_display(str(count) + '枚', 6)}"
            f"  {ljust_display(f'{pct:5.1f}%', 7)}"
            f"  {bar}"
        )

    # バランスコメント
    print()
    print(f"  {'─' * (WIDTH - 4)}")
    max_elem  = max(element_counter, key=element_counter.get)  # type: ignore[arg-type]
    max_ratio = element_counter[max_elem] / total * 100
    max_label = ELEMENT_LABEL.get(max_elem, max_elem)

    print(f"  最も多い元素: {max_label}  ({max_ratio:.1f}%)")
    if max_ratio >= 50:
        print("  → 特定元素への偏りが強く、そのテーマが今回の中心課題です。")
    elif max_ratio >= 30:
        print("  → 1つの元素が主導的ですが、全体的に多様なテーマが混在しています。")
    else:
        print("  → 各元素がバランスよく分布しており、多面的な状況を示しています。")

    # 大アルカナ比率チェック
    major_keys  = {"major", "spirit", "霊", "大アルカナ", "Major Arcana"}
    major_count = sum(v for k, v in element_counter.items() if k in major_keys)
    if major_count > 0:
        major_pct = major_count / total * 100
        print()
        print(f"  大アルカナ比率: {major_count}枚 / {major_pct:.1f}%")
        if major_pct >= 40:
            print("  → 宿命的・大局的な力が強く働いており、重要な転換期を示唆します。")
        else:
            print("  → 自由意志と宿命が程よく混在するスプレッドです。")


# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------

def main() -> None:

    # ── ヘッダー ────────────────────────────────────────────────────────────
    print()
    print(THICK_LINE)
    print(center_text("🔮  fortune-core  /  TarotEngine  単体動作検証デモ  🔮"))
    print(center_text("Celtic Cross Spread  ―  ケルト十字スプレッド"))
    print(THICK_LINE)

    # ── カードデザイン選択 ─────────────────────────────────────────────────
    design = choose_design()

    # ── Step 1: TarotEngine 初期化 ─────────────────────────────────────────
    print()
    print(f"{'▶ Step 1 ':─<{WIDTH}}")
    print("  TarotEngine を初期化しています...")
    try:
        engine = TarotEngine()
        print("  ✅ TarotEngine の初期化に成功しました。")
    except Exception as exc:
        print(f"  ❌ TarotEngine の初期化に失敗しました: {exc}")
        print("\n  【確認事項】")
        print("  - src/fortune_core/tarot_engine.py が存在しますか？")
        print("  - src/fortune_core/data/tarot_cards.json が存在しますか？")
        print("  - pip install -e . でパッケージをインストールしましたか？")
        sys.exit(1)

    # ── Step 2: シード取得 ─────────────────────────────────────────────────
    print()
    print(f"{'▶ Step 2 ':─<{WIDTH}}")
    user_seed = int(time.time() * 1000)
    print("  占い師がシャッフルを止めた瞬間のタイムスタンプ（ms）:")
    print(f"  user_seed = {user_seed}")

    # ── Step 3: クエリ設定 ─────────────────────────────────────────────────
    print()
    print(f"{'▶ Step 3 ':─<{WIDTH}}")
    query = "この占いアプリケーション開発プロジェクトの今後の進展について"
    print(f"  相談内容: 「{query}」")

    # ── Step 4: draw_celtic_cross 実行 ─────────────────────────────────────
    print()
    print(f"{'▶ Step 4 ':─<{WIDTH}}")
    print("  ケルト十字スプレッドを展開しています...")

    # 引数バリエーションを順に試す（engine のシグネチャ違いに対応）
    result      = None
    arg_variants = [
        {"user_seed": user_seed, "query": query},
        {"seed":      user_seed, "query": query},
        {"user_seed": user_seed},
        {"seed":      user_seed},
    ]
    for kwargs in arg_variants:
        try:
            result = engine.draw_celtic_cross(**kwargs)
            print(f"  ✅ draw_celtic_cross({', '.join(f'{k}=...' for k in kwargs)}) 成功")
            break
        except TypeError:
            continue
        except Exception as exc:
            print(f"  ❌ draw_celtic_cross の実行中にエラーが発生しました: {exc}")
            sys.exit(1)

    if result is None:
        print("  ❌ draw_celtic_cross を呼び出せる引数の組み合わせが見つかりませんでした。")
        print("     tarot_engine.py の draw_celtic_cross シグネチャを確認してください。")
        sys.exit(1)

    cards = normalize_result(result)

    if not cards:
        print("  ❌ 結果からカードリストを取得できませんでした。")
        print(f"     result の型   : {type(result)}")
        print(f"     result の内容 : {result!r}")
        sys.exit(1)

    print(f"  📌 取得カード枚数: {len(cards)} 枚")

    # ── Step 5: スプレッド表示 ─────────────────────────────────────────────
    print()
    print(STAR_LINE)
    print(center_text("🃏  ケルト十字スプレッド  結果  🃏"))
    print(center_text(f"相談: 「{query}」"))
    print(STAR_LINE)

    for i, card in enumerate(cards, start=1):
        fields = extract_card_fields(card, i)
        pos_ja = resolve_position_ja(fields["pos_key"])
        draw_card(
            pos_index   = i,
            pos_name    = fields["pos_name"],
            pos_ja      = pos_ja,
            card_name   = fields["card_name"],
            is_reversed = fields["is_reversed"],
            element     = fields["element"],
            keywords    = fields["keywords"],
            meaning     = fields["meaning"],
            design      = design,
        )

    print()
    print(center_text(f"以上、{len(cards)} 枚のカードが展開されました。"))

    # ── Step 6: 元素分布バランス分析 ──────────────────────────────────────
    show_element_analysis(cards)

    # ── フッター ─────────────────────────────────────────────────────────────
    print()
    print(THICK_LINE)
    print(center_text("✅  デモ実行完了  ―  TarotEngine は正常に動作しています"))
    print(THICK_LINE)
    print()


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()