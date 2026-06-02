from .models import Detection


class ObjectDetector:
    def __init__(self, confidence_threshold: float, model_path: str):
        self.confidence_threshold = confidence_threshold
        self.model_path = model_path
        self._model = None
        self._names: dict[int, str] = {}
        self._load_model()

    def _load_model(self) -> None:
        try:
            from libreyolo import LibreYOLO  # type: ignore
            self._model = LibreYOLO(self.model_path)
        except ImportError as e:
            raise ImportError(
                "libreyolo is not installed. Run: pip install libreyolo"
            ) from e
        except Exception as e:
            raise RuntimeError(
                "Failed to load LibreYOLO model. Please provide a valid model path using --model."
            ) from e

    def detect(self, frame) -> list[Detection]:
        if self._model is None:
            return []

        try:
            results = self._model(frame, conf=self.confidence_threshold)
        except Exception as e:
            print(f"[WARNING] Detection inference error: {e}")
            return []

        detections: list[Detection] = []

        for result in results:
            boxes = getattr(result, "boxes", None)
            names = getattr(result, "names", {})

            if boxes is None:
                continue

            for box in boxes:
                try:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].tolist()
                    class_name = names.get(cls_id, str(cls_id))

                    detections.append(
                        Detection(
                            class_name=class_name,
                            confidence=conf,
                            bbox=[float(v) for v in xyxy],
                        )
                    )
                except Exception as e:
                    print(f"[WARNING] Skipping malformed detection box: {e}")
                    continue

        return detections
