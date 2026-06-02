import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    model_path: str
    default_confidence: float
    default_sample_fps: int
    max_frame_width: int
    max_frame_height: int
    mock_detection: bool
    host: str
    port: int
    openai_api_key: str
    openai_base_url: str | None
    image_model: str


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name, "1" if default else "0").strip().lower()
    return val in ("1", "true", "yes", "on")


def get_settings() -> Settings:
    return Settings(
        model_path=os.getenv("MODEL_PATH", "LibreYOLO9t.pt"),
        default_confidence=float(os.getenv("DEFAULT_CONFIDENCE", "0.45")),
        default_sample_fps=int(os.getenv("DEFAULT_SAMPLE_FPS", "5")),
        max_frame_width=int(os.getenv("MAX_FRAME_WIDTH", "640")),
        max_frame_height=int(os.getenv("MAX_FRAME_HEIGHT", "480")),
        mock_detection=_env_bool("MOCK_DETECTION", False),
        host=os.getenv("BACKEND_HOST", "127.0.0.1"),
        port=int(os.getenv("BACKEND_PORT", "8000")),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv("OPENAI_BASE_URL") or None,
        image_model=os.getenv("IMAGE_MODEL", "dall-e-3"),
    )
