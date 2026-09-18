import { useEffect, useRef, useState } from "react";
import { askQuestion } from "../api";
import { RoomStage } from "../components/RoomStage";
import { StressGauge } from "../components/StressGauge";
import { Timer } from "../components/Timer";
import { ChatLog } from "../components/ChatLog";
import { EvidencePanel } from "../components/EvidencePanel";
import { EvidenceFolder } from "../components/evidence/EvidenceFolder";
import { ActionBar } from "../components/ActionBar";

const ROUND_SECONDS = 12 * 60;

export function Interrogation({ session, onStatusChange }) {
  const [entries, setEntries] = useState([]);
  const [question, setQuestion] = useState("");
  const [stress, setStress] = useState(session.stress ?? 0);
  const [milestone, setMilestone] = useState(session.milestone ?? 0);
  const [evidenceFound, setEvidenceFound] = useState(session.evidence_found ?? []);
  const [openEvidence, setOpenEvidence] = useState(null);
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);
  const [secondsRemaining, setSecondsRemaining] = useState(ROUND_SECONDS);
  const [activeAction, setActiveAction] = useState("ask");
  const inputRef = useRef(null);

  const handleAction = (action) => {
    setActiveAction(action);
    if (action === "ask") {
      inputRef.current?.focus();
    }
    if (action === "evidence") {
      const firstUnlocked = evidenceFound[0];
      if (firstUnlocked) setOpenEvidence(firstUnlocked);
    }
  };

  useEffect(() => {
    const id = window.setInterval(() => {
      setSecondsRemaining((value) => Math.max(0, value - 1));
    }, 1000);
    return () => window.clearInterval(id);
  }, []);

  const handleSend = async () => {
    const trimmed = question.trim();
    if (!trimmed || sending) return;

    setSending(true);
    setError("");
    setEntries((prev) => [...prev, { role: "player", text: trimmed }]);
    setQuestion("");

    try {
      const result = await askQuestion(session.session_id, trimmed);
      setEntries((prev) => [...prev, { role: "adrian", text: result.response }]);
      setStress(result.stress);
      setMilestone(result.milestone);
      setEvidenceFound(result.evidence_found);
      if (result.status !== "ACTIVE") {
        onStatusChange({ ...session, ...result });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  };

  return (
    <main className="interrogation-shell">
      <RoomStage stress={stress}>
        <header className="stage-hud stage-hud-top">
          <div className="stage-brand">
            <span className="stage-brand-name">
              PROMPT <span className="start-x">X</span>
            </span>
            <small>{session.session_id}</small>
          </div>
          <Timer secondsRemaining={secondsRemaining} />
        </header>

        <footer className="stage-hud stage-hud-bottom">
          <StressGauge stress={stress} />
          <div className="milestone-readout">
            MILESTONE {String(milestone).padStart(2, "0")}/05
          </div>
        </footer>
      </RoomStage>

      <ActionBar active={activeAction} onSelect={handleAction} disabled={sending} />

      <div className="interrogation-body">
        <div className="interrogation-main">
          <ChatLog entries={entries} />

          {activeAction === "accuse" && (
            <section className="action-panel">
              <p className="panel-title">// FORMAL ACCUSATION</p>
              <p className="action-panel-body">
                An accusation is final. State it as a question that names the contradiction
                you have proven — Adrian will not break on an unsupported claim.
              </p>
              <p className="action-panel-note">
                Milestones completed: {milestone}/5. All five are required before a
                confession can be forced.
              </p>
              <button type="button" onClick={() => handleAction("ask")}>
                RETURN TO QUESTIONING
              </button>
            </section>
          )}

          {activeAction === "end" && (
            <section className="action-panel action-panel-warning">
              <p className="panel-title">// END SESSION</p>
              <p className="action-panel-body">
                Ending closes the interrogation. Your progress is recorded as-is and
                cannot be resumed.
              </p>
              <div className="action-panel-actions">
                <button type="button" onClick={() => handleAction("ask")}>
                  CANCEL
                </button>
                <button
                  type="button"
                  className="action-danger"
                  onClick={() => onStatusChange({ ...session, status: "ENDED", stress })}
                >
                  CONFIRM END
                </button>
              </div>
            </section>
          )}

          <section className="question-panel">
            <label className="panel-title" htmlFor="question">
              // ENTER_INTERROGATION
            </label>
            <textarea
              id="question"
              ref={inputRef}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Type your question here..."
              maxLength={500}
              disabled={sending}
            />
            <div className="question-actions">
              <span className="char-count">{question.length}/500</span>
              <button type="button" onClick={handleSend} disabled={sending}>
                {sending ? "SENDING..." : "SEND"}
              </button>
            </div>
            {error && <p className="error-text">{error}</p>}
          </section>
        </div>

        <EvidencePanel evidenceFound={evidenceFound} onSelect={setOpenEvidence} />
      </div>

      {openEvidence && (
        <EvidenceFolder evidenceId={openEvidence} onClose={() => setOpenEvidence(null)} />
      )}
    </main>
  );
}
