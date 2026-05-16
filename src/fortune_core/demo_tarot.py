""
demo_tarot.py
=============

【TarotEngine 単体動作検証デモ】
src/fortune_core/tarot_engine.py と data/tarot_cards.json が正しく
動作するかをターミナル上で確認するためのデモ実行スクリプト。

実行方法:
    # リポジトリルートから
    python src/fortune_core/demo_tarot.py

    # または fortune_core パッケージとしてインポート済みの場合
    python -m fortune_core.demo_tarot

動作確認項目:
    1. TarotEngine の初期化
    2. タイムスタンプ（ミリ秒）をシードとして draw_celtic_cross を実行
    3. ケルト十字（10 枚）の結果を整形表示
    4. スプレッド全体の元素分布バランスを分析・出力
"""

import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# パス解決: 直接実行 / パッケージ実行 どちらでも動くように
# ---------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
_SRC_DIR   = _THIS_FILE.parent.parent          # src/
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from fortune_core.tarot_engine import TarotEngine  # noqa: E402

# ---------------------------------------------------------------------------
# 表示用定数
# ---------------------------------------------------------------------------
WIDTH       = 72          # ターミナル横幅（文字数）
DIVIDER     = "─" * WIDTH
THICK_LINE  = "═" * WIDTH
STAR_LINE   = "★" * WIDTH

# ケルト十字 各ポジションの意味（英名 → 日本語）
POSITION_MEANING: dict[str, str] = {
    "present":           "現在の状況",
    "challenge":         "課題・交差するもの",
    "past":              "過去の影響",
    "future":            "近未来の方向性",
    "above":             "意識・目標",
    "below":             "潜在意識・基盤",
    "advice":            "アドバイス",
    "external":          "外部環境・他者の影響",
    "hopes_fears":       "希望と恐れ",
    "outcome":           "最終的な結末",
    # engine が別のキー名を使う場合に備えた追加マッピング
    "significator":      "本人・中心テーマ",
    "crossing":          "課題・交差するもの",
    "foundation":        "潜在意識・基盤",
    "recent_past":       "過去の影響",
    "crowning":          "意識・目標",
    "near_future":       "近未来の方向性",
    "self":              "アドバイス",
    "environment":       "外部環境・他者の影響",
    "inner_hopes":       "希望と恐れ",
    "final_outcome":     "最終的な結末",
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

ELEMENT_BAR_CHAR = "█"
BAR_MAX_WIDTH    = 30   # プログレスバーの最大幅（文字数）


# ---------------------------------------------------------------------------
# ユーティリティ
# ---------------------------------------------------------------------------

def center(text: str, width: int = WIDTH) -> str:
    """文字列を幅に合わせてセンタリング（全角対応の簡易版）"""
    # 全角文字を幅 2 として計算
    display_len = sum(2 if ord(c) > 0x7F else 1 for c in text)
    pad = max(0, width - display_len)
    left  = pad // 2
    right = pad - left
    return " " * left + text + " " * right


def ljust_wide(text: str, width: int) -> str:
    """全角考慮の左揃え"""
    display_len = sum(2 if ord(c) > 0x7F else 1 for c in text)
    pad = max(0, width - display_len)
    return text + " " * pad


def orientation_label(is_reversed: bool) -> str:
    return "🔄 逆位置" if is_reversed else "⬆️  正位置"


def make_bar(ratio: float, max_width: int = BAR_MAX_WIDTH) -> str:
    filled = round(ratio * max_width)
    return ELEMENT_BAR_CHAR * filled + "░" * (max_width - filled)


def safe_get(obj, *keys, default=""):
    """ネストしたdict/objectから安全に値を取得"""
    for key in keys:
        if obj is None:
            return default
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            obj = getattr(obj, key, None)
    return obj if obj is not None else default


# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------

def main() -> None:

    # ── ヘッダー ────────────────────────────────────────────────────────────
    print()
    print(THICK_LINE)
    print(center("🔮  fortune-core  /  TarotEngine  単体動作検証デモ  🔮"))
    print(center("Celtic Cross Spread  ―  ケルト十字スプレッド"))
    print(THICK_LINE)

    # ── 1. TarotEngine 初期化 ───────────────────────────────────────────────
    print(f"\n{'▶ Step 1':─<{WIDTH}}")
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

    # ── 2. シード取得 ────────────────────────────────────────────────────────
    print(f"\n{'▶ Step 2':─<{WIDTH}}")
    user_seed = int(time.time() * 1000)
    print(f"  占い師がシャッフルを止めた瞬間のタイムスタンプ（ms）:")
    print(f"  user_seed = {user_seed}")

    # ── 3. クエリ設定 ────────────────────────────────────────────────────────
    print(f"\n{'▶ Step 3':─<{WIDTH}}")
    query = "この占いアプリケーション開発プロジェクトの今後の進展について"
    print(f"  相談内容: 「{query}」")

    # ── 4. draw_celtic_cross 実行 ────────────────────────────────────────────
    print(f"\n{'▶ Step 4':─<{WIDTH}}")
    print("  ケルト十字スプレッドを展開しています...")
    try:
        result = engine.draw_celtic_cross(user_seed=user_seed, query=query)
        print("  ✅ draw_celtic_cross の実行に成功しました。")
    except TypeError:
        # 引数名が異なる engine に対するフォールバック
        try:
            result = engine.draw_celtic_cross(seed=user_seed, query=query)
            print("  ✅ draw_celtic_cross の実行に成功しました（seed= 引数を使用）。")
        except Exception as exc2:
            print(f"  ❌ draw_celtic_cross の実行に失敗しました: {exc2}")
            sys.exit(1)
    except Exception as exc:
        print(f"  ❌ draw_celtic_cross の実行に失敗しました: {exc}")
        sys.exit(1)

    # result の型を正規化（list / dict どちらにも対応）
    if isinstance(result, dict):
        cards = result.get("cards", result.get("spread", list(result.values())))
    elif isinstance(result, list):
        cards = result
    else:
        # オブジェクトの場合
        cards = getattr(result, "cards", None) or getattr(result, "spread", [])

    if not cards:
        print("  ❌ 結果からカードリストを取得できませんでした。")
        print(f"     result の型: {type(result)}")
        print(f"     result の内容: {result}")
        sys.exit(1)

    # ── スプレッド表示 ────────────────────────────────────────────────────────
    print()
    print(STAR_LINE)
    print(center("🃏  ケルト十字スプレッド  結果  🃏"))
    print(center(f"相談: 「{query}」"))
    print(STAR_LINE)

    for i, card in enumerate(cards, start=1):
        # --- カードデータを dict / object 両対応で取得 ---
        if isinstance(card, dict):
            pos_key     = (card.get("position_key") or card.get("position") or "").lower()
            pos_name    = card.get("position_name") or card.get("position") or f"Position {i}"
            card_name   = card.get("name") or card.get("card_name") or "（不明）"
            is_reversed = card.get("is_reversed", card.get("reversed", False))
            element     = card.get("element") or card.get("suit") or "—"
            meaning_u   = card.get("meaning_upright") or card.get("meaning") or card.get("keywords") or ""
            meaning_r   = card.get("meaning_reversed") or ""
            keywords    = card.get("keywords") or card.get("key_themes") or ""
        else:
            pos_key     = (getattr(card, "position_key", "") or getattr(card, "position", "") or "").lower()
            pos_name    = getattr(card, "position_name", None) or getattr(card, "position", f"Position {i}")
            card_name   = getattr(card, "name", None) or getattr(card, "card_name", "（不明）")
            is_reversed = getattr(card, "is_reversed", getattr(card, "reversed", False))
            element     = getattr(card, "element", None) or getattr(card, "suit", "—")
            meaning_u   = getattr(card, "meaning_upright", None) or getattr(card, "meaning", "") or ""
            meaning_r   = getattr(card, "meaning_reversed", "") or ""
            keywords    = getattr(card, "keywords", "") or getattr(card, "key_themes", "") or ""

        # ポジション日本語説明の取得
        pos_ja = POSITION_MEANING.get(pos_key, "")
        if not pos_ja:
            # 部分一致で検索
            for k, v in POSITION_MEANING.items():
                if k in pos_key or pos_key in k:
                    pos_ja = v
                    break

        # 表示する意味テキストの選択（正逆に応じて）
        if is_reversed and meaning_r:
            display_meaning = meaning_r
        else:
            display_meaning = meaning_u or meaning_r

        # keywords が list の場合は文字列化
        if isinstance(keywords, list):
            keywords = "・".join(str(k) for k in keywords)

        # --- 出力 ---
        print()
        print(DIVIDER)
        # ポジションヘッダー
        pos_header = f"  【{i:2d}】 {pos_name}"
        if pos_ja:
            pos_header += f"  ―  {pos_ja}"
        print(pos_header)
        print(DIVIDER)

        # カード名 + 正逆
        orient = orientation_label(is_reversed)
        print(f"  🃏 カード名  : {card_name}")
        print(f"  {orient}")
        print(f"  🌊 元素/スート: {element}")

        # キーワード（ある場合）
        if keywords:
            print(f"  🔑 キーワード: {keywords}")

        # 意味テキスト（折り返し表示）
        if display_meaning:
            print(f"  📖 解釈テキスト:")
            # 全角・半角混在での折り返し（簡易版: 50文字ごと）
            text = str(display_meaning)
            line_width = 50
            words = ""
            current_len = 0
            buf_lines = []
            current_line = ""
            for char in text:
                w = 2 if ord(char) > 0x7F else 1
                if current_len + w > line_width:
                    buf_lines.append(current_line)
                    current_line = char
                    current_len  = w
                else:
                    current_line += char
                    current_len  += w
            if current_line:
                buf_lines.append(current_line)
            for line in buf_lines:
                print(f"     {line}")

    print()
    print(DIVIDER)
    print(center("以上、10枚のカードが展開されました。"))
    print(DIVIDER)

    # ── 5. 元素分布バランス分析 ─────────────────────────────────────────────
    print()
    print(STAR_LINE)
    print(center("📊  元素分布バランス分析"))
    print(STAR_LINE)

    element_counter: dict[str, int] = {}
    total = 0

    for card in cards:
        if isinstance(card, dict):
            elem = card.get("element") or card.get("suit") or "不明"
        else:
            elem = getattr(card, "element", None) or getattr(card, "suit", None) or "不明"

        # 文字列の正規化（小文字化）
        elem = str(elem).strip()
        element_counter[elem] = element_counter.get(elem, 0) + 1
        total += 1

    if total == 0:
        print("  元素データを取得できませんでした。")
    else:
        print()
        print(f"  スプレッド合計: {total} 枚")
        print()
        print(f"  {'元素':16s}  {'枚数':>4s}  {'割合':>6s}  グラフ")
        print(f"  {'─'*16}  {'─'*4}  {'─'*6}  {'─'*BAR_MAX_WIDTH}")

        # 枚数の多い順にソート
        for elem, count in sorted(element_counter.items(), key=lambda x: -x[1]):
            ratio     = count / total
            pct       = ratio * 100
            label     = ELEMENT_LABEL.get(elem, f"　{elem}")
            bar       = make_bar(ratio)
            print(f"  {ljust_wide(label, 18)}  {count:>4d}枚  {pct:>5.1f}%  {bar}")

        print()
        # バランスコメント
        max_elem  = max(element_counter, key=element_counter.get)
        max_ratio = element_counter[max_elem] / total * 100
        max_label = ELEMENT_LABEL.get(max_elem, max_elem)

        print("  ── バランスコメント ──────────────────────────────────────────")
        print(f"  最も多い元素: {max_label}  ({max_ratio:.1f}%)")

        if max_ratio >= 50:
            print("  → 特定元素への偏りが強く、そのテーマが今回の中心課題です。")
        elif max_ratio >= 30:
            print("  → 1つの元素が主導的ですが、全体的に多様なテーマが混在しています。")
        else:
            print("  → 各元素がバランスよく分布しており、多面的な状況を示しています。")

        # 大アルカナ比率チェック
        major_keys = {"major", "spirit", "霊", "大アルカナ", "Major Arcana"}
        major_count = sum(v for k, v in element_counter.items() if k in major_keys)
        if major_count > 0:
            major_pct = major_count / total * 100
            print(f"\n  大アルカナ比率: {major_count}枚 / {major_pct:.1f}%")
            if major_pct >= 40:
                print("  → 宿命的・大局的な力が強く働いており、重要な転換期を示唆します。")
            else:
                print("  → 自由意志と宿命が程よく混在するスプレッドです。")

    # ── フッター ─────────────────────────────────────────────────────────────
    print()
    print(THICK_LINE)
    print(center("✅  デモ実行完了  ―  TarotEngine は正常に動作しています"))
    print(THICK_LINE)
    print()


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
