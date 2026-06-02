export type Box = {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
};

export type Detection = {
  id: string;
  className: string;
  confidence: number;
  box: Box;
  sourceFrameWidth: number;
  sourceFrameHeight: number;
  selected?: boolean;
  knownObject?: boolean;
  cardId?: string | null;
  generating?: boolean;
};

export type FrameResponse = {
  frameId: number;
  sourceFrameWidth: number;
  sourceFrameHeight: number;
  detections: Array<{
    id: string;
    className: string;
    confidence: number;
    box: Box;
    knownObject?: boolean;
    cardId?: string | null;
  }>;
  processingMs?: number;
};

export type CardInfo = {
  cardId: string;
  name: string;
  className: string;
  detectionId: string;
  reused: boolean;
  imageUrl?: string | null;
};
