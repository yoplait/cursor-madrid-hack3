import { useCallback, useEffect, useRef, useState } from "react";
import { generateCard, getCard, wsDetectUrl } from "./api";
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
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [enabledClasses, setEnabledClasses] = useState<Set<string>>(
    () => new Set(DEFAULT_CLASSES)
  );
  const [confidence, setConfidence] = useState(0.45);
  const [processingMs, setProcessingMs] = useState<number | null>(null);

  const selected =
    detections.find((d) => d.id === selectedId) ?? null;

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
  }, []);

  const start = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      streamRef.current = stream;
      const video = videoRef.current;
      if (video) {
        video.srcObject = stream;
        await video.play();
      }

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
  }, [captureAndSend, mergeDetections, running]);

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

  useEffect(() => {
    const video = videoRef.current;
    if (!selected || !video) {
      setPreviewUrl(null);
      return;
    }
    const url = captureFrameCrop(
      video,
      selected.box,
      selected.sourceFrameWidth,
      selected.sourceFrameHeight
    );
    setPreviewUrl(url);
    setCardInfo(null);
    setStatusMessage(null);
  }, [selected, sourceW, sourceH]);

  const handleSelect = (det: Detection | null) => {
    setSelectedId(det?.id ?? null);
    selectedIdRef.current = det?.id ?? null;
    selectedClassRef.current = det?.className ?? null;
    setStatusMessage(null);
    setCardInfo(null);
  };

  const handleGenerate = async () => {
    if (!selected) return;
    generatingRef.current = true;
    setGenerating(true);
    setStatusMessage("Generating card...");
    setDetections((prev) =>
      prev.map((d) =>
        d.id === selected.id ? { ...d, generating: true, selected: true } : d
      )
    );

    try {
      const { card, message } = await generateCard(
        selected.id,
        selected.className,
        selected.confidence,
        selected.box
      );
      setCardInfo(card);
      setStatusMessage(message);
      setDetections((prev) =>
        prev.map((d) =>
          d.id === selected.id
            ? {
                ...d,
                knownObject: true,
                cardId: card.cardId,
                generating: false,
                selected: true,
              }
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

  const handleShowCard = async () => {
    if (!selected?.cardId) return;
    try {
      const card = await getCard(selected.cardId);
      setCardInfo(card);
      setStatusMessage(`Card: ${card.name} (${card.className})`);
    } catch {
      setStatusMessage("Could not load card");
    }
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
          <Viewer
            videoRef={videoRef}
            detections={detections}
            selectedId={selectedId}
            sourceFrameWidth={sourceW}
            sourceFrameHeight={sourceH}
            running={running}
            onSelect={handleSelect}
            onVideoReady={() => {}}
          />
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
          selected={selected}
          previewUrl={previewUrl}
          cardInfo={cardInfo}
          statusMessage={statusMessage}
          generating={generating}
          onGenerate={handleGenerate}
          onShowCard={handleShowCard}
        />
      </div>
    </div>
  );
}
