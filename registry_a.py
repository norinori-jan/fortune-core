"""
registry_a.py
=============
【唯一の真実】共通コア定義ジェネレータ

3つのリポジトリ（fortune-core, fengshui-app, fenshui_map）を統合する
Feng Shui Registry の生成エンジン。

iPhone 17 Pro UI、AR ゴーグル、WebGL/Three.js 対応を想定した
拡張可能なデータ構造を生成します。

出力: registry_a.json (UTF-8, Gzip 圧縮対応)
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple


# ========================================================================
# 基本定義テーブル
# ========================================================================

# 二十四山（24mountain）の構成
MOUNTAINS_DEFINITION = [
    ("子", "水", "earthly_branch", "north", "玄武"),
    ("癸", "水", "heavenly_stem", "north", "玄武"),
    ("丑", "土", "earthly_branch", "north_east", "鬼門"),
    ("艮", "土", "bagua", "north_east", "鬼門"),
    ("寅", "木", "earthly_branch", "north_east", "鬼門"),
    ("甲", "木", "heavenly_stem", "east", "青龍"),
    ("卯", "木", "earthly_branch", "east", "青龍"),
    ("乙", "木", "heavenly_stem", "east", "青龍"),
    ("辰", "土", "earthly_branch", "south_east", "風門"),
    ("巽", "木", "bagua", "south_east", "風門"),
    ("巳", "火", "earthly_branch", "south_east", "風門"),
    ("丙", "火", "heavenly_stem", "south", "朱雀"),
    ("午", "火", "earthly_branch", "south", "朱雀"),
    ("丁", "火", "heavenly_stem", "south", "朱雀"),
    ("未", "土", "earthly_branch", "south_west", "裏鬼門"),
    ("坤", "土", "bagua", "south_west", "裏鬼門"),
    ("申", "金", "earthly_branch", "south_west", "裏鬼門"),
    ("庚", "金", "heavenly_stem", "west", "白虎"),
    ("酉", "金", "earthly_branch", "west", "白虎"),
    ("辛", "金", "heavenly_stem", "west", "白虎"),
    ("戌", "土", "earthly_branch", "north_west", "天門"),
    ("乾", "金", "bagua", "north_west", "天門"),
    ("亥", "水", "earthly_branch", "north_west", "天門"),
    ("壬", "水", "heavenly_stem", "north", "玄武"),
]

# 八卦（Bagua）定義 — 伏羲八卦順序
BAGUA_DEFINITION = [
    {
        "id": "坎",
        "seq_fuxi": 6,
        "seq_wenwang": 1,
        "element": "水",
        "number": 1,
        "direction": "north",
        "direction_ja": "北",
        "lines": "010",  # 陰陽爻表現（下から上）
        "symbol": "☵",
        "phenomenon": "水",
        "family_member": "次子",
        "season": "冬",
        "time": "夜中",
        "body_part": "耳",
        "animal": "豚",
        "taste": "塩辛い",
        "color": "黒",
    },
    {
        "id": "坤",
        "seq_fuxi": 7,
        "seq_wenwang": 2,
        "element": "土",
        "number": 2,
        "direction": "south_west",
        "direction_ja": "南西",
        "lines": "000",
        "symbol": "☷",
        "phenomenon": "地",
        "family_member": "母",
        "season": "late_summer",
        "time": "午後",
        "body_part": "腹",
        "animal": "牛",
        "taste": "甘い",
        "color": "黄",
    },
    {
        "id": "震",
        "seq_fuxi": 3,
        "seq_wenwang": 3,
        "element": "木",
        "number": 3,
        "direction": "east",
        "direction_ja": "東",
        "lines": "001",
        "symbol": "☳",
        "phenomenon": "雷",
        "family_member": "長子",
        "season": "春",
        "time": "明け方",
        "body_part": "足",
        "animal": "龍",
        "taste": "酸っぱい",
        "color": "青",
    },
    {
        "id": "巽",
        "seq_fuxi": 2,
        "seq_wenwang": 4,
        "element": "木",
        "number": 4,
        "direction": "south_east",
        "direction_ja": "南東",
        "lines": "011",
        "symbol": "☴",
        "phenomenon": "風",
        "family_member": "長女",
        "season": "late_spring",
        "time": "朝",
        "body_part": "腿",
        "animal": "鶏",
        "taste": "酸っぱい",
        "color": "緑",
    },
    {
        "id": "乾",
        "seq_fuxi": 0,
        "seq_wenwang": 6,
        "element": "金",
        "number": 6,
        "direction": "north_west",
        "direction_ja": "北西",
        "lines": "111",
        "symbol": "☰",
        "phenomenon": "天",
        "family_member": "父",
        "season": "early_winter",
        "time": "夕方",
        "body_part": "頭",
        "animal": "馬",
        "taste": "塩辛い",
        "color": "白",
    },
    {
        "id": "兌",
        "seq_fuxi": 1,
        "seq_wenwang": 7,
        "element": "金",
        "number": 7,
        "direction": "west",
        "direction_ja": "西",
        "lines": "110",
        "symbol": "☱",
        "phenomenon": "沢",
        "family_member": "次女",
        "season": "autumn",
        "time": "夜",
        "body_part": "口",
        "animal": "羊",
        "taste": "辛い",
        "color": "白",
    },
    {
        "id": "艮",
        "seq_fuxi": 4,
        "seq_wenwang": 8,
        "element": "土",
        "number": 8,
        "direction": "north_east",
        "direction_ja": "北東",
        "lines": "100",
        "symbol": "☶",
        "phenomenon": "山",
        "family_member": "次男",
        "season": "late_winter",
        "time": "夜中",
        "body_part": "手",
        "animal": "犬",
        "taste": "甘い",
        "color": "黄",
    },
    {
        "id": "離",
        "seq_fuxi": 5,
        "seq_wenwang": 9,
        "element": "火",
        "number": 9,
        "direction": "south",
        "direction_ja": "南",
        "lines": "101",
        "symbol": "☲",
        "phenomenon": "火",
        "family_member": "次女",
        "season": "summer",
        "time": "昼",
        "body_part": "目",
        "animal": "雉",
        "taste": "苦い",
        "color": "赤",
    },
]

# 天干（Heavenly Stems）
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支（Earthly Branches）
EARTHLY_BRANCHES = [
    "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"
]

# 五行（Five Elements）— 相生・相剋
FIVE_ELEMENTS_DEFINITION = {
    "木": {
        "label_ja": "木",
        "label_en": "wood",
        "color": "青",
        "generates": "火",
        "controlled_by": "金",
        "yin_yang": "陽",
        "organ": "肝",
        "sense": "目",
        "season": "春",
        "direction": "東",
    },
    "火": {
        "label_ja": "火",
        "label_en": "fire",
        "color": "赤",
        "generates": "土",
        "controlled_by": "水",
        "yin_yang": "陰",
        "organ": "心",
        "sense": "舌",
        "season": "夏",
        "direction": "南",
    },
    "土": {
        "label_ja": "土",
        "label_en": "earth",
        "color": "黄",
        "generates": "金",
        "controlled_by": "木",
        "yin_yang": "陽",
        "organ": "脾",
        "sense": "口",
        "season": "晩夏",
        "direction": "中央",
    },
    "金": {
        "label_ja": "金",
        "label_en": "metal",
        "color": "白",
        "generates": "水",
        "controlled_by": "火",
        "yin_yang": "陰",
        "organ": "肺",
        "sense": "鼻",
        "season": "秋",
        "direction": "西",
    },
    "水": {
        "label_ja": "水",
        "label_en": "water",
        "color": "黒",
        "generates": "木",
        "controlled_by": "土",
        "yin_yang": "陽",
        "organ": "腎",
        "sense": "耳",
        "season": "冬",
        "direction": "北",
    },
}

# 方角ロール（四神相応）
DIRECTIONAL_ROLES = {
    "north": {"label_ja": "北", "role": "玄武", "element": "水", "meaning": "後方サポート"},
    "east": {"label_ja": "東", "role": "青龍", "element": "木", "meaning": "左側サポート"},
    "south": {
        "label_ja": "南",
        "role": "朱雀",
        "element": "火",
        "meaning": "前方開放",
    },
    "west": {"label_ja": "西", "role": "白虎", "element": "金", "meaning": "右側サポート"},
}


# ========================================================================
# ジェネレータメイン関数
# ========================================================================


def generate_twenty_four_mountains() -> List[Dict[str, Any]]:
    """二十四山（24-Mountain）を動的に生成"""
    mountains_list = []
    for idx, (name, element, category, direction, role) in enumerate(MOUNTAINS_DEFINITION):
        center_deg = (idx * 15.0) % 360.0
        start_deg = (center_deg - 7.5) % 360.0
        end_deg = (center_deg + 7.5) % 360.0

        mountains_list.append(
            {
                "index": idx,
                "name": name,
                "center_deg": center_deg,
                "start_deg": start_deg,
                "end_deg": end_deg,
                "element": element,
                "category": category,  # earthly_branch, heavenly_stem, bagua
                "direction": direction,
                "feng_shui_role": role,
            }
        )
    return mountains_list


def generate_five_elements() -> Dict[str, Dict[str, Any]]:
    """五行（Five Elements）を生成"""
    return FIVE_ELEMENTS_DEFINITION


def generate_ganzhi() -> Dict[str, List[str]]:
    """干支（Ganzhi: Heavenly Stems + Earthly Branches）を生成"""
    return {
        "heavenly_stems": HEAVENLY_STEMS,
        "earthly_branches": EARTHLY_BRANCHES,
    }


def generate_bagua() -> List[Dict[str, Any]]:
    """八卦（Bagua）を生成"""
    return BAGUA_DEFINITION


def generate_lopan_layers() -> Dict[str, Dict[str, Any]]:
    """
    羅盤層（L1〜L13）を生成
    
    L1: 天池（中央磁針）
    L2: 先天八卦（伏羲八卦）
    L3: 後天八卦（文王八卦）
    L4: 地盤正針二十四山
    L5: 人盤三十六穴（予備）
    L6: 天盤正針二十四山（予備）
    L7: 分金（金銭分金）
    L8: 更細分
    L9〜L13: 将来の拡張用
    """
    return {
        "L1": {
            "name": "天池",
            "name_en": "compass_rose",
            "type": "center_point",
            "description": "羅盤中央の磁針",
            "precision_deg": 0.0,
            "mobile_ar": {"visible": True, "z_offset": 0.1},
        },
        "L2": {
            "name": "先天八卦",
            "name_en": "fuxi_bagua",
            "type": "bagua",
            "description": "伏羲八卦（先天八卦）8方位",
            "count": 8,
            "degree_per_section": 45.0,
            "ref": "bagua",
            "mobile_ar": {"visible": True, "z_offset": 0.2},
        },
        "L3": {
            "name": "後天八卦",
            "name_en": "wenwang_bagua",
            "type": "bagua",
            "description": "文王八卦（後天八卦）",
            "count": 8,
            "degree_per_section": 45.0,
            "mobile_ar": {"visible": True, "z_offset": 0.25},
        },
        "L4": {
            "name": "地盤正針二十四山",
            "name_en": "ground_24_mountains_compass",
            "type": "24_mountains",
            "description": "地盤の正針二十四山",
            "count": 24,
            "degree_per_section": 15.0,
            "ref": "twenty_four_mountains",
            "precision_deg": 7.5,
            "mobile_ar": {"visible": True, "z_offset": 0.3},
        },
        "L5": {
            "name": "人盤",
            "name_en": "human_plate",
            "type": "human_plate",
            "description": "人盤（将来実装予定）",
            "count": 36,
            "degree_per_section": 10.0,
            "mobile_ar": {"visible": False, "z_offset": 0.35},
        },
        "L6": {
            "name": "天盤正針二十四山",
            "name_en": "heaven_24_mountains_compass",
            "type": "24_mountains",
            "description": "天盤の正針二十四山（将来実装予定）",
            "count": 24,
            "degree_per_section": 15.0,
            "mobile_ar": {"visible": False, "z_offset": 0.4},
        },
        "L7": {
            "name": "分金",
            "name_en": "fine_divisions",
            "type": "fine_divisions",
            "description": "金銭分金（5度精度）",
            "precision_deg": 5.0,
            "mobile_ar": {"visible": False, "z_offset": 0.45},
        },
        "L8": {
            "name": "更細分",
            "name_en": "ultra_fine_divisions",
            "type": "ultra_fine_divisions",
            "description": "3度精度による更細分",
            "precision_deg": 3.0,
            "mobile_ar": {"visible": False, "z_offset": 0.5},
        },
        "L9": {
            "name": "予約L9",
            "name_en": "reserved_L9",
            "type": "reserved",
            "description": "将来の層拡張用",
            "mobile_ar": {"visible": False},
        },
        "L10": {
            "name": "予約L10",
            "name_en": "reserved_L10",
            "type": "reserved",
            "description": "将来の層拡張用",
            "mobile_ar": {"visible": False},
        },
        "L11": {
            "name": "予約L11",
            "name_en": "reserved_L11",
            "type": "reserved",
            "description": "将来の層拡張用",
            "mobile_ar": {"visible": False},
        },
        "L12": {
            "name": "予約L12",
            "name_en": "reserved_L12",
            "type": "reserved",
            "description": "将来の層拡張用",
            "mobile_ar": {"visible": False},
        },
        "L13": {
            "name": "三百六十度",
            "name_en": "360_degrees",
            "type": "full_precision",
            "description": "360度フルスケール（1度精度）",
            "precision_deg": 1.0,
            "mobile_ar": {"visible": False, "z_offset": 0.55},
        },
    }


def generate_registry() -> Dict[str, Any]:
    """
    registry_a.json 本体を生成
    
    Returns:
        統合 Registry データ
    """
    registry_data = {
        "meta": {
            "version": "1.0.0",
            "schema_version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "source": "registry_a.py",
            "description": "Unified feng shui compass registry (Single Source of Truth)",
            "repositories": {
                "fortune_core": "https://github.com/norinori-jan/fortune-core",
                "fengshui_app": "https://github.com/norinori-jan/fengshui-app",
                "fenshui_map": "https://github.com/norinori-jan/fenshui_map",
            },
            "compatibility": {
                "platforms": ["web", "mobile_ios_17", "mobile_android", "ar_goggle"],
                "formats": ["json", "json_gz", "msgpack"],
                "caching": {"ttl_seconds": 86400, "etag_support": True},
            },
        },
        "twenty_four_mountains": generate_twenty_four_mountains(),
        "bagua": generate_bagua(),
        "five_elements": generate_five_elements(),
        "ganzhi": generate_ganzhi(),
        "directional_roles": DIRECTIONAL_ROLES,
        "lopan_layers": generate_lopan_layers(),
        "constants": {
            "degrees_per_day": 360.0,
            "degrees_per_year": 360.0 * 365.25,
            "precision_default": 1.0,
            "precision_mobile": 7.5,
        },
    }
    return registry_data


# ========================================================================
# ファイル出力処理
# ========================================================================


def save_registry_json(output_dir: str = ".") -> str:
    """
    registry_a.json を出力
    
    Args:
        output_dir: 出力ディレクトリ（デフォルト: カレントディレクトリ）
    
    Returns:
        出力ファイルのパス
    """
    registry_data = generate_registry()
    output_path = os.path.join(output_dir, "registry_a.json")

    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, ensure_ascii=False, indent=2)

    return output_path


def validate_registry(registry_data: Dict[str, Any]) -> bool:
    """
    registry データをバリデーション
    
    Args:
        registry_data: Registry データ
    
    Returns:
        バリデーション成功時 True
    """
    checks = [
        ("meta" in registry_data, "meta field missing"),
        (
            len(registry_data.get("twenty_four_mountains", [])) == 24,
            "Expected 24 mountains",
        ),
        (len(registry_data.get("bagua", [])) == 8, "Expected 8 bagua"),
        (
            len(registry_data.get("ganzhi", {}).get("heavenly_stems", [])) == 10,
            "Expected 10 heavenly stems",
        ),
        (
            len(registry_data.get("ganzhi", {}).get("earthly_branches", [])) == 12,
            "Expected 12 earthly branches",
        ),
        (
            len(registry_data.get("five_elements", {})) == 5,
            "Expected 5 elements",
        ),
    ]

    for check, msg in checks:
        if not check:
            print(f"❌ Validation failed: {msg}")
            return False

    print("✅ Registry validation passed")
    return True


# ========================================================================
# メイン実行
# ========================================================================


if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("【fortune-core】registry_a.json Generator")
    print("=" * 70)

    # Registry生成
    registry = generate_registry()

    # バリデーション
    if not validate_registry(registry):
        sys.exit(1)

    # ファイル出力
    output_path = save_registry_json()
    print(f"\n✅ Generated: {output_path}")
    print(f"   Size: {os.path.getsize(output_path)} bytes")
    print(f"\n📌 Ready for deployment to GitHub Pages:")
    print(f"   https://norinori-jan.github.io/fortune-core/registry_a.json")

    # 統計情報
    print(f"\n📊 Registry statistics:")
    print(f"   - 24 Mountains: {len(registry['twenty_four_mountains'])}")
    print(f"   - Bagua: {len(registry['bagua'])}")
    print(f"   - Five Elements: {len(registry['five_elements'])}")
    print(f"   - Heavenly Stems: {len(registry['ganzhi']['heavenly_stems'])}")
    print(f"   - Earthly Branches: {len(registry['ganzhi']['earthly_branches'])}")
    print(f"   - Lopan Layers: {len(registry['lopan_layers'])}")
    print()
