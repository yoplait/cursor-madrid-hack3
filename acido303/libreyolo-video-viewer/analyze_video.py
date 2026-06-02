#!/usr/bin/env python3
import argparse
import os
import sys

import cv2

from src.config import Config
from src.detector import ObjectDetector
from src.event_builder import build_events, filter_detections, summarize_events
from src.models import DetectionEvent
from src.renderer import FrameRenderer
from src.report_writer import write_report
from src.snapshot_writer import SnapshotWriter
from src.time_utils import format_seconds
from src.video_reader import VideoMetadata, open_video
from src.viewer import VideoViewer


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        description="Analyse une vidéo MP4 locale avec la détection d'objets LibreYOLO."
    )
    parser.add_argument("--video", required=True, help="Chemin vers le fichier MP4 local.")
    parser.add_argument(
        "--model",
        default="./models/LibreYOLOXs.pt",
        help="Chemin vers le modèle LibreYOLO (par défaut : ./models/LibreYOLOXs.pt).",
    )
    parser.add_argument("--output-dir", default="./output", help="Répertoire de sortie.")
    parser.add_argument("--classes", nargs="*", default=[], help="Filtrer par noms de classes.")
    parser.add_argument(
        "--confidence", type=float, default=0.45, help="Seuil de confiance."
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=5,
        help="Fréquence de détection en images par seconde.",
    )
    parser.add_argument(
        "--viewer", action="store_true", help="Afficher la fenêtre de visionneuse OpenCV."
    )
    parser.add_argument(
        "--save-annotated-video", action="store_true", help="Enregistrer le MP4 annoté."
    )
    parser.add_argument(
        "--save-snapshots",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enregistrer des instantanés pour chaque détection.",
    )
    parser.add_argument(
        "--annotate-snapshots",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Dessiner les boîtes englobantes sur les instantanés.",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=None,
        help="Arrêter après N événements (pour les tests).",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Arrêter après N images traitées (pour les tests).",
    )

    args = parser.parse_args()

    if not (0.0 < args.confidence <= 1.0):
        parser.error("--confidence doit être compris entre 0 et 1.")
    if args.sample_rate < 1:
        parser.error("--sample-rate doit être >= 1.")

    return Config(
        video_path=args.video,
        model_path=args.model,
        output_dir=args.output_dir,
        classes=args.classes or [],
        confidence=args.confidence,
        sample_rate=args.sample_rate,
        viewer=args.viewer,
        save_annotated_video=args.save_annotated_video,
        save_snapshots=args.save_snapshots,
        annotate_snapshots=args.annotate_snapshots,
        max_events=args.max_events,
        max_frames=args.max_frames,
    )


def make_output_dirs(output_dir: str) -> tuple[str, str, str]:
    snapshots_dir = os.path.join(output_dir, "snapshots")
    annotated_dir = os.path.join(output_dir, "annotated")
    try:
        os.makedirs(snapshots_dir, exist_ok=True)
        os.makedirs(annotated_dir, exist_ok=True)
    except OSError as e:
        print(f"[ERREUR] Impossible de créer les répertoires de sortie : {e}", file=sys.stderr)
        sys.exit(1)
    return output_dir, snapshots_dir, annotated_dir


def print_header(cfg: Config, meta: VideoMetadata) -> None:
    print(f"Analyse de la vidéo : {cfg.video_path}")
    print(f"IPS : {meta.fps:.1f}")
    print(f"Résolution : {meta.width}x{meta.height}")
    print(f"Durée : {format_seconds(meta.duration_seconds)}")
    print(f"Fréquence d'échantillonnage : {cfg.sample_rate} images/s")
    print(f"Seuil de confiance : {cfg.confidence}")
    print(f"Classes : {', '.join(cfg.classes) if cfg.classes else 'toutes'}")
    print(f"Visionneuse : {'activée' if cfg.viewer else 'désactivée'}")
    print(f"Export vidéo annotée : {'activé' if cfg.save_annotated_video else 'désactivé'}")
    print()


def build_video_writer(
    meta: VideoMetadata, annotated_dir: str, stem: str
) -> cv2.VideoWriter | None:
    out_path = os.path.join(annotated_dir, f"annotated_{stem}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, meta.fps, (meta.width, meta.height))
    if not writer.isOpened():
        print(
            "[AVERTISSEMENT] Codec mp4v indisponible ; essai avec avc1.",
            file=sys.stderr,
        )
        writer.release()
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        writer = cv2.VideoWriter(out_path, fourcc, meta.fps, (meta.width, meta.height))
        if not writer.isOpened():
            print(
                "[ERREUR] Aucun codec vidéo adapté. La vidéo annotée ne sera pas enregistrée.",
                file=sys.stderr,
            )
            return None
    return writer


def main() -> None:
    cfg = parse_args()

    try:
        cap, meta = open_video(cfg.video_path)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"[ERREUR] {e}", file=sys.stderr)
        sys.exit(1)

    output_dir, snapshots_dir, annotated_dir = make_output_dirs(cfg.output_dir)
    print_header(cfg, meta)

    try:
        detector = ObjectDetector(confidence_threshold=cfg.confidence, model_path=cfg.model_path)
    except (ImportError, RuntimeError) as e:
        print(f"[ERREUR] {e}", file=sys.stderr)
        cap.release()
        sys.exit(1)

    renderer = FrameRenderer()
    snapshot_writer = SnapshotWriter(snapshots_dir, annotate=cfg.annotate_snapshots)

    video_stem = os.path.splitext(os.path.basename(cfg.video_path))[0]
    annotated_video_path = os.path.join(annotated_dir, f"annotated_{video_stem}.mp4")
    json_report_path = os.path.join(output_dir, "detections.json")

    video_writer: cv2.VideoWriter | None = None
    if cfg.save_annotated_video:
        video_writer = build_video_writer(meta, annotated_dir, video_stem)

    viewer: VideoViewer | None = None
    if cfg.viewer:
        viewer = VideoViewer(fps=meta.fps)

    frame_interval = max(1, int(round(meta.fps / cfg.sample_rate)))
    all_events: list[DetectionEvent] = []
    current_detections: list = []
    frame_idx = 0

    def on_manual_snapshot(frame_data) -> None:
        path = snapshot_writer.save_manual(frame_data)
        print(f"  [instantané] enregistré manuellement : {path}")

    if viewer is not None:
        viewer.snapshot_callback = on_manual_snapshot

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            is_inference_frame = frame_idx % frame_interval == 0
            seconds = frame_idx / meta.fps

            if is_inference_frame:
                raw = detector.detect(frame)
                current_detections = filter_detections(raw, cfg.classes)

                if current_detections:
                    snapshot_paths: dict[str, str] = {}
                    if cfg.save_snapshots:
                        snapshot_paths = snapshot_writer.save(
                            frame, current_detections, seconds
                        )

                    new_events = build_events(
                        current_detections, frame_idx, meta.fps, snapshot_paths
                    )
                    all_events.extend(new_events)

                    for ev in new_events:
                        print(
                            f"[{ev.timestamp}] {ev.class_name} détecté,"
                            f" confiance {ev.confidence:.2f}"
                        )

                    if cfg.max_events is not None and len(all_events) >= cfg.max_events:
                        break

            timestamp_str = format_seconds(seconds)
            annotated = renderer.render(frame, current_detections, timestamp_str)

            if video_writer is not None:
                video_writer.write(annotated)

            if viewer is not None:
                if not viewer.show(annotated):
                    break

            frame_idx += 1

            if cfg.max_frames is not None and frame_idx >= cfg.max_frames:
                break

    finally:
        cap.release()
        if video_writer is not None:
            video_writer.release()
        if viewer is not None:
            viewer.close()
        cv2.destroyAllWindows()

    write_report(
        output_path=json_report_path,
        video_meta={
            "path": cfg.video_path,
            "fps": meta.fps,
            "frame_count": meta.frame_count,
            "width": meta.width,
            "height": meta.height,
            "duration_seconds": meta.duration_seconds,
        },
        analysis_settings={
            "confidence_threshold": cfg.confidence,
            "sample_rate": cfg.sample_rate,
            "classes": cfg.classes,
            "viewer_enabled": cfg.viewer,
            "annotated_video_enabled": cfg.save_annotated_video,
        },
        outputs={
            "json_report": json_report_path,
            "snapshot_dir": snapshots_dir,
            "annotated_video": annotated_video_path if cfg.save_annotated_video else None,
        },
        events=all_events,
    )

    summary = summarize_events(all_events)
    print()
    print("Terminé.")
    print(f"Nombre total d'événements : {len(all_events)}")
    if summary:
        for cls, count in summary.items():
            print(f"  {cls}: {count}")
    print(f"Rapport enregistré dans : {json_report_path}")
    print(f"Instantanés enregistrés dans : {snapshots_dir}")
    if cfg.save_annotated_video and video_writer is not None:
        print(f"Vidéo annotée enregistrée dans : {annotated_video_path}")


if __name__ == "__main__":
    main()
