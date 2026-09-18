import { EVIDENCE_CONTENT, EVIDENCE_PHOTOS } from "../data/evidenceContent";

const PHOTO_IDS = new Set(Object.keys(EVIDENCE_PHOTOS));

export function DeskEvidenceStack({ evidenceFound, onOpen }) {
  return (
    <section className="desk-evidence" aria-label="Evidence on desk">
      <div className="desk-case-folder" aria-hidden="true"><img src="/assets/props/desk-case-file.png" alt="" /></div>
      {evidenceFound.map((id, index) => {
        const item = EVIDENCE_CONTENT[id] ?? EVIDENCE_PHOTOS[id];
        if (!item) return null;
        const photo = PHOTO_IDS.has(id);
        return (
          <button key={id} type="button" className={`desk-file desk-file-${index}${photo ? " desk-file-photo" : ""}`} onClick={() => onOpen(id)} aria-label={`Open ${item.title}`}>
            {photo ? <img src={item.src} alt="" /> : <span className="desk-file-paper"><i>EX-{String(index + 1).padStart(2, "0")}</i><strong>{item.title}</strong><em>{item.reference}</em></span>}
            <span className="desk-file-label">{item.title}</span>
          </button>
        );
      })}
    </section>
  );
}
