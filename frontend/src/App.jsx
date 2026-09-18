import { useState } from "react";
import { Start } from "./pages/Start";
import { Interrogation } from "./pages/Interrogation";
import { Confession } from "./pages/Confession";
import "./styles/tokens.css";
import "./styles/app.css";

export default function App() {
  const [session, setSession] = useState(null);

  if (!session) {
    return <Start onStarted={setSession} />;
  }

  if (session.status === "CONFESSION" || session.status === "ENDED") {
    return <Confession session={session} />;
  }

  return <Interrogation session={session} onStatusChange={setSession} />;
}
