import unittest

from fortune_core.hexagrams import get_hexagram, get_trigram


class TestHexagrams(unittest.TestCase):
    def test_get_hexagram_64_returns_misei(self) -> None:
        hexagram = get_hexagram(64)
        self.assertEqual(hexagram["name_jp"], "未済")

    def test_get_trigram_alias_still_works(self) -> None:
        trigram = get_trigram(1)
        self.assertEqual(trigram["name_jp"], "乾")


if __name__ == "__main__":
    unittest.main()