import type { CardInfo, Detection } from "../types";

type Props = {
  selected: Detection | null;
  previewUrl: string | null;
  cardInfo: CardInfo | null;
  statusMessage: string | null;
  generating: boolean;
  onGenerate: () => void;
  onShowCard: () => void;
};

export default function SidePanel({
  selected,
  previewUrl,
  cardInfo,
  statusMessage,
  generating,
  onGenerate,
  onShowCard,
}: Props) {
  if (!selected) {
    return (
      <aside className="panel">
        <h2>Selected Object</h2>
        <p className="status">Click a detection on the video to inspect it.</p>
      </aside>
    );
  }

  const pct = Math.round(selected.confidence * 100);
  const isKnown = selected.knownObject && selected.cardId;
  const status = generating
    ? "Generating card..."
    : isKnown
      ? "Already discovered"
      : "New object";

  return (
    <aside className="panel">
      <h2>Selected Object</h2>
      <div className="field">
        <strong>Class:</strong> {selected.className}
      </div>
      <div className="field">
        <strong>Confidence:</strong> {pct}%
      </div>
      <div className="field">
        <strong>Status:</strong> {status}
      </div>
      {cardInfo && (
        <div className="field">
          <strong>Card:</strong> {cardInfo.name}
        </div>
      )}
      {previewUrl && (
        <img className="preview" src={previewUrl} alt="Crop preview" />
      )}
      <div className="panel-actions">
        {isKnown ? (
          <button type="button" className="show" onClick={onShowCard}>
            Show Card
          </button>
        ) : (
          <button
            type="button"
            className="generate"
            onClick={onGenerate}
            disabled={generating}
          >
            {generating ? "Generating..." : "Generate Card"}
          </button>
        )}
      </div>
      {statusMessage && <div className="badge-msg">{statusMessage}</div>}
    </aside>
  );
}
