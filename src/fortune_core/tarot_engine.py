"""
tarot_engine.py
===============

fortune-core  /  TarotEngine

78 枚のフルデッキから「ケルト十字スプレッド（10枚）」を展開するエンジン。

戻り値フォーマット（draw_celtic_cross）:
    {
        "query":     str,              # ユーザーの相談内容
        "seed":      int,              # user_seed（ミリ秒タイムスタンプ）
        "timestamp": str,              # ISO 8601 形式の鑑定日時
        "spread":    "celtic_cross",
        "positions": {                 # ← キー: ポジション定数名（大文字）
            "CURRENT_SITUATION": {
                "position_label": "現在の状況",
                "position_index": 1,
                "card": { ... },       # tarot_cards.json の cards[n]
                "is_reversed": bool,
            },
            "CROSSING_CHALLENGE": { ... },
            ...（全10ポジション）
        }
    }
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# ポジション定義（挿入順序が展開順）
# ---------------------------------------------------------------------------
CELTIC_CROSS_POSITIONS: list[tuple[str, str]] = [
    ("CURRENT_SITUATION",   "現在の状況"),
    ("CROSSING_CHALLENGE",  "課題・交差するもの"),
    ("DISTANT_PAST",        "遠い過去・根底にあるもの"),
    ("RECENT_PAST",         "近い過去の影響"),
    ("BEST_OUTCOME",        "意識・最善の結果"),
    ("IMMEDIATE_FUTURE",    "近未来の方向性"),
    ("SELF_PERCEPTION",     "自己認識・内面"),
    ("EXTERNAL_INFLUENCES", "外部環境・他者の影響"),
    ("HOPES_AND_FEARS",     "希望と恐れ"),
    ("FINAL_OUTCOME",       "最終的な結末"),
]

# ---------------------------------------------------------------------------
# TarotEngine
# ---------------------------------------------------------------------------

class TarotEngine:
    """
    タロットエンジン。

    初期化時に tarot_cards.json を読み込み、draw_celtic_cross() で
    10枚のケルト十字スプレッドを展開して positions 辞書を返す。

    Parameters
    ----------
    data_path : Path | str | None
        tarot_cards.json のパス。None のとき自動解決。
    """

    def __init__(self, data_path: "Path | str | None" = None) -> None:
        if data_path is None:
            # 優先順 1: このファイルと同じ data/ ディレクトリ
            # 優先順 2: このファイルと同じディレクトリ（フラット配置）
            candidates = [
                Path(__file__).parent / "data" / "tarot_cards.json",
                Path(__file__).parent / "tarot_cards.json",
            ]
            resolved = next((p for p in candidates if p.exists()), None)
            if resolved is None:
                raise FileNotFoundError(
                    "tarot_cards.json が見つかりません。\n"
                    f"  探索パス: {[str(p) for p in candidates]}\n"
                    "  src/fortune_core/data/tarot_cards.json に配置してください。"
                )
            data_path = resolved

        with open(data_path, encoding="utf-8") as f:
            raw = json.load(f)

        self._cards: list[dict] = raw["cards"]
        if len(self._cards) != 78:
            raise ValueError(
                f"tarot_cards.json のカード枚数が {len(self._cards)} 枚です。"
                "78 枚である必要があります。"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw_celtic_cross(
        self,
        user_seed: int,
        query: str = "",
    ) -> dict:
        """
        ケルト十字スプレッド（10枚）を展開する。

        Parameters
        ----------
        user_seed : int
            シャッフルを止めた瞬間のタイムスタンプ（ミリ秒）。
            同じ seed なら常に同じ結果が再現される。
        query : str
            ユーザーの相談内容。

        Returns
        -------
        dict
            {
                "query": str,
                "seed": int,
                "timestamp": str,
                "spread": "celtic_cross",
                "positions": {
                    "CURRENT_SITUATION": {
                        "position_label": str,
                        "position_index": int,
                        "card": dict,
                        "is_reversed": bool,
                    },
                    ...
                }
            }
        """
        rng = random.Random(user_seed)

        # 78 枚をシャッフルして先頭 10 枚を使う
        deck_indices = list(range(len(self._cards)))
        rng.shuffle(deck_indices)
        drawn_indices = deck_indices[:10]

        # 正逆はシードに基づいて独立して決定
        reversed_flags = [rng.random() < 0.35 for _ in range(10)]

        positions: dict[str, dict] = {}
        for i, (pos_key, pos_label) in enumerate(CELTIC_CROSS_POSITIONS):
            card = self._cards[drawn_indices[i]]
            positions[pos_key] = {
                "position_label": pos_label,
                "position_index": i + 1,
                "card":           card,
                "is_reversed":    reversed_flags[i],
            }

        return {
            "query":     query,
            "seed":      user_seed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "spread":    "celtic_cross",
            "positions": positions,
        }

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def all_cards(self) -> list[dict]:
        """デッキ全 78 枚を返す（読み取り専用コピー）"""
        return list(self._cards)

    def card_count(self) -> int:
        """デッキのカード枚数（常に 78）"""
        return len(self._cards)