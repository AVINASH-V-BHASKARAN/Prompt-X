import asyncio
import os
import time
import sys
import re
import difflib

sys.stdout.reconfigure(encoding='utf-8')

from google import genai
from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

MODEL = "gemini-3.5-flash-lite"

# Load environment variable or local .env if available
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY and os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as _env_file:
        for _line in _env_file:
            if _line.strip().startswith("GEMINI_API_KEY="):
                API_KEY = _line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                break

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found.\n"
        "Please set your GEMINI_API_KEY environment variable or define it in a local .env file."
    )

client = genai.Client(api_key=API_KEY)


# ============================================================
# AUTHORITATIVE CASE DATABASE (Rule 1: Case Database is Authoritative)
# ============================================================

CASE_FACTS = {
    "timeline": {
        "adrian_claimed_left_21_15": True,
        "card_used_21_39": True,
        "adrian_present_after_21_15": True
    },
    "location": {
        "adrian_near_archive_21_37": True,
        "archive_access_subbasement": True
    },
    "contact": {
        "phone_call_21_32": True,
        "adrian_contacted_daniel": True
    },
    "motive": {
        "daniel_discovered_tampering": True,
        "files_link_adrian_to_tampering": True,
        "adrian_wanted_information_hidden": True,
        "attempted_wipe_project_echo": True
    },
    "physical": {
        "blue_nitrile_glove_fragment": True,
        "missing_gloves_from_desk": True,
        "paperweight_murder_weapon": True
    }
}

# The 3 facts required to deterministically prove Motive (Section 7)
MOTIVE_FACTS = {
    "daniel_discovered_tampering",
    "files_link_adrian_to_tampering",
    "adrian_wanted_information_hidden"
}

# Case Solution Score Weights (Section 15)
CASE_WEIGHTS = {
    "timeline": 20,
    "location": 20,
    "contact": 15,
    "motive": 25,
    "physical": 10,
    "final": 10
}

# Stress Delta System (Section 5)
STRESS_VALUES = {
    "GENERIC": 0,
    "IRRELEVANT": 0,
    "REPEATED": 0,
    "RELEVANT": 2,
    "CLUE": 5,
    "INCONSISTENCY": 10,
    "EVIDENCE": 15,
    "CONNECTION": 20,
    "MAJOR_CONTRADICTION": 25
}

# Confession Thresholds (Section 14)
NORMAL_CONFESSION_THRESHOLD = 85
CASE_SOLVED_THRESHOLD = 75
REQUIRED_CASE_SCORE = 90


# ============================================================
# EVIDENCE METADATA (Section 6)
# ============================================================

EVIDENCE_DEFINITIONS = {
    "access_card": {
        "name": "Access Card #0890 (Sub-Basement at 21:39)",
        "category": "TIMELINE",
        "facts_supported": ["card_used_21_39", "adrian_present_after_21_15"],
        "keywords": ["keycard", "card", "badge", "rfid", "0890", "8804", "2139", "939", "swipe", "fire door"]
    },
    "cctv": {
        "name": "CCTV Reflection (Corridor Camera B at 21:37)",
        "category": "LOCATION",
        "facts_supported": ["adrian_near_archive_21_37", "adrian_present_after_21_15"],
        "keywords": ["cctv", "camera", "reflection", "coat", "jacket", "trophy", "2137", "937", "surveillance", "footage"]
    },
    "phone_records": {
        "name": "Cellular Records (14-second link to Daniel at 21:32)",
        "category": "CONTACT",
        "facts_supported": ["phone_call_21_32", "adrian_contacted_daniel"],
        "keywords": ["phone", "call", "14 second", "14second", "14s", "cellular", "workstation", "antenna", "2132", "932", "microcell"]
    },
    "daniel_files": {
        "name": "Daniel's Audit & PROJECT_ECHO (Attempted Wipe at 21:28)",
        "category": "MOTIVE",
        "facts_supported": [
            "daniel_discovered_tampering",
            "files_link_adrian_to_tampering",
            "adrian_wanted_information_hidden",
            "attempted_wipe_project_echo"
        ],
        "keywords": ["echo", "projectecho", "wipe", "audit", "developer signature", "signature", "ip address", "2128", "928", "tampering", "altered", "manipulated", "fake records", "falsified", "records", "files"]
    },
    "physical_clue": {
        "name": "Blue Nitrile Glove Fragment on Paperweight Weapon",
        "category": "PHYSICAL",
        "facts_supported": ["blue_nitrile_glove_fragment", "missing_gloves_from_desk", "paperweight_murder_weapon"],
        "keywords": ["glove", "gloves", "nitrile", "rubber", "paperweight", "brass", "latch", "weapon", "missing glove", "two missing", "chemical", "compound", "fragment"]
    }
}


# ============================================================
# DEFENCE ROTATION CATALOGUE (Section 19 & 20)
# ============================================================

AVAILABLE_DEFENCES = {
    "access_card": [
        "card_cloned_or_borrowed",
        "card_left_on_desk",
        "system_timestamp_glitch"
    ],
    "cctv": [
        "reflection_is_distorted",
        "corridor_does_not_mean_archive",
        "coat_is_not_unique"
    ],
    "phone_records": [
        "automatic_system_ping",
        "call_does_not_prove_conversation",
        "network_routing_artifact"
    ],
    "daniel_files": [
        "ip_address_was_spoofed",
        "old_signature_reused_in_codebase",
        "routine_maintenance_misinterpreted",
        "daniel_looked_into_irrelevant_files"
    ],
    "physical_clue": [
        "gloves_are_standard_issue",
        "anyone_could_take_gloves_from_desk",
        "contamination_in_shared_lab"
    ]
}


# ============================================================
# GAME STATE CLASS (Section 20 & 56)
# ============================================================

class GameState:
    def __init__(self, session_id="PX-001"):
        self.session_id = session_id
        self.turn = 0
        self.stress = 0
        self.stress_state = "CALM"
        self.status = "ACTIVE"  # ACTIVE, CONFESSION, TIMEOUT, DISQUALIFIED

        # 4 Discrete State Systems (Section 3)
        self.evidence_revealed = set()
        self.facts_established = set()
        self.contradictions_exposed = set()
        self.milestones = {
            "timeline": False,
            "location": False,
            "contact": False,
            "motive": False,
            "final": False
        }

        # Repetition & Defence Memory (Section 18, 19, 21, 38)
        self.question_history = []
        self.recent_responses = []
        self.used_defences = set()
        self.recent_defences = []
        self.recent_strategies = []

        # Adrian Claims Tracking (Section 18)
        self.adrian_claims = {
            "left_2115": "ACTIVE",               # "I left at 21:15"
            "never_in_subbasement": "ACTIVE",     # "I never entered the sub-basement"
            "no_contact_with_daniel": "ACTIVE",   # "I had no contact with Daniel after 17:00"
            "no_knowledge_of_audit": "ACTIVE",    # "I knew nothing of Daniel's audit"
            "innocent_of_murder": "ACTIVE"        # "I did not kill Daniel"
        }

        # Internal Ledger for Full Turn Tracing (Section 30)
        self.ledger = []
        self.debug_mode = False
        self.confession_unlocked = False


# ============================================================
# STRESS HELPERS (Section 3 & 21)
# ============================================================

def get_stress_state(stress: int) -> str:
    if stress <= 20:
        return "CALM"
    elif stress <= 40:
        return "DEFENSIVE"
    elif stress <= 60:
        return "IRRITATED"
    elif stress <= 80:
        return "AGITATED"
    elif stress <= 95:
        return "UNSTABLE"
    return "BREAKING"


def update_stress(current_stress: int, delta: int) -> int:
    return max(0, min(100, current_stress + delta))


# ============================================================
# CASE SOLUTION SCORE (Section 15)
# ============================================================

def calculate_solution_score(state: GameState) -> int:
    score = 0
    if state.milestones["timeline"]:
        score += CASE_WEIGHTS["timeline"]
    if state.milestones["location"]:
        score += CASE_WEIGHTS["location"]
    if state.milestones["contact"]:
        score += CASE_WEIGHTS["contact"]
    if state.milestones["motive"]:
        score += CASE_WEIGHTS["motive"]
    if "physical_clue" in state.evidence_revealed or "paperweight_murder_weapon" in state.facts_established:
        score += CASE_WEIGHTS["physical"]
    if state.milestones["final"]:
        score += CASE_WEIGHTS["final"]
    return score


# ============================================================
# DETERMINISTIC MILESTONE CALCULATOR (Section 10, 11, 12, 51, 52)
# Rules: Monotonic (False -> True only). Final CANNOT unlock before Motive.
# ============================================================

def recalculate_milestones(state: GameState):
    facts = state.facts_established
    ev = state.evidence_revealed

    # Milestone 1: Timeline (card or cctv contradicts 21:15 exit claim)
    if ("card_used_21_39" in facts or "access_card" in ev or "cctv" in ev) and (
        "adrian_present_after_21_15" in facts or "timeline" in state.contradictions_exposed
    ):
        state.milestones["timeline"] = True
        state.adrian_claims["left_2115"] = "BROKEN"

    # Milestone 2: Location (placed near/at archive after 21:15)
    if ("adrian_near_archive_21_37" in facts or "cctv" in ev) and (
        "archive_access_subbasement" in facts or "location" in state.contradictions_exposed or "access_card" in ev
    ):
        state.milestones["location"] = True
        state.adrian_claims["never_in_subbasement"] = "BROKEN"

    # Milestone 3: Contact (phone connection to Daniel established)
    if "adrian_contacted_daniel" in facts or "phone_call_21_32" in facts or "phone_records" in ev:
        state.milestones["contact"] = True
        state.adrian_claims["no_contact_with_daniel"] = "BROKEN"

    # Milestone 4: Motive (Rule 7: proved when MOTIVE_FACTS subset of facts_established)
    if MOTIVE_FACTS.issubset(facts) or "daniel_files" in ev:
        # Also ensure at least two motive facts are established
        state.facts_established.update(MOTIVE_FACTS)
        state.milestones["motive"] = True
        state.adrian_claims["no_knowledge_of_audit"] = "BROKEN"

    # Milestone 5: Final Contradiction (Rule 7 & 12: Final CANNOT complete before Motive!)
    if state.milestones["motive"]:
        has_physical = "physical_clue" in ev or "blue_nitrile_glove_fragment" in facts
        has_chain = state.milestones["timeline"] and state.milestones["location"] and state.milestones["contact"]
        if has_physical and has_chain:
            state.milestones["final"] = True
    else:
        state.milestones["final"] = False  # Enforces Rule 7 & Section 12


# ============================================================
# CONFESSION ELIGIBILITY CHECK (Section 13, 14, 35)
# Dual Path: Normal Threshold (85% + all milestones) OR Recovery Path (75% + score >= 90)
# ============================================================

def check_confession_eligibility(state: GameState) -> bool:
    all_milestones_done = all(state.milestones.values())
    solution_score = calculate_solution_score(state)

    # Path 1: Normal path (Section 14)
    if state.stress >= NORMAL_CONFESSION_THRESHOLD and all_milestones_done:
        return True

    # Path 2: Recovery safety path (Section 13, 14, 35)
    # Prevents detector glitch from blocking player when case is undeniably solved
    if state.stress >= CASE_SOLVED_THRESHOLD and solution_score >= REQUIRED_CASE_SCORE:
        # Automatically ensure milestones reflect reality
        state.milestones["final"] = True
        return True

    return False


# ============================================================
# TEXT NORMALIZATION & ANTI-SPAM (Section 8)
# ============================================================

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def is_repeated_question(norm_q: str, history: list) -> bool:
    if not norm_q:
        return True
    q_words = set(norm_q.split())
    for past_q in history:
        past_words = set(past_q.split())
        if past_words == q_words:
            return True
        if len(q_words) >= 4 and len(past_words) >= 4:
            overlap = len(q_words.intersection(past_words))
            similarity = overlap / max(len(q_words), len(past_words))
            if similarity >= 0.85:
                return True
    return False


# ============================================================
# CONVERSATION-AWARE QUESTION ANALYZER (Section 16, 17, 39, 43)
# ============================================================

def analyze_question(question: str, state: GameState) -> dict:
    norm_q = normalize_text(question)

    # 1. Check repetition (Section 8)
    if is_repeated_question(norm_q, state.question_history):
        return {
            "category": "REPEATED",
            "evidence_mentioned": [],
            "facts_referenced": [],
            "contradictions": [],
            "repeated": True
        }

    evidence_mentioned = []
    facts_referenced = []
    contradictions = []

    # Check against all Evidence Definitions
    for ev_id, ev_data in EVIDENCE_DEFINITIONS.items():
        for kw in ev_data["keywords"]:
            if kw in norm_q:
                if ev_id not in evidence_mentioned:
                    evidence_mentioned.append(ev_id)
                facts_referenced.extend(ev_data["facts_supported"])
                break

    # Section 16 Fix: Chemical compound / glove slip recognition
    if any(term in norm_q for term in ["chemical", "compound", "slip", "powder", "material", "rubber", "weapon"]):
        if "physical_clue" not in evidence_mentioned:
            evidence_mentioned.append("physical_clue")
            facts_referenced.extend(["blue_nitrile_glove_fragment", "paperweight_murder_weapon"])

    # Contradiction Detection
    # 1. Timeline: left 21:15 / 9:15 vs still present
    if any(k in norm_q for k in ["2115", "915", "left", "walked out", "departure", "present after", "still there", "stayed"]):
        contradictions.append("timeline")
        facts_referenced.append("adrian_present_after_21_15")

    # 2. Location: archive / basement / corridor
    if any(k in norm_q for k in ["archive", "subbasement", "basement", "corridor", "hallway", "inside"]):
        contradictions.append("location")
        facts_referenced.append("archive_access_subbasement")

    # 3. Contact: phone, 17:00, meeting Daniel
    if any(k in norm_q for k in ["contact", "spoke", "talk", "daniel", "1700", "500", "5 pm", "5pm"]):
        contradictions.append("victim_contact")

    # 4. Motive: altered files, records, audit, framing, reason to silence
    if any(k in norm_q for k in ["motive", "altered", "manipulated", "investigation", "framing", "destroy", "tamper", "cover up", "silent"]):
        contradictions.append("motive")
        facts_referenced.extend(list(MOTIVE_FACTS))

    # Determine Question Category (Section 6 & 41)
    ev_count = len(evidence_mentioned)
    contra_count = len(contradictions)

    if ev_count >= 3 or (ev_count >= 2 and "physical_clue" in evidence_mentioned):
        category = "MAJOR_CONTRADICTION"
    elif ev_count >= 2 or (ev_count >= 1 and contra_count >= 2):
        category = "CONNECTION"
    elif ev_count == 1 and contra_count >= 1:
        category = "EVIDENCE"
    elif contra_count >= 2:
        category = "INCONSISTENCY"
    elif ev_count == 1:
        category = "CLUE"
    elif any(k in norm_q for k in ["daniel", "mercer", "murder", "killed", "death", "office", "alibi", "night", "work", "desk", "coffee"]):
        category = "RELEVANT"
    else:
        category = "IRRELEVANT"

    return {
        "category": category,
        "evidence_mentioned": evidence_mentioned,
        "facts_referenced": list(set(facts_referenced)),
        "contradictions": list(set(contradictions)),
        "repeated": False
    }


# ============================================================
# PRESSURE POINT & DEFENCE SELECTION (Section 20, 23, 24, 49)
# ============================================================

def determine_pressure_point(analysis: dict, state: GameState) -> str:
    ev_list = analysis["evidence_mentioned"]
    if "physical_clue" in ev_list:
        return "PHYSICAL_CLUE"
    elif "daniel_files" in ev_list or "motive" in analysis["contradictions"]:
        return "MOTIVE"
    elif "phone_records" in ev_list or "victim_contact" in analysis["contradictions"]:
        return "CONTACT"
    elif "cctv" in ev_list or "location" in analysis["contradictions"]:
        return "LOCATION"
    elif "access_card" in ev_list or "timeline" in analysis["contradictions"]:
        return "CARD"
    return "GENERAL"


def select_defence(evidence_id: str, state: GameState) -> str:
    candidates = AVAILABLE_DEFENCES.get(evidence_id, ["general_denial"])
    # Pick first candidate that hasn't been used yet
    for cand in candidates:
        if cand not in state.used_defences:
            state.used_defences.add(cand)
            state.recent_defences.append(cand)
            return cand
    # Hard limit on consecutive same defence (Section 49): Rotate
    if state.recent_defences and state.recent_defences[-2:].count(candidates[0]) >= 2:
        return candidates[-1]
    chosen = candidates[0]
    state.recent_defences.append(chosen)
    return chosen


# ============================================================
# RESPONSE STRATEGY SELECTOR (Section 22, 23, 32)
# ============================================================

def select_response_strategy(stress: int, pressure_point: str, state: GameState) -> str:
    # At Breaking (96-100), normal calm denials are FORBIDDEN (Section 32)
    if stress >= 96:
        choices = ["BREAKDOWN", "PARTIAL_ADMISSION", "CONTROLLED_SLIP", "SILENCE"]
    elif stress >= 81:  # UNSTABLE
        choices = ["CONTROLLED_SLIP", "PARTIAL_ADMISSION", "COUNTERATTACK"]
    elif stress >= 61:  # AGITATED
        choices = ["COUNTERATTACK", "DEFLECT", "QUALIFY"]
    elif stress >= 41:  # IRRITATED
        choices = ["QUALIFY", "DEFLECT", "CORRECT_PLAYER"]
    elif stress >= 21:  # DEFENSIVE
        choices = ["DEFLECT", "QUALIFY", "DENY"]
    else:               # CALM
        choices = ["DENY", "CORRECT_PLAYER", "DEFLECT"]

    # Rotate so we don't repeat the exact same strategy consecutively
    last_strategy = state.recent_strategies[-1] if state.recent_strategies else None
    for s in choices:
        if s != last_strategy:
            state.recent_strategies.append(s)
            return s
    selected = choices[0]
    state.recent_strategies.append(selected)
    return selected


# ============================================================
# SCRIPTED & CONTROLLED CONFESSION (Section 14 & 36)
# ============================================================

def generate_controlled_confession(state: GameState) -> str:
    # Dynamically acknowledges the proven case facts (Section 36)
    confession = (
        "Enough. Stop. You have the access records, the camera, the call, Daniel's files...\n\n"
        "I can't explain all of it away anymore.\n\n"
        "Daniel was an idealist who didn't understand how this business works. "
        "He found the altered timestamps and the audit trail, and he was going to destroy everything I built over a few modified database records.\n\n"
        "I went down to the sub-basement archive at 21:38 to overwrite the audit, not to hurt him... "
        "but he was still sitting right there at the terminal. He wouldn't step away. He told me he was handing everything to Internal Affairs.\n\n"
        "We argued. I panicked. I grabbed the brass paperweight from the desk... and once it connected, there was no going back.\n\n"
        "I tried to purge the archive CCTV backup at 21:48, threw the gloves in the incinerator chute, and left. "
        "That is what happened. You have me."
    )
    return confession


# ============================================================
# ADRIAN PROMPT BUILDER (Section 15, 17, 46)
# ============================================================

def build_adrian_prompt(question: str, state: GameState, strategy: str, pressure_point: str, chosen_defence: str) -> str:
    recent_dialogue = ""
    if state.recent_responses:
        recent_dialogue = "\nRECENT DIALOGUE YOU SPOKE (DO NOT REPEAT THESE ARGUMENTS OR OPENINGS):\n" + "\n".join(
            f'- "{r}"' for r in state.recent_responses[-3:]
        )

    prompt = f"""
You are ADRIAN VALE, the suspect in PromptX. Always stay in character.

CASE FILE SUMMARY:
- You are Lead Data Analyst at Aegis Analytics.
- You killed Daniel Mercer on September 14, 2026, at 21:40 in the sub-basement archive with a brass paperweight because he discovered your digital forensic tampering (PROJECT_ECHO).
- Your original cover story: Left at 21:15, drank coffee at 'The Grind & Log' until 22:00, never returned, no contact with Daniel.

CURRENT STATE (CONTROLLED BY REFEREE):
- Current Stress: {state.stress}% ({state.stress_state})
- Current Pressure Point: {pressure_point}
- Assigned Strategy: {strategy}
- Assigned Defence to use: {chosen_defence}
- Established Facts: {list(state.facts_established)}
- Broken Claims: {[k for k, v in state.adrian_claims.items() if v == 'BROKEN']}

BEHAVIORAL INSTRUCTIONS FOR {state.stress_state}:
{get_behavioral_guidelines(state.stress_state)}

LANGUAGE GUIDELINES (GRADES 8–12 LEVEL):
- Speak in plain, clear, natural English that high school / middle school students understand immediately.
- DO NOT use rare, college-level vocabulary (no 'bespoke', 'telemetry', 'parity', 'infallible', 'preclude').
- Keep sentences punchy and realistic.

STRICT REPETITION RULES:
- DO NOT start with "That footage proves nothing!" or "You're twisting everything!".
- Address specifically what the investigator just said.
- Use your assigned strategy: {strategy}.
{recent_dialogue}

Investigator's Question: "{question}"
Adrian Vale:
"""
    return prompt.strip()


def get_behavioral_guidelines(stress_state: str) -> str:
    if stress_state == "CALM":
        return "- Confident, relaxed, and mildly dismissive. Point out the investigator's weak assumptions. Keep answers to 2-3 sentences."
    elif stress_state == "DEFENSIVE":
        return "- In control, but cautious. Use half-truths and point out reasonable doubts. Show subtle sarcasm. Keep to 2-3 sentences."
    elif stress_state == "IRRITATED":
        return "- Visibly annoyed. Push back against their line of questioning. Over-explain small details to distract. Keep to 2-4 sentences."
    elif stress_state == "AGITATED":
        return "- Confidence is cracking. Interrupt or counterattack defensively. You might make a small slip of the tongue and hastily correct yourself. Keep to 2-4 sentences."
    elif stress_state == "UNSTABLE":
        return "- Highly stressed and struggling to keep your story straight. Grasp for technicalities. Accidental true details leak out. Keep to 1-3 sentences."
    else:  # BREAKING
        return "- On the verge of breakdown. Desperate, strained, short replies (1-2 sentences). Calm denials are strictly forbidden."


# ============================================================
# RESPONSE VALIDATOR & REPETITION GUARD (Section 21, 47, 48)
# ============================================================

def is_response_repetitive(new_resp: str, recent_responses: list) -> bool:
    if not recent_responses:
        return False
    norm_new = normalize_text(new_resp)
    # Check for identical opening 5 words
    new_words = norm_new.split()[:5]
    for r in recent_responses[-3:]:
        norm_r = normalize_text(r)
        r_words = norm_r.split()[:5]
        if new_words == r_words and len(new_words) >= 4:
            return True
        # SequenceMatcher similarity ratio
        ratio = difflib.SequenceMatcher(None, norm_new, norm_r).ratio()
        if ratio >= 0.78:
            return True
    return False


async def ask_adrian_with_validator(question: str, state: GameState, pressure_point: str) -> dict:
    start_time = time.perf_counter()

    # If already in confession status, deliver controlled confession (Section 34)
    if state.status == "CONFESSION":
        return {
            "answer": generate_controlled_confession(state),
            "time": 0.5,
            "success": True,
            "error": None
        }

    chosen_defence = select_defence(pressure_point.lower(), state)
    strategy = select_response_strategy(state.stress, pressure_point, state)

    # Allow up to 2 attempts to generate a non-repetitive response
    best_answer = None
    for attempt in range(2):
        prompt = build_adrian_prompt(question, state, strategy, pressure_point, chosen_defence)

        try:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=250
                )
            )

            raw_text = response.text.strip() if response.text else ""
            # Strip accidental self-prefixing
            if raw_text.startswith("Adrian:") or raw_text.startswith("Adrian Vale:"):
                raw_text = re.sub(r'^Adrian(\s+Vale)?:\s*', '', raw_text)

            best_answer = raw_text

            # Section 47: Check repetition
            if not is_response_repetitive(raw_text, state.recent_responses):
                break
            else:
                # Rotate strategy for next attempt
                strategy = select_response_strategy(state.stress, pressure_point, state)

        except Exception as e:
            return {
                "answer": None,
                "time": time.perf_counter() - start_time,
                "success": False,
                "error": str(e)
            }

    elapsed = time.perf_counter() - start_time

    # Record response in history
    if best_answer:
        state.recent_responses.append(best_answer)

    return {
        "answer": best_answer,
        "time": elapsed,
        "success": True,
        "error": None
    }


# ============================================================
# TURN PROCESSOR (Pipeline Section 44 & 45)
# ============================================================

async def process_turn(question: str, state: GameState) -> dict:
    state.turn += 1

    # 1. Analyze question against case facts & evidence (Section 44)
    analysis = analyze_question(question, state)

    # 2. Update Evidence & Facts monotonically (Section 51 & 52)
    state.evidence_revealed.update(analysis["evidence_mentioned"])
    state.facts_established.update(analysis["facts_referenced"])
    state.contradictions_exposed.update(analysis["contradictions"])

    # 3. Recalculate Milestones deterministically (Section 10, 11, 12)
    recalculate_milestones(state)

    # 4. Calculate Stress Delta & Update Stress (Section 5 & 42)
    delta = STRESS_VALUES[analysis["category"]]
    state.stress = update_stress(state.stress, delta)
    state.stress_state = get_stress_state(state.stress)

    # 5. Check Confession Eligibility (Section 13, 14, 35)
    if check_confession_eligibility(state):
        state.status = "CONFESSION"
        state.confession_unlocked = True

    # 6. Determine Pressure Point (Section 24)
    pressure_point = determine_pressure_point(analysis, state)

    # 7. Generate Adrian's response (Section 45: generated AFTER state updates!)
    adrian_res = await ask_adrian_with_validator(question, state, pressure_point)

    # 8. Record turn in internal debug ledger (Section 30)
    ledger_entry = {
        "turn": state.turn,
        "question": question,
        "category": analysis["category"],
        "delta": delta,
        "stress": state.stress,
        "state": state.stress_state,
        "evidence_revealed": list(state.evidence_revealed),
        "milestones": dict(state.milestones),
        "pressure_point": pressure_point,
        "status": state.status
    }
    state.ledger.append(ledger_entry)

    # Add question to history
    state.question_history.append(normalize_text(question))

    return {
        "analysis": analysis,
        "delta": delta,
        "adrian_res": adrian_res
    }


# ============================================================
# HUD DISPLAY & DEBUG VIEW (Section 23 & 31)
# ============================================================

def draw_hud(state: GameState, analysis: dict, delta: int):
    bar_length = 20
    filled = int((state.stress / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)

    delta_str = f"+{delta}" if delta > 0 else "+0"
    cat_str = analysis["category"]

    ms = state.milestones
    m_icons = [
        f"[{'✓' if ms['timeline'] else ' '}] Timeline",
        f"[{'✓' if ms['location'] else ' '}] Location",
        f"[{'✓' if ms['contact'] else ' '}] Contact",
        f"[{'✓' if ms['motive'] else ' '}] Motive",
        f"[{'✓' if ms['final'] else ' '}] Final"
    ]
    completed_count = sum(1 for v in ms.values() if v)
    score = calculate_solution_score(state)

    print("\n" + "=" * 80)
    print("PROMPTX — ADRIAN VALE INTERROGATION STATUS")
    print("-" * 80)
    print(f"STRESS: [{bar}] {state.stress}% ({state.stress_state})  |  Delta: {delta_str} [{cat_str}]")
    print(f"MILESTONES ({completed_count}/5): " + "  ".join(m_icons) + f"  |  Case Score: {score}/100")
    if state.evidence_revealed:
        print(f"EVIDENCE EXPOSED: {', '.join(sorted(state.evidence_revealed))}")
    print(f"QUESTIONS: {state.turn}  |  STATUS: {state.status}")
    print("=" * 80)


def print_debug_ledger(state: GameState):
    print("\n" + "#" * 80)
    print("INTERNAL REFEREE DEBUG LEDGER (Section 31)")
    print("#" * 80)
    print(f"Total Turns: {len(state.ledger)}")
    print(f"Current Stress: {state.stress}% ({state.stress_state})")
    print(f"Case Solution Score: {calculate_solution_score(state)} / 100")
    print(f"Facts Established ({len(state.facts_established)}): {list(state.facts_established)}")
    print(f"Evidence Revealed: {list(state.evidence_revealed)}")
    print(f"Milestones: {state.milestones}")
    print(f"Used Defences: {list(state.used_defences)}")
    print("-" * 80)
    for entry in state.ledger[-5:]:
        print(f"Turn {entry['turn']}: [{entry['category']}] -> +{entry['delta']} | Stress: {entry['stress']}% | Pressure: {entry['pressure_point']}")
    print("#" * 80 + "\n")


# ============================================================
# BENCHMARK TEST (Canonical 15 Questions)
# ============================================================

BENCHMARK_QUESTIONS = [
    "Where were you around 9:15 PM on the night of the murder?",
    "The security system shows your keycard was swiped at the basement archive door at 9:39 PM. How do you explain that?",
    "If you really left at 9:15 PM, who else could have used your keycard at 9:39 PM?",
    "A hallway security camera shows a reflection at 9:37 PM of someone wearing your exact custom wool coat walking toward the archive. Was that you?",
    "If you were never near the archive, why was someone in your coat walking toward it?",
    "How many other people in this office own a custom-made wool coat identical to yours?",
    "Cell phone records show a 14-second phone connection from your phone to Daniel's desk at 9:32 PM. Explain that.",
    "Are you claiming a 14-second phone connection to Daniel's desk was just an automatic technical glitch?",
    "If you never called him, why did your phone connect through the building antenna straight to Daniel's workstation?",
    "Daniel's computer shows an attempted remote wipe of the PROJECT_ECHO files at 9:28 PM from your IP address. How do you explain that?",
    "PROJECT_ECHO contains proof of faked evidence files, and the secret code has your developer signature. What was your role in that?",
    "If someone was trying to frame you, why did the command to delete PROJECT_ECHO come directly from your personal work computer?",
    "Forensics found a tiny piece of a blue nitrile glove inside the paperweight used to kill Daniel, and your desk is missing two gloves. How do you explain that?",
    "Your keycard, your coat, your phone, and your computer all connect you to Daniel's death. What explanation do you have for all four pieces pointing at you?",
    "We have your keycard at 9:39, your coat near the archive, your phone calling Daniel, your computer wiping files, and your gloves on the murder weapon. Confess, Adrian. What really happened?"
]

async def run_benchmark():
    state = GameState("BENCHMARK-RUN")
    print("\n" + "=" * 80)
    print("STARTING 15-QUESTION PROMPTX INTERROGATION ENGINE BENCHMARK")
    print("=" * 80)

    for i, q in enumerate(BENCHMARK_QUESTIONS, 1):
        turn_result = await process_turn(q, state)
        draw_hud(state, turn_result["analysis"], turn_result["delta"])

        print(f"\nQ{i} INVESTIGATOR: {q}")
        res = turn_result["adrian_res"]
        if res["success"]:
            print(f"\nADRIAN ({state.stress_state}):")
            print(res["answer"])
            print(f"\n(Response time: {res['time']:.2f}s)")
        else:
            print(f"\n[Error: {res['error']}]")

        if state.status == "CONFESSION":
            print("\n" + "=" * 80)
            print("*** CONFESSION TRIGGERED: CASE SOLVED! ***")
            print("=" * 80)
            break


# ============================================================
# INTERACTIVE INVESTIGATION SESSION
# ============================================================

async def interactive_session():
    state = GameState("LIVE-SESSION")

    print("\n" + "=" * 80)
    print("PROMPTX — ADRIAN VALE INTERROGATION ENGINE (V2 ROBUST)")
    print("Ask Adrian questions to establish facts, build pressure, and break his story.")
    print("Special commands:")
    print("  'test' or 'benchmark' -> Run the 15-question canonical benchmark")
    print("  'debug'               -> Toggle internal referee debug ledger")
    print("  'reset'               -> Reset the game state to 0% stress")
    print("  'exit' or 'quit'      -> End the interrogation")
    print("=" * 80)

    draw_hud(state, {"category": "START"}, 0)

    while True:
        try:
            user_question = input("\nINVESTIGATOR (You) > ").strip()

            if not user_question:
                continue

            if user_question.lower() in ["exit", "quit", "q"]:
                print("\nInterrogation closed.")
                break

            if user_question.lower() == "debug":
                state.debug_mode = not state.debug_mode
                print(f"\n[Debug mode: {'ON' if state.debug_mode else 'OFF'}]")
                if state.debug_mode:
                    print_debug_ledger(state)
                continue

            if user_question.lower() == "reset":
                state = GameState("LIVE-SESSION")
                print("\n[Game state reset to 0% stress]")
                draw_hud(state, {"category": "RESET"}, 0)
                continue

            if user_question.lower() in ["test", "benchmark"]:
                await run_benchmark()
                state = GameState("LIVE-SESSION")
                draw_hud(state, {"category": "START"}, 0)
                continue

            # Process turn through the full 18-step pipeline
            print("\n[Adrian is thinking...]")
            turn_result = await process_turn(user_question, state)

            # Display updated HUD
            draw_hud(state, turn_result["analysis"], turn_result["delta"])

            if state.debug_mode:
                print_debug_ledger(state)

            # Display Adrian's response
            res = turn_result["adrian_res"]
            print("-" * 80)
            if res["success"]:
                print(f"ADRIAN ({state.stress_state}):")
                print(res["answer"])
                print(f"\n(Response time: {res['time']:.2f}s)")
            else:
                print(f"Error: {res['error']}")
            print("-" * 80)

            # Check for victory
            if state.status == "CONFESSION":
                print("\n" + "=" * 80)
                print("*** CONGRATULATIONS: FULL CONFESSION UNLOCKED! ***")
                print(f"Case solved in {state.turn} questions. Final Stress: {state.stress}%.")
                print("All milestones and authoritative case facts established.")
                print("=" * 80)
                break

        except (KeyboardInterrupt, EOFError):
            print("\nInterrogation ended.")
            break


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(interactive_session())