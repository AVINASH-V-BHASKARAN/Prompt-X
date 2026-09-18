export const EVIDENCE_CONTENT = {
  access_card: {
    title: "ACCESS CARD RECORD",
    reference: "EX-01 / BADGE-4471",
    rows: [
      { time: "18:02", event: "ENTRY — Main Lobby", flagged: false },
      { time: "20:47", event: "ENTRY — Level 3 Corridor", flagged: false },
      { time: "21:15", event: "NO EXIT LOGGED", flagged: true },
      { time: "21:39", event: "ENTRY — Archive Room", flagged: true },
    ],
    note: "Card assigned to A. VALE. No exit scan recorded before the 21:39 entry.",
  },
  phone_records: {
    title: "PHONE RECORD",
    reference: "EX-03 / LINE-0092",
    rows: [
      { time: "19:58", event: "OUTGOING — D. MERCER (4m 12s)", flagged: false },
      { time: "21:06", event: "INCOMING — D. MERCER (0m 48s)", flagged: true },
      { time: "21:31", event: "OUTGOING — D. MERCER (unanswered)", flagged: true },
    ],
    note: "Three contacts logged with the victim on the night in question.",
  },
  victim_files: {
    title: "ARCHIVE FILE",
    reference: "EX-04 / CASE-MERCER",
    rows: [
      { time: "—", event: "Forensic dataset revision history", flagged: false },
      { time: "—", event: "12 records altered post-submission", flagged: true },
      { time: "—", event: "Editor credential: A. VALE", flagged: true },
    ],
    note: "Victim compiled evidence of dataset manipulation prior to his death.",
  },
};

export const EVIDENCE_PHOTOS = {
  cctv: {
    title: "CCTV FRAGMENT",
    reference: "EX-02 / CAM-07",
    src: "/assets/evidence/cctv-corridor-photo.png",
    caption: "Archive corridor, 21:38. Figure consistent with suspect build.",
  },
  physical_clue: {
    title: "FINAL EVIDENCE",
    reference: "EX-05 / ITEM-113",
    src: "/assets/evidence/hammer-tool-photo.png",
    caption: "Recovered blunt instrument. Partial print lifted from the grip.",
  },
};
