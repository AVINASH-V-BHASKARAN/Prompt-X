export function DeskEvidenceStack({ evidenceFound, onOpen }) {
  const count = evidenceFound.length;

  return (
    <button
      type="button"
      className="desk-evidence"
      onClick={() => count > 0 && onOpen(evidenceFound[0])}
      disabled={count === 0}
      aria-label={
        count === 0
          ? "Evidence folder — empty, no evidence discovered yet"
          : `Evidence folder — ${count} of 5 files discovered, open`
      }
    >
      <img
        className="desk-evidence-img"
        src="/assets/props/evidence-stack.png"
        alt=""
        aria-hidden="true"
      />
      <span className="desk-evidence-count">
        {count}/5 FILES
      </span>
    </button>
  );
}
