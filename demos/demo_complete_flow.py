"""
demo_complete_flow.py
=====================

fortune-core の完全フロー デモンストレーション：
1. 占いの入り口（相談内容入力→占術自動マッチング）
2. ケルト十字スプレッド実行
3. 鑑定結果のレポート生成・保存

実行方法:
    python src/fortune_core/demo_complete_flow.py
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

_THIS_FILE = Path(__file__).resolve()
_SRC_DIR = _THIS_FILE.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from fortune_core.divination_entry import DivineEntryEngine
from fortune_core.tarot_engine import TarotEngine
from fortune_core.report_generator import ReportGenerator, ReadingReport


# ==============================================================================
# デモ用ユーティリティ
# ==============================================================================

def print_header(title: str):
    """ヘッダー表示"""
    WIDTH = 80
    print("\n" + "=" * WIDTH)
    print(f"  {title.center(WIDTH - 4)}")
    print("=" * WIDTH + "\n")


def print_section(title: str):
    """セクション表示"""
    print(f"\n【 {title} 】\n")


def print_divider():
    """区切り線"""
    print("-" * 80)


def safe_input(prompt: str, default: str = "") -> str:
    """安全な入力取得"""
    try:
        result = input(prompt)
        return result if result.strip() else default
    except (EOFError, KeyboardInterrupt):
        return default


# ==============================================================================
# デモ実行
# ==============================================================================

def demo_complete_flow():
    """完全フロー デモ"""
    
    print_header("🔮 fortune-core 完全フロー デモンストレーション 🔮")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 1: 占いの入り口
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("STEP 1️⃣ : 占いの入り口 - 相談内容のヒアリング")
    print("""
今、どのようなことで悩んでいますか？

【相談内容の例】
  • 「今のプロジェクトをどう進めるべきか？」
  • 「3ヶ月後の転職の行方は？」
  • 「彼との関係は今後どうなる？」
  • 「自分の適職は何か？」
  • 「引っ越しに最適な方位は？」
""")
    
    # サンプル相談内容（インタラクティブか固定か）
    sample_queries = [
        "今のプロジェクトをどう進めるべきか？状況が複雑で、チーム内の意見も割れています。",
        "彼との関係は今後どうなりますか？結婚を考えていますが、彼の気持ちが不安です。",
        "転職を考えていますが、本当に今の会社を辞めるべきでしょうか？",
    ]
    
    print("\n【サンプル相談内容（デモ用）】")
    for i, query in enumerate(sample_queries, 1):
        print(f"  [{i}] {query}")
    
    choice = safe_input("\nいずれか選択してください [1-3] (デフォルト: 1): ", "1")
    
    try:
        query_idx = int(choice) - 1
        if 0 <= query_idx < len(sample_queries):
            query_text = sample_queries[query_idx]
        else:
            query_text = sample_queries[0]
    except ValueError:
        query_text = sample_queries[0]
    
    print(f"\n✓ 相談内容: 「{query_text}」\n")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 2: 占術自動マッチング
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("STEP 2️⃣ : 占術自動マッチング")
    print("AIがあなたの相談内容を分析し、最適な占術を判定しています...")
    time.sleep(0.5)
    
    entry_engine = DivineEntryEngine()
    entry = entry_engine.create_entry(query_text)
    recommendation = entry.recommendation
    
    print(f"\n✓ 分析完了！")
    print(f"  カテゴリ: {entry.concern_type}")
    print(f"  推奨占術: {recommendation.divination_type}")
    print(f"  確度: {recommendation.confidence:.0%}\n")
    
    print(recommendation.reasoning + "\n")
    
    print_divider()
    print("\n" + recommendation.user_guidance + "\n")
    print_divider()
    
    # フォローアップ質問
    follow_ups = entry_engine.suggest_follow_up_questions(entry)
    if follow_ups:
        print("\n【次のステップ】")
        for i, q in enumerate(follow_ups[:2], 1):
            print(f"  {i}. {q}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 3: ケルト十字スプレッド実行
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("STEP 3️⃣ : ケルト十字スプレッド実行")
    print("TarotEngine を初期化しています...")
    
    try:
        tarot_engine = TarotEngine()
        print("✓ エンジン初期化完了！\n")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return
    
    # シンクロニシティシード（現在のミリ秒タイムスタンプ）
    user_seed = int(time.time() * 1000)
    
    print(f"相談内容を心に思い浮かべながら、シャッフルします...")
    print(f"（シンクロシード: {user_seed}）\n")
    
    # スプレッド実行
    reading_result = tarot_engine.draw_celtic_cross(user_seed, query_text)
    
    print("✓ 10枚のカードが展開されました！\n")
    
    # 結果表示
    print("【ケルト十字スプレッド結果】\n")
    positions = reading_result.get("positions", {})
    
    position_labels = {
        "CURRENT_SITUATION": "① 現在の状況",
        "CROSSING_CHALLENGE": "② 課題・交差するもの",
        "DISTANT_PAST": "③ 遠い過去・根底",
        "RECENT_PAST": "④ 近い過去の影響",
        "BEST_OUTCOME": "⑤ 意識・最善の結果",
        "IMMEDIATE_FUTURE": "⑥ 近未来の方向性",
        "SELF_PERCEPTION": "⑦ 自己認識・内面",
        "EXTERNAL_INFLUENCES": "⑧ 外部環境・他者の影響",
        "HOPES_AND_FEARS": "⑨ 希望と恐れ",
        "FINAL_OUTCOME": "⑩ 最終的な結末",
    }
    
    for pos_key, pos_data in positions.items():
        card = pos_data.get("card", {})
        is_reversed = pos_data.get("is_reversed", False)
        card_name = card.get("name", "Unknown")
        element = card.get("element", "?")
        meaning_key = "meaning_reversed" if is_reversed else "meaning_upright"
        meaning = card.get(meaning_key, "")
        
        label = position_labels.get(pos_key, f"? {pos_key}")
        orientation = "🔄 逆位置" if is_reversed else "✓ 正位置"
        
        print(f"{label}")
        print(f"  カード: {card_name} [{element}]")
        print(f"  向き: {orientation}")
        print(f"  解釈: {meaning[:60]}...\n" if len(meaning) > 60 else f"  解釈: {meaning}\n")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 4: 要素バランス分析
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("STEP 4️⃣ : 要素バランス分析")
    
    element_dist = {}
    for pos_data in positions.values():
        card = pos_data.get("card", {})
        element = card.get("element", "unknown")
        element_dist[element] = element_dist.get(element, 0) + 1
    
    element_emojis = {
        "fire": "🔥 火（ワンド）",
        "water": "💧 水（カップ）",
        "air": "🌬 風（ソード）",
        "earth": "🌿 地（ペンタクル）",
        "spirit": "✨ 霊（大アルカナ）",
    }
    
    print("このスプレッドの要素分布:\n")
    for element, count in element_dist.items():
        label = element_emojis.get(element, f"? {element}")
        bar = "■" * count + "□" * (10 - count)
        print(f"  {label:<20} {bar} ({count})")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 5: レポート生成・保存
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("STEP 5️⃣ : 鑑定結果レポート生成")
    
    # Reading ID 生成
    reading_id = f"reading_{user_seed}"
    
    # ReportData 構築
    report = ReadingReport(
        reading_id=reading_id,
        query_text=query_text,
        timestamp=datetime.now().isoformat(),
        divination_type=recommendation.divination_type,
        positions=positions,
        element_distribution=element_dist,
        user_seed=user_seed,
    )
    
    # レポート生成
    report_generator = ReportGenerator()
    
    print("レポートを生成しています...\n")
    
    try:
        export_paths = report_generator.export_formats(report, formats=("json", "html"))
        
        print("✓ レポート生成完了！\n")
        print("【保存ファイル】")
        for fmt, path in export_paths.items():
            print(f"  {fmt.upper()}: {path}")
        
        # JSON プレビュー
        print("\n【JSON データ プレビュー】\n")
        json_str = report_generator.generate_json_report(report)
        json_obj = json.loads(json_str)
        print(json.dumps(
            {
                "reading_id": json_obj["reading_id"],
                "query_text": json_obj["query_text"],
                "timestamp": json_obj["timestamp"],
                "divination_type": json_obj["divination_type"],
                "user_seed": json_obj["user_seed"],
                "element_distribution": json_obj["element_distribution"],
                "positions": "（全10ポジション分のカード情報）",
            },
            ensure_ascii=False,
            indent=2
        ))
        
    except Exception as e:
        print(f"✗ レポート生成エラー: {e}")
        return
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 6: 保存方法ガイド
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("STEP 6️⃣ : 保存方法ガイド")
    
    save_guide = report_generator.get_save_instructions()
    print(save_guide)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 完了
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_header("✨ デモンストレーション完了！ ✨")
    print(f"""
【このデモで実演したもの】
  1️⃣  占いの入り口 - 相談内容の分析と占術自動マッチング
  2️⃣  ケルト十字スプレッド - 10枚のカード展開
  3️⃣  要素バランス分析 - 東洋占術連携の基盤
  4️⃣  レポート生成 - JSON・HTML形式での多形式出力
  5️⃣  ファイル保存 - ユーザーが自分の資産として持ち帰れる機能

【次のステップ】
  • フロントエンド（Web/Mobile）で UI/UX を構築
  • 音声テキスト注入機能で meanings を動的に育成
  • 複数占術の連携・クロスオーバー分析の実装

                🔮 fortune-core へようこそ！ 🔮
""")


if __name__ == "__main__":
    try:
        demo_complete_flow()
    except KeyboardInterrupt:
        print("\n\n中断しました。")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
