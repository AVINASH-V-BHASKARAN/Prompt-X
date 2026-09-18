export function RoomStage({ stress = 0, tune, children }) {
  const intensity = Math.min(1, stress / 100);

  const style = { "--stage-intensity": intensity };
  if (tune) {
    style["--suspect-width"] = `${tune.width}vw`;
    style["--suspect-bottom"] = `${tune.bottom}%`;
    style["--suspect-left"] = `${tune.left}%`;
    style["--suspect-brightness"] = tune.brightness / 100;
  }

  return (
    <div className="room-stage" style={style}>
      <img
        className="room-plate"
        src="/assets/environment/interrogation-room-plate.png"
        alt=""
        aria-hidden="true"
      />
      <div className="room-suspect-glow" aria-hidden="true" />
      <img
        className="room-suspect"
        src="/assets/character/suspect-portrait-source.png"
        alt="Adrian Vale"
      />
      <div className="room-desk-occluder" aria-hidden="true" />
      <div className="room-scanlines" aria-hidden="true" />
      <div className="room-grain" aria-hidden="true" />
      <div className="room-vignette" aria-hidden="true" />
      <div className="room-content">{children}</div>
    </div>
  );
}
