import { useEffect } from "react";
import { EVIDENCE_CONTENT, EVIDENCE_PHOTOS } from "../../data/evidenceContent";
import { WitnessStatementDoc } from "./WitnessStatementDoc";
import { FingerprintDoc } from "./FingerprintDoc";

function RecordDoc({ content }) {
  return (
    <div className="doc-body">
      <ol className="doc-timeline">
        {content.rows.map((row, index) => (
          <li key={index} className={row.flagged ? "doc-row doc-row-flagged" : "doc-row"}>
            <span className="doc-time">{row.time}</span>
            <span className="doc-event">{row.event}</span>
          </li>
        ))}
      </ol>
      <p className="doc-note">{content.note}</p>
    </div>
  );
}

function PhotoDoc({ photo }) {
  return (
    <div className="doc-body">
      <figure className="doc-photo">
        <img src={photo.src} alt={photo.caption} />
        <figcaption>{photo.caption}</figcaption>
      </figure>
      {photo.statement && <WitnessStatementDoc statement={photo.statement} />}
      {photo.forensics && <FingerprintDoc forensics={photo.forensics} />}
    </div>
  );
}

export function EvidenceFolder({ evidenceId, onClose, onPresent, presenting }) {
  useEffect(() => {
    const onKey = (event) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const textContent = EVIDENCE_CONTENT[evidenceId];
  const photoContent = EVIDENCE_PHOTOS[evidenceId];
  const header = textContent ?? photoContent;

  if (!header) return null;

  return (
    <div
      className="evidence-overlay"
      role="dialog"
      aria-modal="true"
      aria-label={header.title}
      onClick={onClose}
    >
      <article className="evidence-folder" onClick={(event) => event.stopPropagation()}>
        <header className="doc-head">
          <h3>{header.title}</h3>
          <span className="doc-ref">{header.reference}</span>
          <span className="doc-stamp">EVIDENCE</span>
        </header>

        {textContent ? <RecordDoc content={textContent} /> : <PhotoDoc photo={photoContent} />}

        <footer className="evidence-actions">
          <button type="button" className="evidence-inspect" autoFocus>INSPECT</button>
          <button type="button" className="evidence-present" onClick={() => onPresent(evidenceId)} disabled={presenting}>{presenting ? "PRESENTING..." : "PRESENT TO SUSPECT"}</button>
          <button type="button" className="doc-close" onClick={onClose}>CLOSE</button>
        </footer>
      </article>
    </div>
  );
}
