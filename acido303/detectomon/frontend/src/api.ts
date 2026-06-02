import type { Box, CardInfo } from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export async function generateCard(
  detectionId: string,
  className: string,
  confidence: number,
  box: Box
): Promise<{ card: CardInfo; message: string }> {
  const res = await fetch(`${API_BASE}/api/cards/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ detectionId, className, confidence, box }),
  });
  if (!res.ok) throw new Error("Failed to generate card");
  return res.json();
}

export async function getCard(cardId: string): Promise<CardInfo> {
  const res = await fetch(`${API_BASE}/api/cards/${cardId}`);
  if (!res.ok) throw new Error("Card not found");
  return res.json();
}

export function wsDetectUrl(): string {
  const base = import.meta.env.VITE_WS_URL;
  if (base) return base;
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host =
    import.meta.env.DEV ? "127.0.0.1:8000" : window.location.host;
  return `${proto}//${host}/ws/detect`;
}
