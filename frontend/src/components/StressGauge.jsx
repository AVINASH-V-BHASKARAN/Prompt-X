// Bands from the design guide's stress scale. Colour walks from the calm
// terminal green through amber to the warning red as pressure builds.
const BANDS = [
  { max: 20, label: "CALM", color: "var(--px-terminal)" },
  { max: 40, label: "DEFENSIVE", color: "#b9c96a" },
  { max: 60, label: "IRRITATED", color: "var(--px-tungsten)" },
  { max: 80, label: "AGITATED", color: "#c2652f" },
  { max: 95, label: "UNSTABLE", color: "var(--px-warning)" },
  { max: 100, label: "BREAKING", color: "#d43b2f" },
];

function stressBand(stress) {
  return BANDS.find((band) => stress <= band.max) ?? BANDS[BANDS.length - 1];
}

export function StressGauge({ stress }) {
  const band = stressBand(stress);

  return (
    <div
      className={`stress-gauge${band.label === "BREAKING" ? " stress-gauge-breaking" : ""}`}
      style={{ "--stress-color": band.color }}
    >
      <div className="stress-gauge-head">
        <span>SUSPECT STRESS</span>
        <span className="stress-gauge-state">{band.label}</span>
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
