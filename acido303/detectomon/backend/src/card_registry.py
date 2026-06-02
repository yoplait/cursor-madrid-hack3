import hashlib
import re
from dataclasses import dataclass, field


@dataclass
class Card:
    card_id: str
    name: str
    class_name: str
    detection_id: str | None = None


@dataclass
class CardRegistry:
    _by_id: dict[str, Card] = field(default_factory=dict)
    _class_to_card: dict[str, str] = field(default_factory=dict)
    _counter: int = 0

    def _slug(self, class_name: str) -> str:
        base = re.sub(r"[^a-z0-9]+", "", class_name.lower()) or "object"
        return base[:1].upper() + base[1:] + "mon"

    def lookup_by_class(self, class_name: str) -> Card | None:
        card_id = self._class_to_card.get(class_name.lower())
        if not card_id:
            return None
        return self._by_id.get(card_id)

    def lookup_by_detection_hash(self, class_name: str, box: dict) -> Card | None:
        key = self._hash_key(class_name, box)
        card_id = self._class_to_card.get(key)
        if card_id:
            return self._by_id.get(card_id)
        return self.lookup_by_class(class_name)

    def _hash_key(self, class_name: str, box: dict) -> str:
        raw = f"{class_name.lower()}:{box['x1']:.0f}:{box['y1']:.0f}:{box['x2']:.0f}:{box['y2']:.0f}"
        return "hash:" + hashlib.md5(raw.encode()).hexdigest()[:12]

    def register_class_mapping(self, class_name: str, card_id: str) -> None:
        self._class_to_card[class_name.lower()] = card_id

    def generate(
        self,
        detection_id: str,
        class_name: str,
        box: dict,
    ) -> tuple[Card, bool]:
        existing = self.lookup_by_class(class_name)
        if existing:
            return existing, True

        self._counter += 1
        card_id = f"card-{self._counter}"
        name = self._slug(class_name)
        card = Card(
            card_id=card_id,
            name=name,
            class_name=class_name,
            detection_id=detection_id,
        )
        self._by_id[card_id] = card
        self.register_class_mapping(class_name, card_id)
        return card, False

    def get(self, card_id: str) -> Card | None:
        return self._by_id.get(card_id)
