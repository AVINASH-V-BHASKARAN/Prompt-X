export function RoomStage({ stress = 0, children }) {
  const intensity = Math.min(1, stress / 100);

  return (
    <div className="room-stage" style={{ "--stage-intensity": intensity }}>
      <img
        className="room-plate"
        src="/assets/environment/interrogation-room-plate.png"
        alt=""
        aria-hidden="true"
      />
      <img
        className="room-suspect"
        src="/assets/character/suspect-portrait-source.png"
        alt="Adrian Vale"
      />
      <div className="room-scanlines" aria-hidden="true" />
      <div className="room-grain" aria-hidden="true" />
      <div className="room-vignette" aria-hidden="true" />
      <div className="room-content">{children}</div>
    </div>
  );
}
