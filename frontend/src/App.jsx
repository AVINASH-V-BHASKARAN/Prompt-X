import { useState } from "react";
import { RoomStage } from "./components/RoomStage";
import "./styles/tokens.css";
import "./styles/app.css";

export default function App() {
  const [stress, setStress] = useState(0);

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: "1rem" }}>
      <RoomStage stress={stress} />
      <input
        type="range"
        min="0"
        max="100"
        value={stress}
        onChange={(event) => setStress(Number(event.target.value))}
        style={{ width: "100%", marginTop: "1rem" }}
      />
      <p>Stress: {stress}</p>
    </main>
  );
}
