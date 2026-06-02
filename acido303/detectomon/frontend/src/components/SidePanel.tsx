import type { CardInfo, Detection } from "../types";

type Props = {
  selected: Detection | null;
  previewUrl: string | null;
  cardInfo: CardInfo | null;
  statusMessage: string | null;
  generating: boolean;
};

export default function SidePanel({
  selected,
  previewUrl,
  cardInfo,
  statusMessage,
  generating,
}: Props) {
  if (!selected) {
    return (
      <aside className="panel">
        <h2>Selected Object</h2>
        <div className="card-slot card-slot--empty">
          <span className="card-slot__hint">Click a detection to inspect it</span>
        </div>
      </aside>
    );
  }

  const pct = Math.round(selected.confidence * 100);
  const status = generating
    ? "Generating card..."
    : selected.knownObject && selected.cardId
      ? "Already discovered"
      : "New object";

  return (
    <aside className="panel">
      <h2>Selected Object</h2>

      {/* Card slot — always visible at the top */}
      {cardInfo?.imageUrl ? (
        <img
          className="card-slot card-slot--art"
          src={cardInfo.imageUrl}
          alt={`${cardInfo.name} card art`}
        />
      ) : (
        <div className={`card-slot${generating ? " card-slot--generating" : " card-slot--empty"}`}>
          {previewUrl && (
            <img className="card-slot__preview" src={previewUrl} alt="Crop preview" />
          )}
          {generating && <span className="card-slot__hint">Generating image…</span>}
        </div>
      )}

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

      {statusMessage && <div className="badge-msg">{statusMessage}</div>}
    </aside>
  );
}
