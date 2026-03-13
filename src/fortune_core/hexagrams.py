from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files


@lru_cache(maxsize=1)
def _load_trigrams() -> list[dict]:
    data_path = files("fortune_core").joinpath("data/hexagrams.json")
    with data_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_trigram(trigram_id: int) -> dict:
    trigrams = _load_trigrams()
    for trigram in trigrams:
        if trigram.get("id") == trigram_id:
            return trigram
    raise ValueError(f"Unknown trigram id: {trigram_id}")
