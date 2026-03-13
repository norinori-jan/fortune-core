from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files


@lru_cache(maxsize=1)
def _load_hexagrams() -> list[dict]:
    data_path = files("fortune_core").joinpath("data/hexagrams.json")
    with data_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_hexagram(hexagram_id: int) -> dict:
    hexagrams = _load_hexagrams()
    for hexagram in hexagrams:
        if hexagram.get("id") == hexagram_id:
            return hexagram
    raise ValueError(f"Unknown hexagram id: {hexagram_id}")


def get_trigram(trigram_id: int) -> dict:
    # Deprecated: Use get_hexagram instead.
    return get_hexagram(trigram_id)
