import { useCallback, useEffect, useRef, useState } from "react";
import { CardNotFoundError, generateCard, getCard, wsDetectUrl } from "./api";
import SidePanel from "./components/SidePanel";
import Viewer, { captureFrameCrop } from "./components/Viewer";
import type { CardInfo, Detection, FrameResponse } from "./types";

const DEFAULT_CLASSES = [
  "person",
  "cup",
  "bottle",
  "laptop",
  "cell phone",
  "chair",
  "book",
  "dog",
  "cat",
];

const SAMPLE_MS = 200;

export default function App() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const frameIdRef = useRef(0);
  const intervalRef = useRef<number | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const selectedIdRef = useRef<string | null>(null);
  const generatingRef = useRef(false);
  const selectedClassRef = useRef<string | null>(null);
  const detectionsRef = useRef<Detection[]>([]);

  const [running, setRunning] = useState(false);
  const [status, setStatus] = useState("Idle");
  const [detections, setDetections] = useState<Detection[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [sourceW, setSourceW] = useState(640);
  const [sourceH, setSourceH] = useState(480);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [cardInfo, setCardInfo] = useState<CardInfo | null>(null);
  const [allCards, setAllCards] = useState<CardInfo[]>([]);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [enabledClasses, setEnabledClasses] = useState<Set<string>>(
    () => new Set(DEFAULT_CLASSES)
  );
  const [confidence, setConfidence] = useState(0.45);
  const [processingMs, setProcessingMs] = useState<number | null>(null);
  const [facingMode, setFacingMode] = useState<"environment" | "user">("environment");
  const [zoom, setZoom] = useState(0);
  const [hwZoomCaps, setHwZoomCaps] = useState<{ min: number; max: number } | null>(null);

  const lastSelectedRef = useRef<Detection | null>(null);
  const selected = detections.find((d) => d.id === selectedId) ?? null;
  // Keep the last visible state so the panel doesn't go blank when the object
  // temporarily leaves the frame. Only truly clear when selectedId becomes null.
  if (selected) lastSelectedRef.current = selected;
  const displaySelected = selected ?? (selectedId ? lastSelectedRef.current : null);

  const mergeDetections = useCallback(
    (incoming: FrameResponse["detections"], sw: number, sh: number) => {
      let sel = selectedIdRef.current;
      const gen = generatingRef.current;
      const prev = detectionsRef.current.find((d) => d.id === sel);

      if (sel && prev && !incoming.some((d) => d.id === sel)) {
        const matchClass = selectedClassRef.current ?? prev.className;
        const same = incoming.filter((d) => d.className === matchClass);
        if (same.length) {
          const best = same.reduce((a, b) =>
            a.confidence >= b.confidence ? a : b
          );
          sel = best.id;
          selectedIdRef.current = best.id;
          setSelectedId(best.id);
        }
      }

      const mapped: Detection[] = incoming.map((d) => ({
        ...d,
        sourceFrameWidth: sw,
        sourceFrameHeight: sh,
        selected: d.id === sel,
        generating: gen && d.id === sel,
        knownObject: gen && d.id === sel && prev?.knownObject ? true : d.knownObject,
        cardId:
          gen && d.id === sel && prev?.cardId ? prev.cardId : d.cardId,
      }));
      detectionsRef.current = mapped;
      setDetections(mapped);
      setSourceW(sw);
      setSourceH(sh);
    },
    []
  );

  const captureAndSend = useCallback(() => {
    const video = videoRef.current;
    const ws = wsRef.current;
    if (!video || !ws || ws.readyState !== WebSocket.OPEN) return;
    if (video.readyState < 2) return;

    const w = video.videoWidth || 640;
    const h = video.videoHeight || 480;
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, w, h);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.7);
    const base64 = dataUrl.split(",")[1];
    frameIdRef.current += 1;
    ws.send(
      JSON.stringify({
        frameId: frameIdRef.current,
        imageBase64: base64,
        classes: Array.from(enabledClasses),
        confidence,
      })
    );
  }, [enabledClasses, confidence]);

  const stop = useCallback(() => {
    if (intervalRef.current) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    wsRef.current?.close();
    wsRef.current = null;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setRunning(false);
    setStatus("Stopped");
    setDetections([]);
    setZoom(0);
    setHwZoomCaps(null);
  }, []);


  const detectHwZoom = useCallback((stream: MediaStream) => {
    const track = stream.getVideoTracks()[0];
    if (!track) return;
    const caps = track.getCapabilities() as MediaTrackCapabilities & {
      zoom?: { min: number; max: number };
    };
    setHwZoomCaps(caps.zoom ?? null);
    setZoom(0);
  }, []);

  // zoom is -10..+10; 0 = 1x. Scale = 2^(zoom/5): -10→0.25x, 0→1x, +10→4x
  const zoomScale = Math.pow(2, zoom / 5);

  const applyZoom = useCallback(async (value: number) => {
    setZoom(value);
    const track = streamRef.current?.getVideoTracks()[0];
    if (!track || !hwZoomCaps) return;
    // reset hw zoom when going neutral/negative; map 1..10 to hw range otherwise
    const hwValue = value <= 0
      ? hwZoomCaps.min
      : hwZoomCaps.min + ((value - 1) / 9) * (hwZoomCaps.max - hwZoomCaps.min);
    try {
      await track.applyConstraints({ advanced: [{ zoom: hwValue } as MediaTrackConstraintSet] });
    } catch {
      // hw zoom failed — CSS transform fallback via state is already applied
    }
  }, [hwZoomCaps]);

  const switchCamera = useCallback(async () => {
    const nextMode = facingMode === "environment" ? "user" : "environment";

    streamRef.current?.getTracks().forEach((t) => t.stop());

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: nextMode, width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      streamRef.current = stream;
      const video = videoRef.current;
      if (video) {
        video.srcObject = stream;
        await video.play();
      }
      detectHwZoom(stream);
      setFacingMode(nextMode);
    } catch {
      // nextMode camera not available — restore the current one
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      streamRef.current = stream;
      const video = videoRef.current;
      if (video) {
        video.srcObject = stream;
        await video.play();
      }
      detectHwZoom(stream);
    }
  }, [facingMode, detectHwZoom]);

  const start = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      streamRef.current = stream;
      const video = videoRef.current;
      if (video) {
        video.srcObject = stream;
        await video.play();
      }
      detectHwZoom(stream);

      const ws = new WebSocket(wsDetectUrl());
      wsRef.current = ws;
      setStatus("Connecting...");

      ws.onopen = () => {
        setStatus("Running");
        setRunning(true);
        intervalRef.current = window.setInterval(captureAndSend, SAMPLE_MS);
      };

      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data) as FrameResponse & { error?: string };
          if (data.error) {
            setStatus(data.error);
            return;
          }
          if (data.processingMs != null) setProcessingMs(data.processingMs);
          mergeDetections(
            data.detections,
            data.sourceFrameWidth,
            data.sourceFrameHeight
          );
        } catch {
          /* ignore */
        }
      };

      ws.onerror = () => setStatus("WebSocket error");
      ws.onclose = () => {
        if (running) setStatus("Disconnected");
      };
    } catch (e) {
      setStatus(
        e instanceof Error ? e.message : "Camera permission denied"
      );
    }
  }, [captureAndSend, mergeDetections, running, facingMode, detectHwZoom]);

  useEffect(() => {
    selectedIdRef.current = selectedId;
    setDetections((prev) =>
      prev.map((d) => ({
        ...d,
        selected: d.id === selectedId,
        generating: generating && d.id === selectedId,
      }))
    );
  }, [selectedId, generating]);

  // Clear everything only on explicit deselect (selectedId → null).
  // Never clear on frame-driven ID changes — that causes flicker.
  useEffect(() => {
    if (!selectedId) {
      lastSelectedRef.current = null;
      setPreviewUrl(null);
      setCardInfo(null);
      setStatusMessage(null);
    }
  }, [selectedId]);

  // Update the crop preview as the bounding box moves each frame
  useEffect(() => {
    const video = videoRef.current;
    if (!selected || !video) return; // keep last preview when object leaves frame
    const url = captureFrameCrop(
      video,
      selected.box,
      selected.sourceFrameWidth,
      selected.sourceFrameHeight
    );
    setPreviewUrl(url);
  }, [selected, sourceW, sourceH]);

  const registerCard = (card: CardInfo) => {
    setCardInfo(card);
    if (card.imageUrl) {
      setAllCards((prev) =>
        prev.some((c) => c.cardId === card.cardId) ? prev : [...prev, card]
      );
    }
  };

  const generateCardForDetection = async (det: Detection) => {
    generatingRef.current = true;
    setGenerating(true);
    setStatusMessage("Generating card...");
    setDetections((prev) =>
      prev.map((d) =>
        d.id === det.id ? { ...d, generating: true, selected: true } : d
      )
    );
    try {
      const { card, message } = await generateCard(
        det.id,
        det.className,
        det.confidence,
        det.box
      );
      registerCard(card);
      setStatusMessage(message);
      setDetections((prev) =>
        prev.map((d) =>
          d.id === det.id
            ? { ...d, knownObject: true, cardId: card.cardId, generating: false, selected: true }
            : d
        )
      );
    } catch {
      setStatusMessage("Card generation failed");
    } finally {
      generatingRef.current = false;
      setGenerating(false);
    }
  };

  const handleSelect = async (det: Detection | null) => {
    setSelectedId(det?.id ?? null);
    selectedIdRef.current = det?.id ?? null;
    setStatusMessage(null);

    if (!det) {
      selectedClassRef.current = null;
      return;
    }

    // Only reset card when the class changes; keep it while tracking the same object
    const classChanged = det.className !== selectedClassRef.current;
    selectedClassRef.current = det.className;
    if (classChanged) setCardInfo(null);

    if (det.knownObject && det.cardId) {
      try {
        const card = await getCard(det.cardId);
        if (card.imageUrl) {
          registerCard(card);
          setStatusMessage(`Card: ${card.name} (${card.className})`);
          return;
        }
      } catch (e) {
        if (e instanceof CardNotFoundError) {
          setDetections((prev) =>
            prev.map((d) =>
              d.id === det.id ? { ...d, knownObject: false, cardId: null } : d
            )
          );
        }
      }
    }

    // Same class already has a card loaded — no need to re-generate
    if (!classChanged && cardInfo?.imageUrl) return;

    // New object, missing image, or stale card — auto-generate
    await generateCardForDetection(det);
  };

  const toggleClass = (name: string) => {
    setEnabledClasses((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  return (
    <div className="app">
      <header>
        <h1>DetectoMon</h1>
        <p>Live camera detection with object cards</p>
      </header>

      <div className="controls">
        {!running ? (
          <button type="button" className="primary" onClick={start}>
            Start Camera
          </button>
        ) : (
          <button type="button" onClick={stop}>
            Stop
          </button>
        )}
        {running && (
          <button type="button" onClick={switchCamera}>
            {facingMode === "environment" ? "Use Front Camera" : "Use Rear Camera"}
          </button>
        )}
        <label>
          Confidence:{" "}
          <input
            type="range"
            min={0.2}
            max={0.9}
            step={0.05}
            value={confidence}
            onChange={(e) => setConfidence(Number(e.target.value))}
            disabled={running}
          />
          {confidence.toFixed(2)}
        </label>
        {running && (
          <label>
            Zoom:{" "}
            <input
              type="range"
              min={-10}
              max={10}
              step={1}
              value={zoom}
              onChange={(e) => applyZoom(Number(e.target.value))}
            />
            {zoom > 0 ? `+${zoom}` : zoom}
          </label>
        )}
        <span className="status">
          Status: {status}
          {processingMs != null && running && ` · ${processingMs}ms`}
        </span>
      </div>

      <div className="class-filters">
        {DEFAULT_CLASSES.map((c) => (
          <label key={c}>
            <input
              type="checkbox"
              checked={enabledClasses.has(c)}
              onChange={() => toggleClass(c)}
              disabled={running}
            />
            {c}
          </label>
        ))}
      </div>

      <div className="layout">
        <div>
          <div className="viewer-wrap">
          <Viewer
            videoRef={videoRef}
            detections={detections}
            selectedId={selectedId}
            sourceFrameWidth={sourceW}
            sourceFrameHeight={sourceH}
            running={running}
            onSelect={handleSelect}
            onVideoReady={() => {}}
            cssZoom={zoom > 0 && hwZoomCaps ? 1 : zoomScale}
          />
          </div>
          {detections.length > 0 && (
            <ul className="detection-list">
              {detections.map((d) => (
                <li key={d.id}>
                  {d.className} {(d.confidence * 100).toFixed(0)}%
                  {d.knownObject ? " · known" : " · new"}
                </li>
              ))}
            </ul>
          )}
        </div>

        <SidePanel
          selected={displaySelected}
          previewUrl={previewUrl}
          cardInfo={cardInfo}
          statusMessage={statusMessage}
          generating={generating}
        />
      </div>

      {allCards.length > 0 && (
        <div className="card-strip">
          {allCards.map((c) => (
            <img
              key={c.cardId}
              className={`card-strip__item${cardInfo?.cardId === c.cardId ? " card-strip__item--active" : ""}`}
              src={c.imageUrl!}
              alt={c.name}
              title={c.name}
            />
          ))}
        </div>
      )}
    </div>
  );
}
