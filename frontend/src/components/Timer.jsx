export function Timer({ secondsRemaining }) {
  const safe = Math.max(0, secondsRemaining);
  const minutes = String(Math.floor(safe / 60)).padStart(2, "0");
  const seconds = String(safe % 60).padStart(2, "0");
  const critical = safe <= 60;

  return (
    <div className={`timer${critical ? " timer-critical" : ""}`}>
      <span className="timer-label">TIME</span>
      <span className="timer-value">
        {minutes}:{seconds}
      </span>
    </div>
  );
}
