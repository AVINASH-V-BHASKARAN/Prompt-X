import "./styles/tokens.css";
import "./styles/app.css";

export default function App() {
  return (
    <main style={{ padding: "2rem" }}>
      <h1>PROMPT X</h1>
      <p style={{ color: "var(--px-terminal-dim)" }}>Token check: dim terminal text</p>
      <p style={{ color: "var(--px-warning)" }}>Token check: warning red</p>
      <p style={{ color: "var(--px-paper)" }}>Token check: paper</p>
      <img
        src="/assets/environment/interrogation-room-plate.png"
        alt="Interrogation room"
        style={{ maxWidth: "480px", border: "1px solid var(--px-hairline)" }}
      />
    </main>
  );
}
