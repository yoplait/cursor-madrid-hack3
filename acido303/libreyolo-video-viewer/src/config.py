from dataclasses import dataclass, field


@dataclass
class Config:
    video_path: str
    model_path: str = "./models/LibreYOLOXs.pt"
    output_dir: str = "./output"
    classes: list[str] = field(default_factory=list)
    confidence: float = 0.45
    sample_rate: int = 5
    viewer: bool = False
    save_annotated_video: bool = False
    save_snapshots: bool = True
    annotate_snapshots: bool = True
    max_events: int | None = None
    max_frames: int | None = None
