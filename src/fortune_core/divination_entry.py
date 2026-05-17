"""
divination_entry.py
====================

占いの入り口：ユーザーの相談内容をヒアリングして、
最適な占術（タロット・風水・複合占法）を自動判定・提案するモジュール。

主要機能:
- 相談内容の分類（恋愛、仕事、金運、人間関係、健康など）
- キーワード分析から最適な占術を推薦
- ユーザーに対する提案文の生成
"""

import json
from dataclasses import dataclass
from typing import Literal
from datetime import datetime


# ---------------------------------------------------------------------------
# 定数定義
# ---------------------------------------------------------------------------

DivationType = Literal["tarot_celtic_cross", "feng_shui", "four_pillars", "combined"]
ConcernType = Literal["love", "work", "money", "relationship", "health", "future", "general"]

# 相談カテゴリのキーワードマッピング
CONCERN_KEYWORDS: dict[ConcernType, list[str]] = {
    "love": [
        "恋愛", "彼氏", "彼女", "パートナー", "結婚", "婚活", "片思い",
        "恋", "デート", "告白", "好き", "愛", "愛情", "交際", "関係",
        "love", "romantic", "boyfriend", "girlfriend", "marriage",
    ],
    "work": [
        "仕事", "転職", "職場", "上司", "同僚", "プロジェクト", "キャリア",
        "昇進", "退職", "失業", "起業", "独立", "キャリアパス",
        "work", "job", "career", "employment", "boss", "promotion",
    ],
    "money": [
        "金運", "お金", "給料", "年収", "投資", "株", "ビジネス", "商売",
        "貯金", "借金", "返済", "経営", "利益", "収入", "支出",
        "money", "financial", "investment", "income", "business",
    ],
    "relationship": [
        "人間関係", "友人", "家族", "親", "兄弟", "姉妹", "友達", "知人",
        "人付き合い", "対人", "信頼", "葛藤", "和解", "別れ",
        "relationship", "friend", "family", "parent",
    ],
    "health": [
        "健康", "病気", "体調", "治療", "症状", "医師", "診断", "回復",
        "ストレス", "睡眠", "運動", "食事", "メンタル", "心身",
        "health", "medical", "illness", "treatment", "wellness",
    ],
    "future": [
        "未来", "前兆", "予測", "予感", "チャンス", "運命", "天命",
        "タイミング", "可能性", "展開", "将来", "次", "後々",
        "future", "destiny", "fortune", "prediction", "outcome",
    ],
}

# タロットが推奨される悩みの特徴
TAROT_OPTIMIZED_KEYWORDS: list[str] = [
    "今", "近未来", "3ヶ月", "半年", "今後", "進め方", "決断",
    "どうすべき", "どうなる", "今後の方向", "状況", "対応",
    "展開", "流れ", "進むべき", "今の状況", "この先",
    "soon", "near future", "how should", "what should",
]

# 東洋占術が推奨される悩みの特徴
FENG_SHUI_OPTIMIZED_KEYWORDS: list[str] = [
    "根本", "本質", "適職", "天職", "才能", "資質", "引っ越し", "方位",
    "環境", "運気", "気の流れ", "エネルギー", "バイオリズム", "周期",
    "宿命", "宿星", "本来の", "真の", "長期", "長年", "根強い",
    "essence", "talent", "relocation", "long-term", "fundamental",
]

# 複合占法が推奨される悩みの特徴
COMBINED_OPTIMIZED_KEYWORDS: list[str] = [
    "複雑", "複数", "総合", "全体的", "人生", "人生設計", "多角的",
    "包括的", "統合", "全方位", "シナリオ", "選択肢", "比較",
]

# ---------------------------------------------------------------------------
# データクラス
# ---------------------------------------------------------------------------


@dataclass
class DivineRecommendation:
    """占術推奨結果"""
    divination_type: DivationType
    confidence: float  # 0.0 ~ 1.0
    concern_category: ConcernType
    reasoning: str
    user_guidance: str
    keywords_matched: list[str]

    def to_dict(self) -> dict:
        """JSON シリアライズ用"""
        return {
            "divination_type": self.divination_type,
            "confidence": self.confidence,
            "concern_category": self.concern_category,
            "reasoning": self.reasoning,
            "user_guidance": self.user_guidance,
            "keywords_matched": self.keywords_matched,
        }


@dataclass
class DivineEntry:
    """占いセッション開始データ"""
    query_text: str
    query_text_ja: str
    concern_type: ConcernType
    recommendation: DivineRecommendation
    session_id: str
    created_at: str

    def to_dict(self) -> dict:
        """JSON シリアライズ用"""
        return {
            "query_text": self.query_text,
            "query_text_ja": self.query_text_ja,
            "concern_type": self.concern_type,
            "recommendation": self.recommendation.to_dict(),
            "session_id": self.session_id,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# 占術推奨エンジン
# ---------------------------------------------------------------------------


class DivineEntryEngine:
    """
    ユーザーの相談内容をヒアリングして、最適な占術を推奨するエンジン。
    """

    def __init__(self):
        """初期化"""
        pass

    def _extract_concern_type(self, query: str) -> tuple[ConcernType, float]:
        """
        相談内容からカテゴリを推定（スコア付き）。
        複数該当する場合は最も確度が高いものを返す。

        Returns:
            (concern_type, confidence) - タイプと確度（0.0～1.0）
        """
        query_lower = query.lower()
        concern_scores: dict[ConcernType, float] = {t: 0.0 for t in [
            "love", "work", "money", "relationship", "health", "future", "general"
        ]}

        for concern_type, keywords in CONCERN_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    concern_scores[concern_type] += 1.0

        # 正規化
        max_score = max(concern_scores.values())
        if max_score > 0:
            concern_scores = {k: v / max_score for k, v in concern_scores.items()}

        # スコアが最も高いカテゴリを選択
        best_concern = max(concern_scores, key=concern_scores.get)
        confidence = concern_scores[best_concern]

        return best_concern, confidence

    def _recommend_divination_type(self, query: str, concern: ConcernType) -> DivineRecommendation:
        """
        相談内容から最適な占術を推奨する。
        """
        query_lower = query.lower()

        # 各占術の符号度をスコアリング
        tarot_score = 0.0
        feng_shui_score = 0.0
        combined_score = 0.0

        # タロットが推奨される特徴をスコアリング
        for keyword in TAROT_OPTIMIZED_KEYWORDS:
            if keyword.lower() in query_lower:
                tarot_score += 1.5

        # 東洋占術が推奨される特徴をスコアリング
        for keyword in FENG_SHUI_OPTIMIZED_KEYWORDS:
            if keyword.lower() in query_lower:
                feng_shui_score += 1.5

        # 複合占法が推奨される特徴をスコアリング
        for keyword in COMBINED_OPTIMIZED_KEYWORDS:
            if keyword.lower() in query_lower:
                combined_score += 1.5

        # 相談カテゴリによるボーナス
        if concern in ["love", "future"]:
            tarot_score += 2.0
        elif concern in ["work", "money"]:
            tarot_score += 1.5
            feng_shui_score += 1.0

        if concern in ["work", "money", "health"]:
            feng_shui_score += 2.0

        if concern == "general":
            combined_score += 1.0

        # 正規化
        total_score = tarot_score + feng_shui_score + combined_score
        if total_score == 0:
            tarot_score = 1.0
            total_score = 1.0

        tarot_confidence = tarot_score / total_score
        feng_shui_confidence = feng_shui_score / total_score
        combined_confidence = combined_score / total_score

        # 推奨タイプ決定
        scores = {
            "tarot_celtic_cross": tarot_confidence,
            "feng_shui": feng_shui_confidence,
            "combined": combined_confidence,
        }
        recommended_type: DivationType = max(scores, key=scores.get)  # type: ignore

        # 推奨文を生成
        guidance_map: dict[DivationType, str] = {
            "tarot_celtic_cross": (
                "あなたのそのお悩みには、状況の深層心理と未来の展開を10本の柱で解き明かす"
                "【タロット・ケルト十字スプレッド】が最も適しています。\n"
                "今この瞬間の心理状態から、3～6ヶ月先の展開まで、詳細に読み解きます。\n"
                "それでは、シャッフルへ進みましょう……"
            ),
            "feng_shui": (
                "あなたのそのお悩みには、あなたの根本的な資質と運気の周期を読み解く"
                "【東洋占術・風水＆四柱推命複合診断】が最も適しています。\n"
                "長期的なバイオリズムと環境エネルギーから、人生の本質的な流れを明かします。\n"
                "それでは、あなたの生年月日と現在地をお聞かせください……"
            ),
            "combined": (
                "あなたのそのお悩みには、短期の心理的展開と長期の宿命的バイオリズムを"
                "【複合占法】で総合的に読み解くことが最も適しています。\n"
                "タロットと東洋占術の両面からアプローチし、360度からの視点を提供します。\n"
                "それでは、シャッフルと四柱推命の準備を進めていきましょう……"
            ),
        }

        reasoning_map: dict[DivationType, str] = {
            "tarot_celtic_cross": (
                f"相談内容に「{', '.join(TAROT_OPTIMIZED_KEYWORDS[:3])}」などの"
                "近期的・具体的なキーワードが含まれており、"
                "タロットの即座の心理読解が最適です。"
            ),
            "feng_shui": (
                f"相談内容に「{', '.join(FENG_SHUI_OPTIMIZED_KEYWORDS[:3])}」などの"
                "根本的・長期的なキーワードが含まれており、"
                "東洋占術の本質的・運命的読解が最適です。"
            ),
            "combined": (
                "複数の異なる側面からの総合的な判断が必要な相談内容です。"
                "短期と長期、心理と運命の両面から包括的に診断します。"
            ),
        }

        return DivineRecommendation(
            divination_type=recommended_type,
            confidence=scores[recommended_type],
            concern_category=concern,
            reasoning=reasoning_map[recommended_type],
            user_guidance=guidance_map[recommended_type],
            keywords_matched=[
                kw for kw in TAROT_OPTIMIZED_KEYWORDS + FENG_SHUI_OPTIMIZED_KEYWORDS + COMBINED_OPTIMIZED_KEYWORDS
                if kw.lower() in query_lower
            ][:5],
        )

    def create_entry(self, query_text: str, query_text_ja: str = "") -> DivineEntry:
        """
        新規占いセッションを開始し、推奨占術を返す。

        Parameters
        ----------
        query_text : str
            ユーザーの相談内容（日本語 or 英語）
        query_text_ja : str
            相談内容の日本語（query_text が英語の場合に指定）

        Returns
        -------
        DivineEntry
            占いセッション開始データ
        """
        # 相談カテゴリを推定
        concern_type, _ = self._extract_concern_type(query_text)

        # 最適な占術を推奨
        recommendation = self._recommend_divination_type(query_text, concern_type)

        # セッションID生成（タイムスタンプ ベース）
        now = datetime.now()
        session_id = f"divine_{int(now.timestamp() * 1000)}"

        entry = DivineEntry(
            query_text=query_text,
            query_text_ja=query_text_ja,
            concern_type=concern_type,
            recommendation=recommendation,
            session_id=session_id,
            created_at=now.isoformat(),
        )

        return entry

    def suggest_follow_up_questions(self, entry: DivineEntry) -> list[str]:
        """
        推奨占術に基づいて、ユーザーへのフォローアップ質問を生成。
        """
        questions_by_type: dict[DivationType, list[str]] = {
            "tarot_celtic_cross": [
                "この相談についてもう少し詳しく教えていただけますか？"
                "（例：期限、関係者、現在のアクション）",
                "この相談に対して、あなたが一番知りたいことは何ですか？",
                "シャッフルを始める前に、この相談事を心に思い浮かべながら"
                "ストップボタンを押してください。あなたの直感がカードを選びます。",
            ],
            "feng_shui": [
                "あなたの生年月日をお聞かせください。",
                "現在お住まいの地域（できれば方位も）をお教えください。",
                "この問題でどのくらいの期間お悩みですか？",
            ],
            "combined": [
                "生年月日をお聞かせください。",
                "この相談の期間軸は短期か長期か、あるいは両方ですか？",
                "シャッフルと四柱推命の両データを揃えて、総合診断を開始します。",
            ],
        }

        return questions_by_type.get(entry.recommendation.divination_type, [])
