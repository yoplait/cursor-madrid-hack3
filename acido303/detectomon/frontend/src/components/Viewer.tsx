import { useCallback, useEffect, useRef } from "react";
import type { Detection } from "../types";
import {
  drawDetections,
  getDisplayScale,
  hitTest,
  type DisplayScale,
} from "../utils/overlay";
import "../styles/viewer.css";

type Props = {
  detections: Detection[];
  selectedId: string | null;
  sourceFrameWidth: number;
  sourceFrameHeight: number;
  running: boolean;
  onSelect: (det: Detection | null) => void;
  onVideoReady: (video: HTMLVideoElement) => void;
  videoRef: React.RefObject<HTMLVideoElement | null>;
  cssZoom?: number;
};

export default function Viewer({
  detections,
  selectedId,
  sourceFrameWidth,
  sourceFrameHeight,
  running,
  onSelect,
  onVideoReady,
  videoRef,
  cssZoom = 1,
}: Props) {
  const overlayRef = useRef<HTMLCanvasElement>(null);
  const captureRef = useRef<HTMLCanvasElement>(null);
  const scaleRef = useRef<DisplayScale | null>(null);

  const syncCanvasSize = useCallback(() => {
    const video = videoRef.current;
    const overlay = overlayRef.current;
    if (!video || !overlay) return;

    const dw = video.clientWidth;
    const dh = video.clientHeight;
    overlay.width = dw;
    overlay.height = dh;

    const sw = sourceFrameWidth || video.videoWidth || 640;
    const sh = sourceFrameHeight || video.videoHeight || 480;
    scaleRef.current = getDisplayScale(video, sw, sh);
  }, [videoRef, sourceFrameWidth, sourceFrameHeight]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const onMeta = () => {
      syncCanvasSize();
      onVideoReady(video);
    };
    video.addEventListener("loadedmetadata", onMeta);
    window.addEventListener("resize", syncCanvasSize);

    return () => {
      video.removeEventListener("loadedmetadata", onMeta);
      window.removeEventListener("resize", syncCanvasSize);
    };
  }, [videoRef, syncCanvasSize, onVideoReady]);

  useEffect(() => {
    syncCanvasSize();
    const overlay = overlayRef.current;
    const scale = scaleRef.current;
    if (!overlay || !scale) return;
    const ctx = overlay.getContext("2d");
    if (!ctx) return;
    drawDetections(ctx, detections, selectedId, scale);
  }, [detections, selectedId, syncCanvasSize]);

  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const overlay = overlayRef.current;
    const scale = scaleRef.current;
    if (!overlay || !scale) return;
    const rect = overlay.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const hit = hitTest(detections, x, y, scale);
    onSelect(hit);
  };

  useEffect(() => {
    if (!running) {
      const ctx = overlayRef.current?.getContext("2d");
      ctx?.clearRect(0, 0, overlayRef.current!.width, overlayRef.current!.height);
    }
  }, [running]);

  return (
    <div className="viewer" style={cssZoom !== 1 ? { transform: `scale(${cssZoom})`, transformOrigin: "top center" } : undefined}>
      <video
        ref={videoRef as React.RefObject<HTMLVideoElement>}
        autoPlay
        muted
        playsInline
      />
      <canvas
        ref={overlayRef}
        className="overlay"
        onClick={handleClick}
        aria-label="Detection overlay"
      />
      <canvas ref={captureRef} className="capture" width={640} height={480} />
    </div>
  );
}

export function captureFrameCrop(
  video: HTMLVideoElement,
  box: Detection["box"],
  sourceW: number,
  sourceH: number
): string | null {
  const canvas = document.createElement("canvas");
  const vw = video.videoWidth || sourceW;
  const vh = video.videoHeight || sourceH;
  const sx = vw / sourceW;
  const sy = vh / sourceH;
  const x1 = Math.max(0, Math.floor(box.x1 * sx));
  const y1 = Math.max(0, Math.floor(box.y1 * sy));
  const x2 = Math.min(vw, Math.ceil(box.x2 * sx));
  const y2 = Math.min(vh, Math.ceil(box.y2 * sy));
  const w = Math.max(1, x2 - x1);
  const h = Math.max(1, y2 - y1);
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  if (!ctx) return null;
  ctx.drawImage(video, x1, y1, w, h, 0, 0, w, h);
  return canvas.toDataURL("image/jpeg", 0.85);
}
