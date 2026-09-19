import { Canvas } from "@react-three/fiber";
import { ChevronRight, Play, Send } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { InterrogationScene } from "./InterrogationScene";
import suspectImage from "../assets/suspect.png";
import deskImage from "../assets/interrogation-desk.png";
import lampImage from "../assets/hanging-lamp.png";
import monitorImage from "../assets/security-monitor.png";
import cameraImage from "../assets/security-camera.png";
import doorImage from "../assets/room-door.png";
import signImage from "../assets/people-lie-sign.png";
import photosImage from "../assets/evidence-photos.png";

const responses = [
  "I mean, yeah. I have hammers. I’m a contractor, man. I got a whole truck full of tools. You think I work construction without tools?",
  "I already told you. I left the site before nine. Ask the night foreman if you don't believe me.",
  "That photograph proves nothing. Plenty of people wear that jacket around the yard.",
];

export function InterrogationApp() {
  const stageRef = useRef<HTMLDivElement>(null);
  const [stress, setStress] = useState(62);
  const [time, setTime] = useState(14 * 60 + 37);
  const [prompts, setPrompts] = useState(15);
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(responses[0]);
  const [status, setStatus] = useState("TRUTH ALWAYS SURFACES");

  useEffect(() => {
    const timer = window.setInterval(() => setTime((current) => Math.max(0, current - 1)), 1000);
    return () => window.clearInterval(timer);
  }, []);

  const sendQuestion = () => {
    if (!question.trim() || prompts <= 0) return;
    const next = responses[(15 - prompts + 1) % responses.length] ?? responses[0];
    setResponse(next);
    setPrompts((value) => Math.max(0, value - 1));
    setStress((value) => Math.min(96, value + 7));
    setQuestion("");
    setStatus("ANALYZING RESPONSE...");
    window.setTimeout(() => setStatus("INCONSISTENCY DETECTED"), 900);
  };

  const minutes = Math.floor(time / 60).toString().padStart(2, "0");
  const seconds = (time % 60).toString().padStart(2, "0");

  const moveScene = (event: React.PointerEvent<HTMLElement>) => {
    const stage = stageRef.current;
    if (!stage) return;
    const bounds = stage.getBoundingClientRect();
    stage.style.setProperty("--look-x", `${((event.clientX - bounds.left) / bounds.width - 0.5) * 2}`);
    stage.style.setProperty("--look-y", `${((event.clientY - bounds.top) / bounds.height - 0.5) * 2}`);
  };

  return (
    <main className="interrogation-shell" onPointerMove={moveScene}>
      <div className="interrogation-stage" ref={stageRef}>
      <Canvas dpr={1} shadows flat camera={{ position: [0, 0.15, 8.7], fov: 48 }}>
        <InterrogationScene />
      </Canvas>

      <div className="room-props" aria-hidden="true">
        <img className="prop prop-door" src={doorImage} alt="" />
        <img className="prop prop-sign" src={signImage} alt="" />
        <img className="prop prop-camera" src={cameraImage} alt="" />
        <img className="prop prop-monitor" src={monitorImage} alt="" />
        <img className="prop prop-lamp" src={lampImage} alt="" />
        <img className="prop prop-suspect" src={suspectImage} alt="" />
        <img className="prop prop-desk" src={deskImage} alt="" />
        <img className="prop prop-photos" src={photosImage} alt="" />
      </div>

      <div className="crt-grain" aria-hidden="true" />
      <div className="vignette" aria-hidden="true" />

      <header className="top-hud">
        <div className="brand-block">
          <div className="prompt-mark">PROMPT <span>×</span></div>
          <small>INTERROGATION PROTOCOL<br />v1.0.0</small>
        </div>
        <div className="stress-meter" aria-label={`Suspect stress level ${stress} percent`}>
          <div className="meter-track"><div className="meter-fill" style={{ width: `${stress}%` }} /></div>
        </div>
        <div className="stress-label">SUSPECT STRESS LEVEL</div>
      </header>

      <section className="dialog-panel response-panel">
        <div className="panel-title">//&nbsp;&nbsp; SUSPECT RESPONSE</div>
        <p>{response}</p>
        <button className="icon-control" aria-label="Replay suspect response" title="Replay response"><Play size={22} fill="currentColor" /></button>
      </section>

      <section className="dialog-panel question-panel">
        <label className="panel-title" htmlFor="question">//&nbsp;&nbsp; ENTER_INTERROGATION ...</label>
        <textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); sendQuestion(); } }} placeholder="Type your question here..." />
        <button className="send-control" onClick={sendQuestion}><Send size={22} fill="currentColor" /> SEND</button>
      </section>

      <div className="evidence-stack" aria-label="Evidence files">
        <div /><div /><div /><strong>EVIDENCE</strong>
      </div>

      <nav className="case-actions" aria-label="Case actions">
        {["ASK QUESTION", "SHOW EVIDENCE", "ACCUSE", "END"].map((item, index) => (
          <button key={item} className={index === 0 ? "active" : ""} onClick={() => index === 0 && document.getElementById("question")?.focus()}>
            {index === 0 && <ChevronRight size={18} fill="currentColor" />}{item}
          </button>
        ))}
      </nav>

      <footer className="bottom-hud">
        <div><b>PROMPT X</b><small>— {status}</small></div>
        <div className="session-stats"><span>TIME REMAINING&nbsp;&nbsp; {minutes}:{seconds}</span><i /> <span>PROMPTS LEFT&nbsp;&nbsp; {prompts}</span></div>
      </footer>
      </div>
    </main>
  );
}