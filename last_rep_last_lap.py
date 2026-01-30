import curses
import random
from dataclasses import dataclass, field
from typing import Dict, List, Callable


# ==========================
# LAST REP, LAST LAP (ASCII GAME)
# ==========================

@dataclass
class Stats:
    week: int = 1
    stamina: int = 70        # 0-100
    injury: int = 10         # 0-100
    confidence: int = 55     # 0-100
    reputation: int = 5      # 0-100
    cash: int = 120

    mentor_trust: int = 0
    agent_interest: int = 0
    tape_study: int = 0
    sleep_debt: int = 0
    injury_flag: bool = False
    signed_bad_deal: bool = False
    signed_good_deal: bool = False
    scandal_flag: bool = False


@dataclass
class Choice:
    key: str
    label: str
    apply_fn: Callable[["GameState"], None]


@dataclass
class Scene:
    scene_id: str
    title: str
    art: str
    text_lines: List[str]
    choices: List[Choice]
    on_enter: Callable[["GameState"], None] = lambda gs: None


@dataclass
class GameState:
    stats: Stats = field(default_factory=Stats)
    rng: random.Random = field(default_factory=lambda: random.Random())
    current_scene_id: str = "intro"
    message_log: List[str] = field(default_factory=list)
    ended: bool = False
    ending_title: str = ""
    ending_lines: List[str] = field(default_factory=list)
    flags: Dict[str, bool] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)  # currently unused, but future-proof

    def log(self, msg: str) -> None:
        self.message_log.append(msg)
        if len(self.message_log) > 6:
            self.message_log = self.message_log[-6:]


# --------------------------
# Utility
# --------------------------

def clamp(n: int, low: int, high: int) -> int:
    return max(low, min(high, n))


def apply_delta(gs: GameState, **kwargs: int) -> None:
    s = gs.stats
    for k, v in kwargs.items():
        if hasattr(s, k):
            setattr(s, k, getattr(s, k) + v)

    s.stamina = clamp(s.stamina, 0, 100)
    s.injury = clamp(s.injury, 0, 100)
    s.confidence = clamp(s.confidence, 0, 100)
    s.reputation = clamp(s.reputation, 0, 100)


def end_game(gs: GameState, title: str, lines: List[str]) -> None:
    gs.ended = True
    gs.ending_title = title
    gs.ending_lines = lines


def fatigue_tick(gs: GameState) -> None:
    s = gs.stats

    if s.stamina < 35:
        s.sleep_debt += 1
    else:
        s.sleep_debt = max(0, s.sleep_debt - 1)

    flare_chance = 0.02 + (s.injury / 200.0) + (s.sleep_debt * 0.03)
    if (not s.injury_flag) and gs.rng.random() < flare_chance and s.injury >= 35:
        s.injury_flag = True
        gs.log("A sharp ache returns. You feel a limit approaching.")

    if s.confidence > 52:
        s.confidence -= 1
    elif s.confidence < 48:
        s.confidence += 1

    s.cash -= 15

    if s.cash < 0:
        apply_delta(gs, confidence=-2, injury=+2)
        gs.log("Bills press in. Stress tightens your body.")


def advance_week(gs: GameState) -> None:
    gs.stats.week += 1
    fatigue_tick(gs)


def check_for_endings(gs: GameState) -> None:
    s = gs.stats

    if s.injury >= 90:
        end_game(gs, "ENDING: CAREER HALTED",
                 [
                     "The pain stops being a warning and becomes a wall.",
                     "A doctor uses words you try not to hear: 'months', 'maybe never'.",
                     "",
                     "It isn't a moral failing. It's a body telling the truth."
                 ])
        return

    if s.confidence <= 10 and s.reputation < 20:
        end_game(gs, "ENDING: QUIET EXIT",
                 [
                     "You keep showing up, but something in you stops believing.",
                     "Eventually, you stop calling it a break and call it done.",
                     "",
                     "You still run sometimes, alone, for the sound of it."
                 ])
        return

    if s.scandal_flag:
        end_game(gs, "ENDING: HEADLINE SEASON",
                 [
                     "The story grows bigger than your effort.",
                     "Sponsors vanish. Invitations dry up.",
                     "",
                     "The hardest part is knowing you helped write it."
                 ])
        return


# --------------------------
# ASCII Art
# --------------------------

ART_GYM = r"""
     _______________________________
    /                               \
   |   ________      ________        |
   |  |  ____  |    |  ____  |       |
   |  | |####| |    | |####| |       |
   |  | |####| |    | |####| |       |
   |  | |____| |    | |____| |       |
   |  |________|    |________|       |
   |                                   |
   |   [RACK]        (MIRROR)          |
   |    ||||           ______          |
   |    ||||          |      |         |
   |    ||||          |      |         |
   |                                   |
   |___________  _________  ___________|
"""

ART_TRACK = r"""
      ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
   __/_________________________\__
  /  /  /  /  /  /  /  /  /  /  /
 /__/__/__/__/__/__/__/__/__/__/
     o           o           o
    /|\         /|\         /|\
    / \         / \         / \
"""

ART_LOCKER = r"""
  _____________________________
 |  ____   ____   ____   ____  |
 | |    | |    | |    | |    | |
 | |____| |____| |____| |____| |
 |  __        BENCH        __   |
 | |  |___________________|  |  |
 | |__|                   |__|  |
 |______________________________|
"""

ART_DINER = r"""
  _______________________________
 |  ( )   ( )   ( )   ( )   ( ) |
 |   |     |     |     |     |  |
 |  _|_   _|_   _|_   _|_   _|_ |
 |  MENU: soup / eggs / coffee   |
 |   _________________________   |
 |  |   booth    booth    booth | |
 |  |_________________________| |
 |_______________________________|
"""

ART_CLINIC = r"""
  _______________________________
 |   CLINIC: PHYSIO & RECOVERY   |
 |  ___________________________  |
 | |  TABLE          ICE PACK   | |
 | |   ____            ____     | |
 | |  |____|          |____|    | |
 | |___________________________| |
 |   "Listen to your body."      |
 |_______________________________|
"""

ART_STAGE = r"""
           _________
      ____/  LIVE   \____
     /   /  SHOWCASE  \   \
    /___/______________\___\
       |   _      _   |
       |  (_)    (_)  |
       |     \__/      |
       |  CROWD ROARS  |
       |_______________|
"""


# --------------------------
# Scenes + Choices
# --------------------------

def make_scenes() -> Dict[str, Scene]:
    scenes: Dict[str, Scene] = {}

    def route_week(gs: GameState) -> None:
        check_for_endings(gs)
        if gs.ended:
            return

        s = gs.stats
        if s.week == 3:
            gs.current_scene_id = "mentor"
            return
        if s.week == 5:
            gs.current_scene_id = "agent"
            return
        if s.week == 8 and (s.injury_flag or s.injury >= 45):
            gs.current_scene_id = "clinic"
            return
        if s.week >= 10:
            gs.current_scene_id = "showcase"
            return

        if s.stamina < 30 or s.injury >= 55:
            gs.current_scene_id = "locker"
        else:
            gs.current_scene_id = "gym" if gs.rng.random() < 0.55 else "track"

    # Choice effects
    def train_hard(gs: GameState) -> None:
        apply_delta(gs, stamina=-18, injury=+10, confidence=+6, reputation=+2)
        gs.stats.agent_interest += 1
        gs.log("You push past the comfortable line. It shows.")
        advance_week(gs)
        route_week(gs)

    def train_smart(gs: GameState) -> None:
        apply_delta(gs, stamina=-12, injury=+5, confidence=+4, reputation=+1)
        gs.stats.mentor_trust += 1
        gs.log("Clean work. The kind that lasts.")
        advance_week(gs)
        route_week(gs)

    def recovery_day(gs: GameState) -> None:
        apply_delta(gs, stamina=+16, injury=-10, confidence=+1)
        gs.stats.sleep_debt = max(0, gs.stats.sleep_debt - 2)
        gs.log("You recover on purpose. It feels like strategy.")
        advance_week(gs)
        route_week(gs)

    def take_extra_shift(gs: GameState) -> None:
        apply_delta(gs, stamina=-8, injury=+2, confidence=-1)
        gs.stats.cash += 80
        gs.log("You work late. The money helps. The body notices.")
        advance_week(gs)
        route_week(gs)

    def study_tape(gs: GameState) -> None:
        apply_delta(gs, confidence=+3, reputation=+1)
        gs.stats.tape_study += 2
        gs.log("You watch yourself like a scientist watches weather.")
        advance_week(gs)
        route_week(gs)

    def risky_supplement(gs: GameState) -> None:
        apply_delta(gs, stamina=-10, injury=+8, confidence=+10, reputation=+4)
        if gs.rng.random() < 0.22:
            gs.stats.scandal_flag = True
        else:
            gs.log("It hits fast. Too fast. You tell yourself it's fine.")
        advance_week(gs)
        route_week(gs)

    def visit_physio(gs: GameState) -> None:
        apply_delta(gs, stamina=+8, injury=-18, confidence=+2)
        gs.stats.cash -= 40
        gs.stats.injury_flag = False
        gs.log("Hands, heat, ice. A map back to functional.")
        advance_week(gs)
        route_week(gs)

    def meet_mentor(gs: GameState) -> None:
        apply_delta(gs, confidence=+2)
        gs.stats.mentor_trust += 2
        gs.log("Your coach says one sentence that rearranges your week.")
        advance_week(gs)
        route_week(gs)

    def meet_agent(gs: GameState) -> None:
        s = gs.stats
        gs.flags["agent_offer_good"] = (s.reputation >= 35 and s.agent_interest >= 2)
        gs.log("An agent studies you like a market that might become a home.")
        advance_week(gs)
        route_week(gs)

    def sign_deal(gs: GameState) -> None:
        s = gs.stats
        if gs.flags.get("agent_offer_good", False):
            s.signed_good_deal = True
            s.cash += 220
            apply_delta(gs, confidence=+4, reputation=+6)
            gs.log("The contract is fair. You feel seen, not used.")
        else:
            s.signed_bad_deal = True
            s.cash += 160
            apply_delta(gs, confidence=+2, reputation=+3, injury=+6)
            gs.log("Fast money, hidden pressure.")
        advance_week(gs)
        route_week(gs)

    def decline_deal(gs: GameState) -> None:
        apply_delta(gs, confidence=+1, reputation=+1)
        gs.stats.mentor_trust += 1
        gs.log("You walk away from noise, not from the dream.")
        advance_week(gs)
        route_week(gs)

    def resolve_showcase(gs: GameState) -> None:
        s = gs.stats
        performance = 0
        performance += int(s.stamina / 10)
        performance += int(s.confidence / 10)
        performance += int(s.reputation / 10)
        performance += int(s.tape_study / 3)
        performance -= int(s.injury / 12)
        performance -= s.sleep_debt
        performance += gs.rng.randint(-2, 2)

        if s.scandal_flag:
            check_for_endings(gs)
            return

        if performance >= 18 and s.injury < 70:
            end_game(gs, "ENDING: THE BIG LEAP",
                     [
                         "The arena feels small once you start moving.",
                         "Clean. Controlled. Alive.",
                         "",
                         "You sign a real deal, on your terms.",
                         "You made it big, and you kept yourself intact."
                     ])
            return

        if performance >= 14 and s.injury < 80:
            end_game(gs, "ENDING: WORKING PRO",
                     [
                         "You place well. Not mythical, but real.",
                         "A team offers a developmental contract.",
                         "",
                         "It's not fame. It's a life built from practice."
                     ])
            return

        if performance >= 10:
            if s.mentor_trust >= 3:
                end_game(gs, "ENDING: THE MENTOR'S LINEAGE",
                         [
                             "You don't win the night, but you win someone's attention.",
                             "A younger athlete asks how you keep showing up.",
                             "",
                             "You realize you can teach what you survived."
                         ])
            else:
                end_game(gs, "ENDING: CULT FAVORITE",
                         [
                             "You don't take the top spot, but you take the crowd.",
                             "People remember your effort more than the podium.",
                             "",
                             "You keep competing. You keep becoming."
                         ])
            return

        if s.injury >= 75:
            end_game(gs, "ENDING: TOO MUCH TOO SOON",
                     [
                         "You try to force a body into a story it can't hold.",
                         "The moment cracks.",
                         "",
                         "You survive the night, but not without cost."
                     ])
            return

        end_game(gs, "ENDING: RESET SEASON",
                 [
                     "The performance is fine, but not enough to open doors.",
                     "You leave with strange relief.",
                     "",
                     "This ending is a beginning if you let it be."
                 ])

    # Scenes
    scenes["intro"] = Scene(
        "intro", "The First Week", ART_LOCKER,
        [
            "Your bag is older than your ambitions.",
            "The locker room smells like tape, soap, and the future.",
            "",
            "Somewhere out there is a version of you who made it.",
            "Right now, you only have today."
        ],
        [
            Choice("1", "Go train in the gym (strength day).", lambda gs: setattr(gs, "current_scene_id", "gym")),
            Choice("2", "Go to the track (speed day).", lambda gs: setattr(gs, "current_scene_id", "track")),
            Choice("3", "Grab a meal and plan the week (diner).", lambda gs: setattr(gs, "current_scene_id", "diner")),
            Choice("4", "Sleep. Seriously. (recovery)", lambda gs: setattr(gs, "current_scene_id", "rest_scene")),
        ]
    )

    scenes["gym"] = Scene(
        "gym", "The Gym", ART_GYM,
        [
            "Iron and repetition. The mirror does not congratulate you.",
            "A rival laughs too loudly at someone else's lift.",
            "",
            "You can chase numbers or chase form."
        ],
        [
            Choice("1", "Train hard: max effort sets.", train_hard),
            Choice("2", "Train smart: form + volume.", train_smart),
            Choice("3", "Study tape instead: notes and footage.", study_tape),
            Choice("4", "Pick up an extra shift tonight for cash.", take_extra_shift),
        ]
    )

    scenes["track"] = Scene(
        "track", "The Track", ART_TRACK,
        [
            "Cold air bites your lungs, clean and honest.",
            "The lanes go forward without caring who you are.",
            "",
            "Your legs feel fast. Your joints feel… watched."
        ],
        [
            Choice("1", "Intervals until you're empty.", train_hard),
            Choice("2", "Tempo work with clean pacing.", train_smart),
            Choice("3", "Recovery jog + mobility.", recovery_day),
            Choice("4", "Risky shortcut: 'performance stack'.", risky_supplement),
        ]
    )

    scenes["diner"] = Scene(
        "diner", "The Diner", ART_DINER,
        [
            "Coffee. Salt. A corner booth that doesn't ask questions.",
            "",
            "The menu is simple. Your life isn't."
        ],
        [
            Choice("1", "Eat well and plan: write a weekly routine.", train_smart),
            Choice("2", "Call your mentor for perspective.", meet_mentor),
            Choice("3", "Take a shift: money now, fatigue later.", take_extra_shift),
            Choice("4", "Rest here: breathe, hydrate, reset.", recovery_day),
        ]
    )

    scenes["rest_scene"] = Scene(
        "rest_scene", "Recovery", ART_LOCKER,
        [
            "You choose sleep like it's training.",
            "Your phone buzzes, then stops.",
            "",
            "You wake up with a quieter mind."
        ],
        [
            Choice("1", "Return to the gym.", lambda gs: setattr(gs, "current_scene_id", "gym")),
            Choice("2", "Return to the track.", lambda gs: setattr(gs, "current_scene_id", "track")),
            Choice("3", "Get food and plan (diner).", lambda gs: setattr(gs, "current_scene_id", "diner")),
            Choice("4", "Take it as a full recovery week.", recovery_day),
        ]
    )

    scenes["mentor"] = Scene(
        "mentor", "Coach's Office", ART_LOCKER,
        [
            "Your mentor watches you walk in before they say a word.",
            "",
            "“Talent is loud,” they say. “Consistency is quiet.”",
            "“Pick what you want to be known for.”"
        ],
        [
            Choice("1", "Commit to clean training: no shortcuts.", meet_mentor),
            Choice("2", "Ask for a structured plan and follow it.", train_smart),
            Choice("3", "Admit you're broke and ask for work leads.", take_extra_shift),
            Choice("4", "Say you're fine and leave fast.", train_hard),
        ]
    )

    scenes["agent"] = Scene(
        "agent", "The Agent", ART_DINER,
        [
            "An agent sits like they belong in your future.",
            "They talk about 'trajectory' and 'brand' and 'timelines'.",
            "",
            "They want you to sign something."
        ],
        [
            Choice("1", "Hear them out. (meet agent)", meet_agent),
            Choice("2", "Sign whatever is offered. (fast path)", sign_deal),
            Choice("3", "Decline. Focus on performance first.", decline_deal),
            Choice("4", "Walk away and train instead.", train_hard),
        ]
    )

    scenes["clinic"] = Scene(
        "clinic", "Physio Clinic", ART_CLINIC,
        [
            "The physio points to a diagram of a knee that looks like yours.",
            "",
            "“Pain is information,” they say.",
            "“Listen before it starts shouting.”"
        ],
        [
            Choice("1", "Do rehab properly (costs cash, saves body).", visit_physio),
            Choice("2", "Ignore it and train anyway.", train_hard),
            Choice("3", "Take a week off: rest + mobility.", recovery_day),
            Choice("4", "Work instead. Money first.", take_extra_shift),
        ]
    )

    scenes["locker"] = Scene(
        "locker", "Locker Room", ART_LOCKER,
        [
            "You sit on the bench and feel your week in your joints.",
            "",
            "You can keep forcing it, or you can get smart."
        ],
        [
            Choice("1", "Recovery-focused week.", recovery_day),
            Choice("2", "Train smart anyway.", train_smart),
            Choice("3", "Take a shift for rent money.", take_extra_shift),
            Choice("4", "Go to the clinic (physio).", visit_physio),
        ]
    )

    scenes["showcase"] = Scene(
        "showcase", "The Showcase", ART_STAGE,
        [
            "Bright lights. Quiet stomach.",
            "A crowd waits to believe in somebody.",
            "",
            "You are somebody. The question is which kind."
        ],
        [
            Choice("1", "Compete. (commit to your season)", resolve_showcase),
            Choice("2", "Withdraw to protect your body.", lambda gs: end_game(gs, "ENDING: WALK AWAY HEALTHY", [
                "You withdraw before the moment becomes damage.",
                "You choose a future with knees that still work.",
                "",
                "Some people call it fear.",
                "You call it wisdom."
            ])),
            Choice("3", "Chase headlines: risky shortcut now.", lambda gs: (setattr(gs.stats, "scandal_flag", gs.rng.random() < 0.65), resolve_showcase(gs))),
            Choice("4", "Breathe, then compete.", lambda gs: (apply_delta(gs, confidence=+3, stamina=+2), resolve_showcase(gs))),
        ]
    )

    return scenes


# --------------------------
# Safe curses rendering
# --------------------------

def safe_addstr(stdscr, y: int, x: int, s: str) -> None:
    """Avoid curses crashes if the terminal is too small."""
    try:
        h, w = stdscr.getmaxyx()
        if y < 0 or y >= h:
            return
        if x < 0 or x >= w:
            return
        if w <= 1:
            return
        stdscr.addstr(y, x, s[: max(0, w - x - 1)])
    except curses.error:
        # swallow rendering errors caused by tiny terminals / resizing mid-frame
        return


def render_screen(stdscr, gs: GameState, scene: Scene) -> None:
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # If terminal is very small, show a friendly message instead of crashing.
    if h < 22 or w < 55:
        safe_addstr(stdscr, 0, 0, "Terminal window too small. Resize larger to play.")
        safe_addstr(stdscr, 2, 0, "Try making it wider and taller, then press any key.")
        safe_addstr(stdscr, h - 1, 0, "q=quit".ljust(max(0, w - 1)))
        stdscr.refresh()
        return

    title_line = f" LAST REP, LAST LAP  |  {scene.title}  "
    safe_addstr(stdscr, 0, 0, title_line)

    s = gs.stats
    hud = (
        f"Week {s.week:02d}  "
        f"STA {s.stamina:3d}  "
        f"INJ {s.injury:3d}  "
        f"CON {s.confidence:3d}  "
        f"REP {s.reputation:3d}  "
        f"$ {s.cash:4d}"
    )
    safe_addstr(stdscr, 1, 0, hud)
    safe_addstr(stdscr, 2, 0, "-" * (w - 1))

    # Art
    art_lines = scene.art.strip("\n").splitlines()
    y = 3
    for line in art_lines:
        if y >= h - 10:
            break
        safe_addstr(stdscr, y, 0, line)
        y += 1

    y += 1
    for line in scene.text_lines:
        if y >= h - 6:
            break
        safe_addstr(stdscr, y, 0, line)
        y += 1

    y += 1
    for ch in scene.choices:
        if y >= h - 2:
            break
        safe_addstr(stdscr, y, 0, f"[{ch.key}] {ch.label}")
        y += 1

    # Log footer
    log_y = h - 5
    safe_addstr(stdscr, log_y, 0, "-" * (w - 1))
    safe_addstr(stdscr, log_y + 1, 0, "Recent:")
    ly = log_y + 2
    for msg in gs.message_log[-3:]:
        if ly >= h - 1:
            break
        safe_addstr(stdscr, ly, 0, f"• {msg}")
        ly += 1

    safe_addstr(stdscr, h - 1, 0, "Keys: 1-4 choose | i=inventory | l=look | q=quit".ljust(w - 1))
    stdscr.refresh()


def render_ending(stdscr, gs: GameState) -> None:
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    lines = [gs.ending_title, ""] + gs.ending_lines + ["", "Press q to quit. Press r to restart."]
    y = 2
    for line in lines:
        if y >= h - 2:
            break
        safe_addstr(stdscr, y, 2, line)
        y += 1
    stdscr.refresh()


def run_game(stdscr) -> None:
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    scenes = make_scenes()
    gs = GameState()

    while True:
        if gs.ended:
            render_ending(stdscr, gs)
            key = stdscr.getch()
            if key in (ord('q'), ord('Q')):
                return
            if key in (ord('r'), ord('R')):
                scenes = make_scenes()
                gs = GameState()
            continue

        scene = scenes[gs.current_scene_id]
        render_screen(stdscr, gs, scene)

        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            return
        if key in (ord('l'), ord('L')):
            gs.log("You take it in again. The details sharpen.")
            continue
        if key in (ord('i'), ord('I')):
            inv = ", ".join(gs.inventory) if gs.inventory else "(nothing)"
            gs.log(f"Inventory: {inv}")
            continue

        chosen = None
        for ch in scene.choices:
            if key == ord(ch.key):
                chosen = ch
                break
        if chosen is None:
            continue

        chosen.apply_fn(gs)


def main() -> None:
    curses.wrapper(run_game)


if __name__ == "__main__":
    main()
