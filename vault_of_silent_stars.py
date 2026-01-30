import sys

# ==========================================
# THE VAULT OF SILENT STARS (v1.1)
# Multi-ending mythic science-fantasy
# ==========================================

class Room:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.exits = {}        # direction -> Room
        self.locked_exits = {} # direction -> Room (sealed)
        self.items = []
        self.npcs = []

    def describe(self):
        print(f"\n{self.name.upper()}")
        print("-" * len(self.name))
        print(self.desc)

        if self.items:
            print("\nYou see:")
            for i in self.items:
                print(" -", i)

        if self.npcs:
            print("\nPresent:")
            for n in self.npcs:
                print(" -", n)

        if self.exits or self.locked_exits:
            print("\nPaths:")
            for e in self.exits:
                print(" -", e)
            for e in self.locked_exits:
                print(" -", f"{e} (sealed)")


class Game:
    def __init__(self):
        self.rooms = {}
        self.current = None
        self.inventory = []
        self.flags = {
            "bridge": False,
            "engine": False,
            "mirror": False,
            "oracle_spoken": False,
            "core_open": False,  # Drift Gate unlocked from Sanctum
        }
        self.build_world()

    # -----------------------------
    # WORLD BUILD
    # -----------------------------

    def build_world(self):
        R = lambda n, d: Room(n, d)

        plaza = R(
            "Glass Plaza",
            "A circular court of translucent stone beneath a fractured sky. "
            "Star-light trickles upward from cracks in the floor."
        )

        archive = R(
            "Star Archive",
            "Floating tablets orbit cracked pedestals. Whispering constellations drift through dust."
        )

        observatory = R(
            "Sky Observatory",
            "Open domes track broken constellations with skeletal instruments."
        )

        garden = R(
            "Gravity Garden",
            "Trees curl sideways, roots drifting in slow arcs. Wind hums without direction."
        )

        bridge = R(
            "Broken Skybridge",
            "A vast gulf splits the structure. Lightless void yawns beneath."
        )

        maw = R(
            "Fracture Maw",
            "Reality tears downward into a spiral of light. The air tastes like cold metal and endings."
        )

        engine = R(
            "Astral Engine",
            "Titanic rings surround a dormant stellar core. Silent, but waiting."
        )

        sanctum = R(
            "Inner Sanctum",
            "Glyphs orbit a spherical aperture humming with pressure."
        )

        core = R(
            "Star Core",
            "A miniature sun writhes inside geometric restraints."
        )

        escape = R(
            "Drift Gate",
            "A crescent portal opens onto impossible distance."
        )

        halls = R(
            "Echoing Halls",
            "Corridors curve in impossible ways, footsteps returning from other centuries."
        )

        vault = R(
            "Reliquary Vault",
            "Stone caskets float weightlessly, engraved with extinct languages."
        )

        mirror = R(
            "Mirror Gallery",
            "Tall obsidian panes reflect skies that do not exist."
        )

        oracle = R(
            "Oracle Chamber",
            "A seated figure of crystal hums faintly, eyes closed."
        )

        # ---- Exits (unsealed) ----

        plaza.exits = {"north": archive, "east": garden, "west": halls, "south": sanctum}

        archive.exits = {"south": plaza, "north": observatory}
        observatory.exits = {"south": archive}

        garden.exits = {"west": plaza, "north": bridge}
        bridge.exits = {"south": garden}  # north sealed until repaired

        halls.exits = {"east": plaza, "north": vault}
        vault.exits = {"south": halls, "north": mirror}
        mirror.exits = {"south": vault, "east": oracle}
        oracle.exits = {"west": mirror}

        sanctum.exits = {"south": engine}  # east sealed until aligned
        engine.exits = {"north": sanctum}  # north sealed until awakened

        core.exits = {"south": engine}
        escape.exits = {"west": sanctum}

        # IMPORTANT: maw is now reversible (debug fix)
        maw.exits = {"south": bridge, "north": sanctum}

        # ---- Locks ----
        bridge.locked_exits["north"] = maw        # repaired via gravity seed
        engine.locked_exits["north"] = core       # awakened via resonant rod
        sanctum.locked_exits["east"] = escape     # aligned via alignment chart

        # ---- Items ----
        archive.items.append("star shard")
        garden.items.append("gravity seed")
        vault.items.append("void lens")
        observatory.items.append("alignment chart")
        halls.items.append("resonant rod")

        # ---- NPCs ----
        oracle.npcs.append("oracle")

        # ---- Register ----
        for r in [
            plaza, archive, observatory, garden, bridge, maw,
            engine, sanctum, core, escape, halls, vault, mirror, oracle
        ]:
            self.rooms[r.name] = r

        self.current = plaza

    # -----------------------------
    # CORE LOOP
    # -----------------------------

    def play(self):
        print("\n🌌 THE VAULT OF SILENT STARS 🌌\n")
        print("You awaken in a structure older than calendars.\n")
        self.current.describe()

        while True:
            self.handle(input("\n> ").strip().lower())

    # -----------------------------
    # COMMAND HANDLER
    # -----------------------------

    def handle(self, cmd):
        if not cmd:
            return

        words = cmd.split()
        verb = words[0]

        if verb in ("quit", "exit"):
            sys.exit()

        if verb == "look":
            self.current.describe()
            return

        if verb == "inventory":
            self.show_inventory()
            return

        if verb == "help":
            self.help()
            return

        if verb == "go":
            self.move(words[1] if len(words) > 1 else "")
            return

        if verb == "take":
            self.take(" ".join(words[1:]))
            return

        if verb == "use":
            self.use(" ".join(words[1:]))
            return

        if verb == "talk":
            self.talk(" ".join(words[1:]))
            return

        print("The structure does not respond.")

    # -----------------------------
    # UI
    # -----------------------------

    def help(self):
        print("""
Commands:
 go <direction>
 look
 take <item>
 use <item>
 talk <npc>
 inventory
 help
 quit
""")

    def show_inventory(self):
        if not self.inventory:
            print("You carry nothing.")
        else:
            print("You carry:")
            for i in self.inventory:
                print(" -", i)

    # -----------------------------
    # MOVEMENT
    # -----------------------------

    def move(self, d):
        if d in self.current.locked_exits:
            print("A stellar seal blocks that path.")
            return

        if d in self.current.exits:
            self.current = self.current.exits[d]
            self.current.describe()
            return

        print("You cannot move that way.")

    # -----------------------------
    # INTERACTION
    # -----------------------------

    def take(self, item):
        if item in self.current.items:
            self.current.items.remove(item)
            self.inventory.append(item)
            print("Taken.")
        else:
            print("That is not here.")

    def talk(self, npc):
        if npc == "oracle" and self.current.name == "Oracle Chamber":
            if not self.flags["oracle_spoken"]:
                print("The oracle whispers:")
                print("“Three endings spiral: flee, mend, or unmake.”")
                print("“But beware: the star may also break loose and choose for you.”")
                self.flags["oracle_spoken"] = True
            else:
                print("“The stars already wait.”")
        else:
            print("Silence answers.")

    # -----------------------------
    # USE LOGIC
    # -----------------------------

    def use(self, item):
        room = self.current.name

        if item not in self.inventory:
            print("You do not possess that.")
            return

        # Bridge stabilization -> unlock Fracture Maw route (and keep it reversible)
        if item == "gravity seed" and room == "Broken Skybridge" and not self.flags["bridge"]:
            print("Roots spiral outward, knitting the void.")
            self.flags["bridge"] = True
            self.rooms["Broken Skybridge"].locked_exits.pop("north", None)
            self.rooms["Broken Skybridge"].exits["north"] = self.rooms["Fracture Maw"]
            return

        # Engine awakening -> open core
        if item == "resonant rod" and room == "Astral Engine" and not self.flags["engine"]:
            print("The rings awaken, humming.")
            self.flags["engine"] = True
            self.rooms["Astral Engine"].locked_exits.pop("north", None)
            self.rooms["Astral Engine"].exits["north"] = self.rooms["Star Core"]
            return

        # Mirror truth -> sets flag for RESTORATION ending
        if item == "void lens" and room == "Mirror Gallery" and not self.flags["mirror"]:
            print("False skies collapse into one.")
            self.flags["mirror"] = True
            return

        # Alignment chart reveals escape in Sanctum
        if item == "alignment chart" and room == "Inner Sanctum" and not self.flags["core_open"]:
            print("Glyphs rotate. A portal forms to the east.")
            self.flags["core_open"] = True
            self.rooms["Inner Sanctum"].locked_exits.pop("east", None)
            self.rooms["Inner Sanctum"].exits["east"] = self.rooms["Drift Gate"]
            return

        # Star shard used at Star Core -> endings (RESTORE / ESCAPE / CATASTROPHE)
        if item == "star shard" and room == "Star Core":
            self.resolve_core()
            return

        # Star shard used at Fracture Maw -> intentional UNMAKING ending
        if item == "star shard" and room == "Fracture Maw":
            self.ending_unmaking()
            return

        print("Nothing changes.")

    # -----------------------------
    # ENDINGS
    # -----------------------------

    def resolve_core(self):
        print("\nThe shard resonates with the imprisoned star.\n")

        # RESTORATION: requires awakening the engine + clarifying the mirrors
        if self.flags["engine"] and self.flags["mirror"]:
            print("You stabilize the stellar lattice.")
            print("The structure exhales and falls quiet.")
            print("\nENDING: RESTORATION\n")
            sys.exit()

        # ESCAPE: open Drift Gate, then trigger the core with the shard
        if self.flags["core_open"]:
            print("You hurl the shard into the core and flee.")
            print("The vault collapses behind you, but you remain whole.")
            print("\nENDING: ESCAPE\n")
            sys.exit()

        # CATASTROPHE: awaken engine, but do neither mirror-truth nor escape alignment
        print("The star erupts unchecked.")
        print("Reality folds inward.\n")
        print("ENDING: CATASTROPHE\n")
        sys.exit()

    def ending_unmaking(self):
        print("\nYou step to the edge of the Fracture Maw.")
        print("The shard grows cold in your palm, then impossibly heavy.")
        print("You release it.\n")
        print("For a moment, you can hear the architecture thinking.")
        print("Then it stops.\n")
        print("Everything unthreads gently, like a story allowed to end.\n")
        print("ENDING: UNMAKING\n")
        sys.exit()


if __name__ == "__main__":
    Game().play()
