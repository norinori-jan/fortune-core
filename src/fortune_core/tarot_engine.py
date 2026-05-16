"""
Tarot Engine for Major Arcana (22 cards) divination.
Supports Celtic Cross spread (10-card layout) with synchronicity support.
Extensible for future integration with Eastern divination systems (Feng Shui, Five Elements).
"""

import json
import random
import time
from enum import Enum
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class Orientation(Enum):
    """Card orientation: upright or reversed."""
    UPRIGHT = "UPRIGHT"
    REVERSED = "REVERSED"


class Element(Enum):
    """Elemental attributes for cross-over compatibility with Eastern divination."""
    AIR = "AIR"
    FIRE = "FIRE"
    WATER = "WATER"
    EARTH = "EARTH"


class CelticCrossPosition(Enum):
    """10-position Celtic Cross spread layout."""
    CURRENT_SITUATION = 1
    CHALLENGE = 2
    DISTANT_PAST = 3
    FOUNDATION = 4
    PAST = 5
    FUTURE = 6
    SELF = 7
    ENVIRONMENT = 8
    HOPES_FEARS = 9
    OUTCOME = 10


@dataclass
class TarotCard:
    """Represents a single Tarot card with full metadata."""
    number: int
    name: str
    element: Element
    meanings: Dict[str, str]

    def get_meaning(self, orientation: Orientation) -> str:
        """Retrieve card meaning based on orientation."""
        key = orientation.value.lower()
        return self.meanings.get(key, "")


@dataclass
class DrawResult:
    """Result of a single card draw with orientation."""
    card: TarotCard
    orientation: Orientation

    def to_dict(self) -> Dict:
        """Convert result to dictionary."""
        return {
            "number": self.card.number,
            "name": self.card.name,
            "element": self.card.element.value,
            "orientation": self.orientation.value,
            "meaning": self.card.get_meaning(self.orientation)
        }


@dataclass
class CelticCrossReading:
    """Complete Celtic Cross spread result (10 cards) with query context."""
    positions: Dict[CelticCrossPosition, DrawResult] = field(default_factory=dict)
    query_text: str = ""
    user_seed: Optional[int] = None
    timestamp: str = ""
    reading_id: str = ""

    def to_dict(self) -> Dict:
        """Convert reading to dictionary."""
        return {
            "reading_id": self.reading_id,
            "timestamp": self.timestamp,
            "query_text": self.query_text,
            "user_seed": self.user_seed,
            "positions": {
                position.name: draw.to_dict()
                for position, draw in self.positions.items()
            }
        }


class TarotEngine:
    """
    Main Tarot divination engine.
    Loads card data from JSON and provides drawing/spreading functionality.
    Supports synchronicity through user-provided seed values.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize Tarot Engine.

        Args:
            data_dir: Directory containing tarot_cards.json.
                     Defaults to the data directory alongside this module.
        """
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"

        self.data_dir = data_dir
        self.cards: List[TarotCard] = []
        self._load_cards()

    def _load_cards(self) -> None:
        """Load all 22 major arcana cards from JSON file."""
        cards_file = self.data_dir / "tarot_cards.json"

        if not cards_file.exists():
            raise FileNotFoundError(f"tarot_cards.json not found at {cards_file}")

        with open(cards_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        loaded_cards = []
        for card_data in data.get("cards", []):
            card = TarotCard(
                number=card_data["number"],
                name=card_data["name"],
                element=Element[card_data["element"]],
                meanings=card_data["meanings"]
            )
            loaded_cards.append(card)

        if len(loaded_cards) != 22:
            raise ValueError(f"Expected 22 cards, got {len(loaded_cards)}")

        loaded_cards.sort(key=lambda c: c.number)
        for i, card in enumerate(loaded_cards):
            if card.number != i:
                raise ValueError(f"Card numbering is not sequential: expected {i}, got {card.number}")

        self.cards = loaded_cards

    def _draw_single_card(self) -> DrawResult:
        """
        Draw a single random card with random orientation.

        Returns:
            DrawResult: A card with its orientation.
        """
        card = random.choice(self.cards)
        orientation = random.choice(list(Orientation))
        return DrawResult(card=card, orientation=orientation)

    def _generate_reading_id(self) -> str:
        """Generate unique reading ID based on timestamp."""
        return f"reading_{int(time.time() * 1000)}"

    def draw_celtic_cross(
        self,
        query_text: str = "",
        user_seed: Optional[int] = None
    ) -> CelticCrossReading:
        """
        Perform a complete Celtic Cross spread (10-card layout) with synchronicity support.

        The user_seed parameter allows the diviner to embed the moment they physically
        stopped the shuffle (e.g., millisecond timestamp) into the random seed,
        creating a mathematical correlation between their intention and the cards drawn.

        Args:
            query_text: The query or concern being addressed in this reading.
                       Stored in the reading result for reference.
            user_seed: Optional seed value representing the moment the diviner stopped shuffling.
                      Typically a millisecond timestamp. If provided, this ensures that
                      the same seed always produces the same card sequence (reproducibility).
                      If None, random.seed() is not explicitly set, allowing true randomness.

        Returns:
            CelticCrossReading: Full reading with all 10 positions mapped to cards,
                               including query context and seed information.

        Positions:
            1. CURRENT_SITUATION - 現状（中央）
            2. CHALLENGE - 障害（十字形の外）
            3. DISTANT_PAST - 顕在意識/遠い過去
            4. FOUNDATION - 潜在意識/基盤
            5. PAST - 過去
            6. FUTURE - 未来
            7. SELF - 本人の立場
            8. ENVIRONMENT - 環境/他者の見方
            9. HOPES_FEARS - 希望/不安
            10. OUTCOME - 最終結果

        Example:
            >>> engine = TarotEngine()
            >>> reading = engine.draw_celtic_cross(
            ...     query_text="私の人生の方向性は？",
            ...     user_seed=1726483924567
            ... )
            >>> print(reading.query_text)
            "私の人生の方向性は？"
            >>> print(reading.positions[CelticCrossPosition.OUTCOME].card.name)
            "The Sun"
        """
        if user_seed is not None:
            random.seed(user_seed)

        positions = {}
        for position in CelticCrossPosition:
            positions[position] = self._draw_single_card()

        reading = CelticCrossReading(
            positions=positions,
            query_text=query_text,
            user_seed=user_seed,
            timestamp=datetime.now().isoformat(),
            reading_id=self._generate_reading_id()
        )

        return reading

    def draw_card(self, count: int = 1) -> List[DrawResult]:
        """
        Draw one or more cards with random orientation.

        Args:
            count: Number of cards to draw. Defaults to 1.

        Returns:
            List[DrawResult]: List of drawn cards with orientations.
        """
        return [self._draw_single_card() for _ in range(count)]

    def get_card_by_number(self, number: int) -> Optional[TarotCard]:
        """
        Retrieve a specific card by its major arcana number (0-21).

        Args:
            number: Card number (0-21).

        Returns:
            TarotCard if found, None otherwise.
        """
        if 0 <= number < len(self.cards):
            return self.cards[number]
        return None

    def get_cards_by_element(self, element: Element) -> List[TarotCard]:
        """
        Retrieve all cards of a specific element.
        Useful for Eastern divination cross-over (Feng Shui, Five Elements).

        Args:
            element: The element to filter by.

        Returns:
            List of cards matching the element.
        """
        return [card for card in self.cards if card.element == element]

    def get_element_distribution(self) -> Dict[str, int]:
        """
        Get distribution of cards across all elements.

        Returns:
            Dict mapping element names to card counts.
        """
        distribution = {elem.value: 0 for elem in Element}
        for card in self.cards:
            distribution[card.element.value] += 1
        return distribution

    def set_card_meaning(
        self,
        card_number: int,
        orientation: str,
        meaning: str
    ) -> bool:
        """
        Update a card's meaning for a specific orientation.
        Supports dynamic meaning injection (e.g., from voice-converted custom interpretations).

        Args:
            card_number: Card number (0-21).
            orientation: "upright" or "reversed".
            meaning: New meaning text.

        Returns:
            True if successful, False otherwise.
        """
        card = self.get_card_by_number(card_number)
        if card is None:
            return False

        orientation_key = orientation.lower()
        if orientation_key not in card.meanings:
            return False

        card.meanings[orientation_key] = meaning
        return True

    def seed(self, value: int) -> None:
        """
        Seed the random number generator for deterministic draws (testing/debugging).

        Args:
            value: Seed value.
        """
        random.seed(value)

    def analyze_reading_elements(self, reading: CelticCrossReading) -> Dict[str, int]:
        """
        Analyze the elemental composition of a completed reading.
        Useful for Eastern divination insights (Feng Shui, Five Elements balance).

        Args:
            reading: A completed CelticCrossReading.

        Returns:
            Dict mapping element names to counts in the reading.
        """
        element_count = {elem.value: 0 for elem in Element}
        for draw_result in reading.positions.values():
            element_count[draw_result.card.element.value] += 1
        return element_count

    def get_reading_summary(self, reading: CelticCrossReading) -> Dict:
        """
        Generate a comprehensive summary of a reading including query, seed, and elements.

        Args:
            reading: A completed CelticCrossReading.

        Returns:
            Dict containing summary data for display or analysis.
        """
        return {
            "reading_id": reading.reading_id,
            "timestamp": reading.timestamp,
            "query_text": reading.query_text,
            "user_seed": reading.user_seed,
            "element_distribution": self.analyze_reading_elements(reading),
            "cards": reading.to_dict()
        }
