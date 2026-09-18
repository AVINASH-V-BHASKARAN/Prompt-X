function stressLabel(stress) {
  if (stress <= 20) return "CALM";
  if (stress <= 40) return "DEFENSIVE";
  if (stress <= 60) return "IRRITATED";
  if (stress <= 80) return "AGITATED";
  if (stress <= 95) return "UNSTABLE";
  return "BREAKING";
}

export function StressGauge({ stress }) {
  return (
    <div className="stress-gauge">
      <div className="stress-gauge-head">
        <span>SUSPECT STRESS</span>
        <span className="stress-gauge-state">{stressLabel(stress)}</span>
      </div>
      <div
        className="stress-track"
        role="meter"
        aria-valuenow={stress}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Suspect stress level"
      >
        <div className="stress-fill" style={{ "--stress-scale": stress / 100 }} />
      </div>
      <div className="stress-value">{stress}%</div>
    </div>
  );
}
