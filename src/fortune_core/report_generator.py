"""
report_generator.py
===================

鑑定結果をPDF/画像/JSON形式で生成・保存するモジュール。
ユーザーが「自分の資産」として持ち帰り、検証・参照できるレポートを作成。

主要機能:
- タロット鑑定結果をJSON形式で保存
- 画像形式（PNG/JPEG）でビジュアルレポート生成
- PDF形式でプロ品質レポート生成
- ローカルファイル保存インターフェース
"""

import json
import io
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal
from urllib.parse import urlencode
import base64


# ---------------------------------------------------------------------------
# データクラス
# ---------------------------------------------------------------------------


@dataclass
class ReadingReport:
    """鑑定レポート"""
    reading_id: str
    query_text: str
    timestamp: str
    divination_type: str
    positions: dict
    element_distribution: dict
    user_seed: Optional[int]
    custom_meanings: dict = None

    def __post_init__(self):
        if self.custom_meanings is None:
            self.custom_meanings = {}

    def to_dict(self) -> dict:
        """JSON シリアライズ"""
        return {
            "reading_id": self.reading_id,
            "query_text": self.query_text,
            "timestamp": self.timestamp,
            "divination_type": self.divination_type,
            "positions": self.positions,
            "element_distribution": self.element_distribution,
            "user_seed": self.user_seed,
            "custom_meanings": self.custom_meanings,
        }


# ---------------------------------------------------------------------------
# レポート生成エンジン
# ---------------------------------------------------------------------------


class ReportGenerator:
    """
    鑑定結果をマルチフォーマット（JSON/HTML/PDF/Image）で生成・保存する。
    """

    def __init__(self):
        """初期化"""
        pass

    def generate_json_report(self, report: ReadingReport) -> str:
        """
        JSON 形式のレポートを生成（テキスト）。

        Returns
        -------
        str
            JSON 文字列
        """
        return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

    def save_json_report(
        self,
        report: ReadingReport,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        JSON レポートをファイルに保存。

        Parameters
        ----------
        report : ReadingReport
            鑑定レポート
        output_path : Path | None
            保存先パス。None の場合はホームディレクトリ/fortune_readings に保存。

        Returns
        -------
        Path
            実際の保存先パス
        """
        if output_path is None:
            output_dir = Path.home() / "fortune_readings" / "json"
            output_path = output_dir / f"{report.reading_id}.json"
        else:
            output_path = Path(output_path)
        
        # 親ディレクトリを作成
        output_path.parent.mkdir(parents=True, exist_ok=True)

        json_text = self.generate_json_report(report)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_text)

        return output_path

    def generate_html_report(self, report: ReadingReport) -> str:
        """
        HTML 形式のビジュアルレポートを生成。
        ブラウザで開いたり、スクリーンショットで画像化できる。

        Returns
        -------
        str
            HTML 文字列（フルドキュメント）
        """
        positions_html = self._generate_positions_html(report.positions)
        element_dist_html = self._generate_element_distribution_html(
            report.element_distribution
        )

        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>タロット鑑定レポート - {report.reading_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Georgia', 'Noto Sans JP', serif;
            background: linear-gradient(135deg, #1a0033 0%, #2d0052 100%);
            color: #d0d0d0;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(20, 10, 40, 0.95);
            border: 2px solid #9333ea;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 0 30px rgba(147, 51, 234, 0.3);
        }}
        
        header {{
            text-align: center;
            border-bottom: 2px solid #9333ea;
            padding-bottom: 30px;
            margin-bottom: 40px;
        }}
        
        h1 {{
            font-size: 32px;
            color: #d8b4fe;
            margin-bottom: 10px;
            font-weight: normal;
        }}
        
        .reading-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(147, 51, 234, 0.1);
            border-radius: 8px;
            border-left: 4px solid #9333ea;
        }}
        
        .meta-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .meta-label {{
            font-size: 12px;
            color: #a78bfa;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }}
        
        .meta-value {{
            font-size: 14px;
            color: #d8b4fe;
            font-weight: bold;
        }}
        
        .query-box {{
            background: rgba(147, 51, 234, 0.15);
            border-left: 4px solid #a855f7;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 4px;
        }}
        
        .query-label {{
            font-size: 12px;
            color: #a78bfa;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        
        .query-text {{
            font-size: 16px;
            color: #e9d5ff;
            font-style: italic;
        }}
        
        section {{
            margin-bottom: 40px;
        }}
        
        section h2 {{
            font-size: 20px;
            color: #d8b4fe;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #5d28a8;
            font-weight: normal;
        }}
        
        .positions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }}
        
        .card-position {{
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid #6366f1;
            border-radius: 8px;
            padding: 15px;
            position: relative;
        }}
        
        .card-position.upright {{
            border-left: 4px solid #06b6d4;
        }}
        
        .card-position.reversed {{
            border-left: 4px solid #f87171;
            opacity: 0.85;
        }}
        
        .position-index {{
            font-size: 11px;
            color: #a78bfa;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        
        .position-name {{
            font-size: 14px;
            font-weight: bold;
            color: #d8b4fe;
            margin-bottom: 8px;
        }}
        
        .card-name {{
            font-size: 16px;
            color: #e9d5ff;
            margin-bottom: 6px;
            font-style: italic;
        }}
        
        .card-element {{
            display: inline-block;
            font-size: 11px;
            padding: 4px 8px;
            background: rgba(147, 51, 234, 0.3);
            border-radius: 4px;
            color: #a78bfa;
            margin-right: 6px;
            margin-bottom: 10px;
        }}
        
        .card-orientation {{
            font-size: 12px;
            color: #06b6d4;
            margin-bottom: 8px;
        }}
        
        .card-orientation.reversed {{
            color: #f87171;
        }}
        
        .card-meaning {{
            font-size: 12px;
            color: #c7d2fe;
            line-height: 1.5;
            padding-top: 8px;
            border-top: 1px solid #5d28a8;
        }}
        
        .element-distribution {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
        }}
        
        .element-card {{
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid #6366f1;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }}
        
        .element-icon {{
            font-size: 32px;
            margin-bottom: 8px;
        }}
        
        .element-count {{
            font-size: 24px;
            font-weight: bold;
            color: #d8b4fe;
            margin-bottom: 4px;
        }}
        
        .element-name {{
            font-size: 12px;
            color: #a78bfa;
        }}
        
        footer {{
            border-top: 2px solid #9333ea;
            padding-top: 20px;
            margin-top: 40px;
            text-align: center;
            font-size: 11px;
            color: #6b7280;
        }}
        
        .footer-text {{
            margin-bottom: 8px;
        }}
        
        .print-instruction {{
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #a78bfa;
        }}
        
        @media print {{
            body {{
                background: white;
                color: black;
            }}
            
            .container {{
                background: white;
                border: none;
                box-shadow: none;
            }}
            
            .print-instruction {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔮 タロット鑑定レポート</h1>
        </header>
        
        <div class="reading-meta">
            <div class="meta-item">
                <span class="meta-label">Reading ID</span>
                <span class="meta-value">{report.reading_id}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">鑑定日時</span>
                <span class="meta-value">{datetime.fromisoformat(report.timestamp).strftime('%Y年%m月%d日 %H:%M')}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">占術</span>
                <span class="meta-value">{report.divination_type}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">シンクロシード</span>
                <span class="meta-value">{report.user_seed if report.user_seed else 'ランダム'}</span>
            </div>
        </div>
        
        <div class="query-box">
            <div class="query-label">相談内容</div>
            <div class="query-text">「{report.query_text}」</div>
        </div>
        
        <section>
            <h2>📇 ケルト十字スプレッド（10枚）</h2>
            <div class="positions-grid">
                {positions_html}
            </div>
        </section>
        
        <section>
            <h2>⚡ 要素バランス分析</h2>
            <div class="element-distribution">
                {element_dist_html}
            </div>
        </section>
        
        <footer>
            <div class="footer-text">
                このレポートは fortune-core によって自動生成されました。
            </div>
            <div class="footer-text">
                カード解釈は参考情報です。最終的な判断はご自身の直感と経験を優先してください。
            </div>
            <div class="print-instruction">
                💾 このページをブラウザのスクリーンショット機能で画像保存するか、
                Ctrl+P で PDF として保存できます。
            </div>
        </footer>
    </div>
    
    <script>
        // ページロード完了時にメッセージ表示（デモ用）
        window.addEventListener('load', () => {{
            console.log('Report loaded. Use Ctrl+P to save as PDF or take a screenshot.');
        }});
    </script>
</body>
</html>"""

        return html

    def _generate_positions_html(self, positions: dict) -> str:
        """ポジション情報をHTMLで生成"""
        html_parts = []
        for pos_key, pos_data in positions.items():
            card = pos_data.get("card", {})
            is_reversed = pos_data.get("is_reversed", False)
            orientation = "reversed" if is_reversed else "upright"

            element = card.get("element", "unknown")
            element_emoji = {
                "fire": "🔥",
                "water": "💧",
                "air": "🌬",
                "earth": "🌿",
                "spirit": "✨",
            }.get(element, "✦")

            card_html = f"""<div class="card-position {orientation}">
                <div class="position-index">Position {pos_data.get('position_index', '?')}</div>
                <div class="position-name">{pos_data.get('position_label', 'Unknown')}</div>
                <div class="card-name">{card.get('name', 'Unknown Card')}</div>
                <div>
                    <span class="card-element">{element_emoji} {element.upper()}</span>
                </div>
                <div class="card-orientation {'reversed' if is_reversed else ''}">
                    {'🔄 逆位置（Reversed）' if is_reversed else '✓ 正位置（Upright）'}
                </div>
                <div class="card-meaning">
                    {card.get('meaning_upright' if not is_reversed else 'meaning_reversed', 'No meaning available')}
                </div>
            </div>"""
            html_parts.append(card_html)

        return "\n".join(html_parts)

    def _generate_element_distribution_html(self, distribution: dict) -> str:
        """要素分布をHTMLで生成"""
        element_emojis = {
            "fire": "🔥",
            "water": "💧",
            "air": "🌬",
            "earth": "🌿",
            "spirit": "✨",
        }

        html_parts = []
        for element, count in distribution.items():
            emoji = element_emojis.get(element, "✦")
            html_part = f"""<div class="element-card">
                <div class="element-icon">{emoji}</div>
                <div class="element-count">{count}</div>
                <div class="element-name">{element.upper()}</div>
            </div>"""
            html_parts.append(html_part)

        return "\n".join(html_parts)

    def save_html_report(
        self,
        report: ReadingReport,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        HTML レポートをファイルに保存。

        Returns
        -------
        Path
            実際の保存先パス
        """
        if output_path is None:
            output_dir = Path.home() / "fortune_readings" / "html"
            output_path = output_dir / f"{report.reading_id}.html"
        else:
            output_path = Path(output_path)
        
        # 親ディレクトリを作成
        output_path.parent.mkdir(parents=True, exist_ok=True)

        html_text = self.generate_html_report(report)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_text)

        return output_path

    def generate_share_url(
        self,
        report: ReadingReport,
        base_url: str = "https://fortune-core.example.com/reading",
    ) -> str:
        """
        鑑定結果をシェア可能なURLに変換。
        クエリパラメータにレポートデータを詰めて返す。

        Parameters
        ----------
        report : ReadingReport
            鑑定レポート
        base_url : str
            ベースURL（デフォルトはプレースホルダー）

        Returns
        -------
        str
            シェアURL
        """
        report_json = json.dumps(report.to_dict())
        encoded = base64.b64encode(report_json.encode("utf-8")).decode("utf-8")
        params = {"data": encoded}
        return f"{base_url}?{urlencode(params)}"

    def export_formats(
        self,
        report: ReadingReport,
        output_dir: Optional[Path] = None,
        formats: tuple[Literal["json", "html"], ...] = ("json", "html"),
    ) -> dict[str, Path]:
        """
        複数形式で同時エクスポート。

        Parameters
        ----------
        report : ReadingReport
            鑑定レポート
        output_dir : Path | None
            出力ディレクトリ（Noneの場合は自動）
        formats : tuple
            出力形式（'json', 'html'）

        Returns
        -------
        dict[str, Path]
            形式ごとの保存先パス
        """
        if output_dir is None:
            output_dir = Path.home() / "fortune_readings"

        results = {}

        if "json" in formats:
            json_path = self.save_json_report(report, output_dir / "json" / f"{report.reading_id}.json")
            results["json"] = json_path

        if "html" in formats:
            html_path = self.save_html_report(report, output_dir / "html" / f"{report.reading_id}.html")
            results["html"] = html_path

        return results

    def get_save_instructions(self) -> str:
        """
        ユーザーへの保存方法ガイドを返す。
        """
        return """
【鑑定結果の保存方法】

📱 スマートフォン（iPhone/Android）:
  1. HTMLレポートをブラウザで開く
  2. 「共有」ボタンをタップ
  3. 「ファイルに保存」または「写真に保存」を選択
  4. 完了！

💻 PC（Windows/Mac）:
  1. HTMLレポートをブラウザで開く
  2. Ctrl+P（またはCmd+P）で印刷ダイアログを開く
  3. 「PDFに保存」を選択
  4. または Ctrl+S（またはCmd+S）でHTML形式で保存

📊 データバックアップ:
  - JSON形式レポートは完全なデータを保持しており、
    後から別システムにインポートできます。
  - 保存先: {Path.home() / 'fortune_readings'}
"""
