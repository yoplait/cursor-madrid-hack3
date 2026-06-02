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

export class CardNotFoundError extends Error {}

export async function getCard(cardId: string): Promise<CardInfo> {
  const res = await fetch(`${API_BASE}/api/cards/${cardId}`);
  if (res.status === 404) throw new CardNotFoundError("Card not found");
  if (!res.ok) throw new Error("Failed to fetch card");
  return res.json();
}

export function wsDetectUrl(): string {
  const base = import.meta.env.VITE_WS_URL;
  if (base) return base;
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}/ws/detect`;
}
