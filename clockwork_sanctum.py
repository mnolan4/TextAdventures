import sys

# ================================
# CLOCKWORK SANCTUM — TEXT ADVENTURE (FIXED)
# ================================

class Room:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.exits = {}          # direction -> Room
        self.items = []          # list[str]
        self.locked_exits = {}   # direction -> Room (blocked)
        self.characters = {}     # name -> description

    def describe(self):
        print("\n" + self.name.upper())
        print("-" * len(self.name))
        print(self.desc)

        if self.items:
            print("\nYou see here:")
            for i in self.items:
                print(" -", i)

        if self.characters:
            print("\nSomeone is here:")
            for c in self.characters:
                print(" -", c)

        if self.exits:
            print("\nExits:")
            for e in self.exits:
                print(" -", e)


class Game:
    def __init__(self):
        self.rooms = {}
        self.inventory = []
        self.current = None
        self.flags = {
            "generator_on": False,
            "gate_open": False,
            "tower_fixed": False,
            "vault_open": False,
            "spoken_to_automaton": False
        }
        self.create_world()

    def create_world(self):
        atrium = Room("Atrium",
            "A vast stone chamber lit by flickering lanterns. Brass gears line the walls, frozen in mid-turn.\n"
            "A shattered clock face lies embedded in the floor.")

        corridor = Room("Echoing Corridor",
            "Your footsteps reverberate endlessly. Pipes snake along the ceiling, dripping oil.")

        workshop = Room("Abandoned Workshop",
            "Workbenches clutter the room. Rusted tools and half-assembled machines are scattered everywhere.")

        generator = Room("Generator Hall",
            "A titanic engine dominates the hall. Its flywheel is motionless. A control lever juts from a panel.")

        library = Room("Chronicle Library",
            "Towering shelves sag under ancient tomes. Dust floats in shafts of amber light.")

        observatory = Room("Observatory",
            "A cracked dome reveals the night sky. Telescopes point nowhere. A broken control console hums faintly.")

        tower = Room("Clock Tower",
            "The heart of the Sanctum. A massive pendulum hangs frozen. The air smells of ozone.")

        vault = Room("Vault Antechamber",
            "A circular chamber with a colossal sealed door engraved with constellations.")

        sanctum = Room("Inner Sanctum",
            "An impossible space of rotating rings and floating glyphs.\n"
            "A radiant core pulses at the center.")

        archives = Room("Hidden Archives",
            "Secret shelves of forbidden schematics and star-charts.")

        catwalk = Room("Steel Catwalk",
            "Narrow beams stretch above bottomless darkness. Steam rises below.")

        subbasement = Room("Sub-Basement",
            "Flooded stone floors. Cables snake into darkness.")

        shrine = Room("Forgotten Shrine",
            "A shrine to time itself. A bronze automaton kneels silently.")

        armory = Room("Mechanized Armory",
            "Clockwork constructs lie dismantled in alcoves.")

        exit_chamber = Room("Exit Chamber",
            "A circular portal frame dominates the room. It is currently dormant.")

        # Open connections
        atrium.exits = {"north": corridor, "east": workshop}
        corridor.exits = {"south": atrium, "north": library, "west": generator}
        workshop.exits = {"west": atrium, "north": armory}
        generator.exits = {"east": corridor, "north": catwalk}
        catwalk.exits = {"south": generator, "down": subbasement}
        subbasement.exits = {"up": catwalk, "east": shrine}
        shrine.exits = {"west": subbasement}
        library.exits = {"south": corridor, "north": observatory}
        observatory.exits = {"south": library, "east": tower}
        tower.exits = {"west": observatory}  # north is locked initially
        vault.exits = {"south": tower}       # north is sealed initially
        armory.exits = {"south": workshop, "east": archives}
        archives.exits = {"west": armory}
        exit_chamber.exits = {"west": shrine}

        # Locked exits (must be removed when unlocked)
        tower.locked_exits["north"] = vault          # to Vault Antechamber
        vault.locked_exits["north"] = sanctum        # to Inner Sanctum (sealed)
        shrine.locked_exits["east"] = exit_chamber   # hidden passage to Exit Chamber

        # Items
        workshop.items.append("wrench")
        library.items.append("star chart")
        archives.items.append("power crystal")
        subbasement.items.append("copper coil")
        atrium.items.append("brass key")
        observatory.items.append("circuit board")
        armory.items.append("energy cell")

        # NPC
        shrine.characters["automaton"] = "A kneeling bronze automaton with dim blue eyes."

        self.rooms = {
            r.name: r for r in [
                atrium, corridor, workshop, generator, library,
                observatory, tower, vault, sanctum, archives,
                catwalk, subbasement, shrine, armory, exit_chamber
            ]
        }

        self.current = atrium

    # ================= COMMAND HANDLING =================

    def play(self):
        print("\nTHE CLOCKWORK SANCTUM\n")
        print("You awaken inside an abandoned time-machine complex buried beneath the world.")
        print("Type 'help' for commands.\n")

        self.current.describe()

        while True:
            cmd = input("\n> ").strip().lower()
            self.handle(cmd)

    def handle(self, cmd):
        words = cmd.split()
        if not words:
            return

        verb = words[0]

        if verb in ("quit", "exit"):
            sys.exit()

        elif verb == "help":
            self.show_help()

        elif verb in ("go", "move"):
            if len(words) < 2:
                print("Go where?")
            else:
                self.move(words[1])

        elif verb in ("look", "examine"):
            if len(words) == 1:
                self.current.describe()
            else:
                self.examine(" ".join(words[1:]))

        elif verb in ("take", "get"):
            if len(words) < 2:
                print("Take what?")
            else:
                self.take(" ".join(words[1:]))

        elif verb == "inventory":
            self.show_inventory()

        elif verb == "use":
            if len(words) < 2:
                print("Use what?")
            else:
                self.use(" ".join(words[1:]))

        elif verb == "unlock":
            if len(words) < 2:
                print("Unlock what?")
            else:
                self.unlock(" ".join(words[1:]))

        elif verb == "talk":
            if len(words) < 2:
                print("Talk to whom?")
            else:
                self.talk(" ".join(words[1:]))

        elif verb == "read":
            if len(words) < 2:
                print("Read what?")
            else:
                self.read(" ".join(words[1:]))

        else:
            print("I don't understand that.")

    # ================= MECHANICS =================

    def move(self, direction):
        if direction in self.current.locked_exits:
            print("That way is locked.")
            return

        if direction in self.current.exits:
            self.current = self.current.exits[direction]
            self.current.describe()
        else:
            print("You can't go that way.")

    def take(self, item):
        if item in self.current.items:
            self.current.items.remove(item)
            self.inventory.append(item)
            print("Taken.")
        else:
            print("You don't see that here.")

    def examine(self, target):
        if target in self.inventory:
            print(f"You examine the {target}. It might be useful.")
        elif target in self.current.items:
            print(f"It’s just lying there: {target}.")
        elif target in self.current.characters:
            print(self.current.characters[target])
        else:
            print("You see nothing special.")

    def show_inventory(self):
        if not self.inventory:
            print("You are carrying nothing.")
        else:
            print("You are carrying:")
            for i in self.inventory:
                print(" -", i)

    def _unlock_direction(self, room, direction, room_obj=None):
        """Remove a lock barrier on a direction and (optionally) add the exit."""
        if direction in room.locked_exits:
            del room.locked_exits[direction]
        if room_obj is not None:
            room.exits[direction] = room_obj

    # ================= PUZZLES =================

    def use(self, item):
        if item not in self.inventory:
            print("You don't have that.")
            return

        room = self.current.name

        if item == "wrench" and room == "Generator Hall":
            print("You tighten several valves and strike the ignition plate.")
            print("The generator roars to life.")
            self.flags["generator_on"] = True
            return

        if item == "copper coil" and room == "Clock Tower":
            print("You fit the coil into the pendulum housing. Sparks leap.")
            print("A deep, steady ticking returns, like a heartbeat.")
            self.flags["tower_fixed"] = True
            return

        if item == "power crystal" and room == "Vault Antechamber":
            print("The sealed door drinks in the crystal's light.")
            print("With a resonant sigh, the northern door slides open.")
            self.flags["vault_open"] = True
            self._unlock_direction(self.current, "north", self.rooms["Inner Sanctum"])
            return

        if item == "energy cell" and room == "Exit Chamber":
            print("You seat the energy cell into a waiting cradle.")
            self.win()
            return

        print("That doesn't seem to work here.")

    def unlock(self, target):
        # Unlock the vault from the Clock Tower
        if target == "vault" and self.current.name == "Clock Tower":
            if "brass key" not in self.inventory:
                print("You need a key.")
                return
            if not self.flags["tower_fixed"]:
                print("The mechanism resists. The tower feels... incomplete.")
                return

            print("You unlock the vault door. It grinds open.")
            self._unlock_direction(self.current, "north", self.rooms["Vault Antechamber"])
            return

        # Reveal/unlock the hidden exit at the Shrine
        if target == "exit" and self.current.name == "Forgotten Shrine":
            if not self.flags["spoken_to_automaton"]:
                print("You feel along the wall, but find no seam to work with.")
                return
            print("Hidden mechanisms click. A passage reveals itself to the east.")
            self._unlock_direction(self.current, "east", self.rooms["Exit Chamber"])
            return

        print("You can't unlock that yet.")

    def talk(self, target):
        if target == "automaton" and self.current.name == "Forgotten Shrine":
            print("\nThe automaton's eyes brighten.")
            print("\"The engine sleeps. The tower must sing again. The vault requires starlight.\"")
            self.flags["spoken_to_automaton"] = True
            return

        print("No response.")

    def read(self, item):
        if item == "star chart" and item in self.inventory:
            print("The chart shows the vault constellation sequence: Orion, Lyra, Draco.")
            print("It feels like a clue from an older version of this place.")
            return

        print("You can't read that.")

    # ================= ENDING =================

    def win(self):
        print("\nThe portal stabilizes, swirling with impossible light.")
        print("You step forward as the Sanctum collapses behind you.")
        print("\nYOU ESCAPE THE CLOCKWORK SANCTUM.")
        print("\nThanks for playing.\n")
        sys.exit()

    def show_help(self):
        print("""
Commands:
 go <direction>
 take <item>
 use <item>
 unlock <thing>
 talk <character>
 read <item>
 examine <thing>
 inventory
 help
 quit
""")


if __name__ == "__main__":
    Game().play()
