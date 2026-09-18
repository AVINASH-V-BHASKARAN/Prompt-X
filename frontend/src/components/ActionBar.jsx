const ACTIONS = [
  { id: "ask", label: "ASK QUESTION" },
  { id: "evidence", label: "SHOW EVIDENCE" },
  { id: "accuse", label: "ACCUSE" },
  { id: "end", label: "END" },
];

export function ActionBar({ active, onSelect, disabled }) {
  return (
    <nav className="action-bar" aria-label="Case actions">
      {ACTIONS.map((action) => {
        const isActive = active === action.id;
        return (
          <button
            key={action.id}
            type="button"
            className={`action-button${isActive ? " action-active" : ""}`}
            aria-current={isActive ? "true" : undefined}
            disabled={disabled}
            onClick={() => onSelect(action.id)}
          >
            <span className="action-caret" aria-hidden="true">
              {isActive ? "▸" : ""}
            </span>
            {action.label}
          </button>
        );
      })}
    </nav>
  );
}
