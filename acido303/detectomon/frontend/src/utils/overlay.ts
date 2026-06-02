import type { Detection } from "../types";

export type DisplayScale = {
  scaleX: number;
  scaleY: number;
  displayW: number;
  displayH: number;
};

export function getDisplayScale(
  videoEl: HTMLVideoElement,
  sourceW: number,
  sourceH: number
): DisplayScale {
  const displayW = videoEl.clientWidth;
  const displayH = videoEl.clientHeight;
  return {
    displayW,
    displayH,
    scaleX: displayW / sourceW,
    scaleY: displayH / sourceH,
  };
}

export function toDisplayBox(
  box: Detection["box"],
  scale: DisplayScale
): { x1: number; y1: number; x2: number; y2: number } {
  return {
    x1: box.x1 * scale.scaleX,
    y1: box.y1 * scale.scaleY,
    x2: box.x2 * scale.scaleX,
    y2: box.y2 * scale.scaleY,
  };
}

export function hitTest(
  detections: Detection[],
  canvasX: number,
  canvasY: number,
  scale: DisplayScale
): Detection | null {
  let best: Detection | null = null;
  let bestConf = -1;

  for (const d of detections) {
    const b = toDisplayBox(d.box, scale);
    if (
      canvasX >= b.x1 &&
      canvasX <= b.x2 &&
      canvasY >= b.y1 &&
      canvasY <= b.y2 &&
      d.confidence > bestConf
    ) {
      best = d;
      bestConf = d.confidence;
    }
  }
  return best;
}

type DrawState = "normal" | "selected" | "known" | "new" | "generating";

function stateFor(d: Detection, selectedId: string | null): DrawState {
  if (d.generating) return "generating";
  if (d.id === selectedId) return "selected";
  if (d.knownObject) return "known";
  if (!d.knownObject) return "new";
  return "normal";
}

const COLORS: Record<DrawState, { stroke: string; fill: string; badge: string }> =
  {
    normal: { stroke: "#4ade80", fill: "rgba(74, 222, 128, 0.12)", badge: "" },
    selected: {
      stroke: "#60a5fa",
      fill: "rgba(96, 165, 250, 0.2)",
      badge: "selected",
    },
    known: {
      stroke: "#a78bfa",
      fill: "rgba(167, 139, 250, 0.15)",
      badge: "Already discovered",
    },
    new: {
      stroke: "#fbbf24",
      fill: "rgba(251, 191, 36, 0.12)",
      badge: "New object",
    },
    generating: {
      stroke: "#f472b6",
      fill: "rgba(244, 114, 182, 0.15)",
      badge: "Generating card...",
    },
  };

export function drawDetections(
  ctx: CanvasRenderingContext2D,
  detections: Detection[],
  selectedId: string | null,
  scale: DisplayScale
) {
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

  for (const d of detections) {
    const state = stateFor(d, selectedId);
    const colors = COLORS[state];
    const b = toDisplayBox(d.box, scale);
    const w = b.x2 - b.x1;
    const h = b.y2 - b.y1;

    ctx.fillStyle = colors.fill;
    ctx.fillRect(b.x1, b.y1, w, h);

    ctx.strokeStyle = colors.stroke;
    ctx.lineWidth = state === "selected" ? 4 : 2;
    if (state === "selected") {
      ctx.shadowColor = colors.stroke;
      ctx.shadowBlur = 12;
    }
    ctx.strokeRect(b.x1, b.y1, w, h);
    ctx.shadowBlur = 0;

    const pct = Math.round(d.confidence * 100);
    let label = `${d.className} ${pct}%`;
    if (state === "selected") label += " — selected";

    ctx.font = "bold 13px system-ui, sans-serif";
    const tm = ctx.measureText(label);
    const labelH = 18;
    ctx.fillStyle = "rgba(0,0,0,0.65)";
    ctx.fillRect(b.x1, b.y1 - labelH, tm.width + 8, labelH);
    ctx.fillStyle = "#fff";
    ctx.fillText(label, b.x1 + 4, b.y1 - 5);

    if (colors.badge) {
      ctx.font = "11px system-ui, sans-serif";
      const badge = colors.badge;
      const bm = ctx.measureText(badge);
      const by = b.y2 + 14;
      ctx.fillStyle = "rgba(0,0,0,0.7)";
      ctx.fillRect(b.x1, by - 12, bm.width + 8, 14);
      ctx.fillStyle =
        state === "generating" ? "#f9a8d4" : state === "known" ? "#c4b5fd" : "#fde68a";
      ctx.fillText(badge, b.x1 + 4, by);
    }
  }
}
