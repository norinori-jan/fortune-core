# api.py
# ======
# fortune-core FastAPI サーバー
#
# 起動コマンド:
#     uvicorn src.fortune_core.api:app --reload --host 0.0.0.0 --port 8000
#
# エンドポイント:
#     GET  /                      - ステータス確認
#     GET  /api/divine            - 相談内容を入力 → 占術判定 + タロット展開
#     GET  /api/docs              - Swagger UI

import time
from datetime import datetime
from typing import Optional, List, Dict

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 既存のコアコンポーネントをインポート
from fortune_core.divination_entry import DivineEntryEngine
from fortune_core.tarot_engine import TarotEngine
from fortune_core.report_generator import ReportGenerator, ReadingReport

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FastApp 初期化
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="🔮 Fortune Core API",
    description="相談内容の解析からタロット展開までを一元管理する占いバックエンドAPI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS 設定（フロントエンド・モバイルアプリから直接アクセス可能）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# エンジンの初期化（シングルトン）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

entry_engine = DivineEntryEngine()
tarot_engine = TarotEngine()
report_generator = ReportGenerator()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pydantic モデル
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AnalysisResponse(BaseModel):
    """相談内容の分析結果"""
    query: str
    concern_type: str
    recommended_spread: str
    confidence_score: float
    reasoning: str
    guidance: str


class CardPosition(BaseModel):
    """カード位置データ"""
    position_label: str
    position_index: int
    card_name: str
    element: str
    is_reversed: bool
    meaning: str


class DivinationResponse(BaseModel):
    """完全な鑑定結果"""
    success: bool
    reading_id: str
    timestamp: str
    analysis: AnalysisResponse
    positions: List[CardPosition]
    element_distribution: Dict[str, int]
    guidance_summary: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ヘルスチェック
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/")
def read_root():
    """ステータス確認"""
    return {
        "status": "online",
        "message": "Welcome to Fortune Core API. Let's divine your destiny.",
        "api_version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/api/health")
def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engines": {
            "entry": "ready",
            "tarot": "ready",
            "report": "ready"
        }
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# メイン API エンドポイント
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/api/divine", response_model=DivinationResponse)
def divine(
    query: str = Query(
        ...,
        description="ユーザーの相談内容を入力してください",
        min_length=1,
        max_length=500
    ),
    user_seed: Optional[int] = Query(
        None,
        description="シンクロニシティシード（ミリ秒タイムスタンプ）。省略時はサーバー側で生成。"
    ),
    save_report: bool = Query(
        False,
        description="JSON/HTMLレポートを保存するか（True = 保存）"
    )
):
    """
    【メイン占いAPI】
    
    相談内容（自然言語）を受け取り、以下を一撃で実行:
    1. 占いの入り口：相談内容を自動解析
    2. 占術判定：最適な占術を推奨（信度スコア付き）
    3. タロット展開：ケルト十字スプレッド実行
    4. レポート生成：JSON/HTML（オプション保存）
    
    Returns:
        DivinationResponse: 完全な鑑定結果（分析＋占い結果＋要素分析）
    """
    try:
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 1: 相談内容の分析 → 占術推奨
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        entry = entry_engine.create_entry(query)
        recommendation = entry.recommendation

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 2: シンクロニシティシード決定
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if user_seed is None:
            user_seed = int(time.time() * 1000)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 3: タロット展開
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # （現在はタロット・ケルト十字をデフォルト）
        if recommendation and getattr(recommendation, "divination_type", ""):
            div_type = recommendation.divination_type
        else:
            div_type = "tarot"

        if "tarot" in div_type.lower():
            reading_result = tarot_engine.draw_celtic_cross(
                user_seed=user_seed,
                query=query
            )
        else:
            # フォールバック（他の占術はまだ未実装）
            reading_result = tarot_engine.draw_celtic_cross(
                user_seed=user_seed,
                query=query
            )

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 4: ポジション情報をAPI形式に変換（堅牢化）
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        positions_api: List[CardPosition] = []
        element_dist: Dict[str, int] = {}

        raw_positions = reading_result.get("positions", {}) if isinstance(reading_result, dict) else {}

        # 安定した順序で返すため position_index でソート（存在しない場合はキー順）
        try:
            sorted_items = sorted(
                raw_positions.items(),
                key=lambda kv: int(kv[1].get("position_index", 0)) if isinstance(kv[1], dict) else 0
            )
        except Exception:
            sorted_items = list(raw_positions.items())

        for pos_key, pos_data in sorted_items:
            if not isinstance(pos_data, dict):
                pos_data = {}

            card = pos_data.get("card", {}) or {}
            element = card.get("element", "unknown") or "unknown"
            is_reversed = bool(pos_data.get("is_reversed", False))

            # 要素分布カウント
            element_dist[element] = element_dist.get(element, 0) + 1

            # 解釈文を選択
            meaning_key = "meaning_reversed" if is_reversed else "meaning_upright"
            meaning = card.get(meaning_key, "") or ""

            # position_index を明示的に int にする（None 対策）
            try:
                position_index = int(pos_data.get("position_index", 0))
            except (TypeError, ValueError):
                position_index = 0

            positions_api.append(
                CardPosition(
                    position_label=str(pos_data.get("position_label", "")) or "",
                    position_index=position_index,
                    card_name=str(card.get("name", "Unknown")) or "Unknown",
                    element=str(element),
                    is_reversed=is_reversed,
                    meaning=str(meaning)
                )
            )

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 5: レポート生成（オプション保存）
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        reading_id = f"reading_{user_seed}"

        if save_report:
            report = ReadingReport(
                reading_id=reading_id,
                query_text=query,
                timestamp=datetime.now().isoformat(),
                divination_type=div_type,
                positions=raw_positions,
                element_distribution=element_dist,
                user_seed=user_seed,
            )
            try:
                report_generator.export_formats(report, formats=("json", "html"))
            except Exception as e:
                # レポート保存に失敗してもAPI応答は継続
                print(f"Warning: Report save failed - {e}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 6: API応答を構築
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        guidance_text = getattr(recommendation, "user_guidance", "") if recommendation else ""
        guidance_summary = (
            f"最適な占術は【{div_type}】です。\n"
            f"{(guidance_text or '')[:200]}..."
        )

        analysis_obj = AnalysisResponse(
            query=query,
            concern_type=getattr(entry, "concern_type", "") if entry else "",
            recommended_spread=div_type,
            confidence_score=float(getattr(recommendation, "confidence", 0.0)) if recommendation else 0.0,
            reasoning=getattr(recommendation, "reasoning", "") if recommendation else "",
            guidance=guidance_text or "",
        )

        return DivinationResponse(
            success=True,
            reading_id=reading_id,
            timestamp=datetime.now().isoformat(),
            analysis=analysis_obj,
            positions=positions_api,
            element_distribution=element_dist,
            guidance_summary=guidance_summary,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Divination failed: {str(e)}")


@app.get("/api/analysis")
def analyze_only(
    query: str = Query(
        ...,
        description="相談内容を入力",
        min_length=1,
        max_length=500
    )
):
    """
    相談内容の分析のみ実行（タロット展開なし）

    ユースケース：
    - UI で推奨占術を先に表示して、ユーザーに確認してからタロット展開
    - レイテンシ改善（分析だけなら高速）
    """
    try:
        entry = entry_engine.create_entry(query)
        recommendation = entry.recommendation

        return {
            "success": True,
            "query": query,
            "concern_type": getattr(entry, "concern_type", "") if entry else "",
            "recommended_spread": getattr(recommendation, "divination_type", "") if recommendation else "",
            "confidence_score": float(getattr(recommendation, "confidence", 0.0)) if recommendation else 0.0,
            "reasoning": getattr(recommendation, "reasoning", "") if recommendation else "",
            "guidance": getattr(recommendation, "user_guidance", "") if recommendation else "",
            "follow_up_questions": entry_engine.suggest_follow_up_questions(entry)[:3] if entry else [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# メタ情報
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/api/info")
def api_info():
    """API 情報とエンドポイント一覧"""
    return {
        "api_name": "Fortune Core API",
        "version": "1.0.0",
        "description": "AI-powered divination backend with tarot, feng shui, and more",
        "endpoints": {
            "health": {
                "method": "GET",
                "path": "/api/health",
                "description": "ヘルスチェック"
            },
            "main_divine": {
                "method": "GET",
                "path": "/api/divine",
                "params": ["query", "user_seed (optional)", "save_report (optional)"],
                "description": "相談内容 → 占術判定 + タロット展開（メインAPI）"
            },
            "analyze_only": {
                "method": "GET",
                "path": "/api/analysis",
                "params": ["query"],
                "description": "相談内容の分析のみ（軽量）"
            },
            "docs": {
                "method": "GET",
                "path": "/api/docs",
                "description": "Swagger UI（インタラクティブドキュメント）"
            }
        },
        "examples": {
            "divine": "/api/divine?query=今のプロジェクトをどう進めるべきか？&save_report=true",
            "analysis": "/api/analysis?query=彼との関係は今後どうなりますか？"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
