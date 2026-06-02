import base64
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from openai import AsyncOpenAI

_DALLE_MODELS = {"dall-e-2", "dall-e-3"}

STATIC_CARDS_DIR = Path(__file__).resolve().parents[1] / "static" / "cards"
_REGISTRY_PATH = STATIC_CARDS_DIR / "registry.json"


def _class_slug(class_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", class_name.lower()) or "object"


async def generate_card_image(
    api_key: str,
    class_name: str,
    card_name: str,
    base_url: str | None = None,
    image_model: str = "dall-e-3",
) -> str | None:
    if not api_key:
        return None

    STATIC_CARDS_DIR.mkdir(parents=True, exist_ok=True)

    slug = _class_slug(class_name)
    file_path = STATIC_CARDS_DIR / f"{slug}.png"

    if file_path.exists():
        return f"/static/cards/{slug}.png"

    client_kwargs: dict = {"api_key": api_key, "timeout": 360.0}
    if base_url:
        client_kwargs["base_url"] = base_url

    client = AsyncOpenAI(**client_kwargs)
    prompt = (
        f"Digital trading card illustration of an original cute fantasy creature named {card_name}, "
        f"inspired by the appearance of a {class_name}. Vibrant anime art style, bold outlines, "
        "single creature centered on a plain gradient background, no text, no card borders, "
        "bright colors, friendly expression."
    )
    is_dalle = image_model in _DALLE_MODELS
    gen_kwargs: dict = {
        "model": image_model,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }
    if is_dalle:
        gen_kwargs["quality"] = "standard"
    else:
        gen_kwargs["quality"] = "auto"

    try:
        response = await client.images.generate(**gen_kwargs)
    except Exception as exc:
        print(f"Image generation failed ({type(exc).__name__}): {exc}")
        return None

    item = response.data[0]
    if getattr(item, "b64_json", None):
        file_path.write_bytes(base64.b64decode(item.b64_json))
    elif item.url:
        async with httpx.AsyncClient() as http:
            r = await http.get(item.url, timeout=30)
            r.raise_for_status()
        file_path.write_bytes(r.content)
    else:
        return None

    return f"/static/cards/{slug}.png"


@dataclass
class Card:
    card_id: str
    name: str
    class_name: str
    detection_id: str | None = None
    image_url: str | None = None


@dataclass
class CardRegistry:
    _by_id: dict[str, Card] = field(default_factory=dict)
    _class_to_card: dict[str, str] = field(default_factory=dict)
    _counter: int = 0

    def _save(self) -> None:
        STATIC_CARDS_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "counter": self._counter,
            "cards": {
                cid: {
                    "card_id": c.card_id,
                    "name": c.name,
                    "class_name": c.class_name,
                    "detection_id": c.detection_id,
                    "image_url": c.image_url,
                }
                for cid, c in self._by_id.items()
            },
            "class_to_card": self._class_to_card,
        }
        _REGISTRY_PATH.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls) -> "CardRegistry":
        registry = cls()
        if not _REGISTRY_PATH.exists():
            return registry
        try:
            data = json.loads(_REGISTRY_PATH.read_text())
            registry._counter = data.get("counter", 0)
            for cid, cd in data.get("cards", {}).items():
                registry._by_id[cid] = Card(**cd)
            registry._class_to_card = data.get("class_to_card", {})
        except Exception:
            pass
        return registry

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
        self._save()
        return card, False

    def get(self, card_id: str) -> Card | None:
        return self._by_id.get(card_id)
