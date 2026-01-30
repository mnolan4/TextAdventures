import sys

# ==========================
# HEARTHLIGHT HOLLOW — A COZY TEXT ADVENTURE
# ==========================

LOCKED = "[LOCKED]"

def dim(t): return f"{LOCKED} {t}"

# ---------- Room ----------

class Room:
    def __init__(self,name,desc):
        self.name=name
        self.desc=desc
        self.exits={}
        self.locked_exits={}
        self.items=[]
        self.npcs=[]

    def describe(self):
        print(f"\n{self.name.upper()}")
        print("-"*len(self.name))
        print(self.desc)

        if self.items:
            print("\nYou notice:")
            for i in self.items: print(" -",i)

        if self.npcs:
            print("\nHere:")
            for n in self.npcs: print(" -",n)

        if self.exits or self.locked_exits:
            print("\nPaths:")
            for e in self.exits: print(" -",e)
            for e in self.locked_exits: print(" -",dim(e))

# ---------- Game ----------

class Game:
    def __init__(self):
        self.rooms={}
        self.current=None
        self.inventory=[]
        self.journal=[]
        self.flags={
            "windmill":False,
            "docklit":False,
            "oven":False,
            "final":False
        }

        self.metrics={"Warmth":0,"Glow":0,"Care":0,"Order":0,"Rest":0}

        self.build_world()

    # ---------- World ----------

    def build_world(self):
        R=lambda n,d:Room(n,d)

        green=R("Village Green","A moss-ringed circle of benches and lanterns. Steam drifts from an unattended kettle.")
        lantern=R("Lantern Fields","Tall reeds cradle sputtering glass lanterns.")
        windmill=R("Windmill Loft","Canvas sails hang slack above a gummy axle.")
        bakery=R("Bakery","A brick oven sleeps cold.")
        grove=R("Mushroom Grove","Glow-caps dot fallen logs.")
        dock=R("River Dock","Wood pylons creak over black water.")
        greenhouse=R("Greenhouse","Fogged panes drip warmth.")
        attic=R("Workshop Attic","Oil tins and matches litter shelves.")
        clockshop=R("Clock Shop","Ticking birds perch above a humming drawer.")
        library=R("Library","Floating books shelve themselves.")
        archive=R("Archive Nook","Ledgers and civic memory.")
        townhall=R("Town Hall","Long tables and folded banners. A stair winds down.")
        hearth=R("Hearth Chamber","A colossal hearth waits with five empty cradles.")
        tea=R("Teahouse Alcove","Low cushions and murmuring kettles.")
        balcony=R("Festival Balcony","Lantern light floods snowy hills.")

        # Exits
        green.exits={"north":lantern,"east":bakery,"south":dock,"west":grove}
        lantern.exits={"south":green,"north":windmill}
        windmill.exits={"south":lantern}

        bakery.exits={"west":green,"up":attic}
        attic.exits={"down":bakery,"east":clockshop}
        clockshop.exits={"west":attic}

        grove.exits={"east":green}

        dock.exits={"north":green,"east":archive,"west":greenhouse}
        greenhouse.exits={"east":dock}
        archive.exits={"west":dock}

        library.exits={"east":green,"west":tea}
        tea.exits={"east":library}

        townhall.exits={"south":green}   # down locked initially
        hearth.exits={"up":townhall}

        # Locks
        lantern.locked_exits["north"]=windmill
        dock.locked_exits["east"]=archive
        townhall.locked_exits["down"]=hearth

        # Items
        green.items=["kettle"]
        lantern.items=["dry wick"]
        grove.items=["glow-caps","kindling"]
        attic.items=["oil flask","matches"]
        greenhouse.items=["bellows"]

        # NPCs
        bakery.npcs=["baker"]
        grove.npcs=["forager"]
        clockshop.npcs=["clockmaker"]
        library.npcs=["librarian"]
        dock.npcs=["ferrier"]
        greenhouse.npcs=["caretaker"]
        tea.npcs=["host"]
        townhall.npcs=["mayor"]

        for r in [green,lantern,windmill,bakery,grove,dock,greenhouse,
                  attic,clockshop,library,archive,townhall,hearth,tea,balcony]:
            self.rooms[r.name]=r

        self.current=green

    # ---------- Loop ----------

    def play(self):
        print("\n🍵 THE HEARTHLIGHT HOLLOW 🍵\n")
        self.current.describe()
        while True:
            self.handle(input("\n> ").strip().lower())

    # ---------- Command Handling ----------

    def handle(self,cmd):
        if not cmd: return
        w=cmd.split(); v=w[0]

        if v in("quit","exit"): sys.exit()
        elif v=="look": self.current.describe()
        elif v=="inventory": self.show_inventory()
        elif v=="journal": self.show_journal()
        elif v=="status": self.show_status()
        elif v=="commands": self.show_commands()
        elif v=="go": self.move(w[1] if len(w)>1 else "")
        elif v=="take": self.take(" ".join(w[1:]))
        elif v=="talk": self.talk(" ".join(w[1:]))
        elif v=="use": self.use(" ".join(w[1:]))
        elif v=="rest": self.rest()
        else: print("You pause, unsure how to do that.")

    # ---------- UI ----------

    def show_inventory(self):
        if not self.inventory: print("Your pockets are empty.")
        else:
            print("You carry:")
            for i in self.inventory: print(" -",i)

    def show_journal(self):
        print("\nJournal:")
        for j in self.journal: print("•",j)

    def show_status(self):
        print("\nVillage Atmosphere:")
        for k,v in self.metrics.items():
            mood="low"
            if v>=3: mood="rising"
            if v>=6: mood="warm"
            print(f"{k}: {mood}")

    def show_commands(self):
        print("\nPossible actions:\n")
        for e in self.current.exits: print("GO",e)
        for e in self.current.locked_exits: print(dim(f"GO {e}"))
        for i in self.current.items: print("TAKE",i)
        for n in self.current.npcs: print("TALK",n)

        # contextual puzzle hints
        if self.current.name=="Windmill Loft":
            print("USE oil flask" if "oil flask" in self.inventory else dim("USE oil flask"))
        if self.current.name=="River Dock":
            cond={"kettle","glow-caps","dry wick"}.issubset(self.inventory)
            print("USE kettle" if cond else dim("USE kettle"))
        if self.current.name=="Bakery":
            cond={"matches","bellows","kindling"}.issubset(self.inventory)
            print("USE oven" if cond else dim("USE oven"))
        if self.current.name=="Hearth Chamber":
            print("USE hearth")

        print("LOOK\nREST")

    # ---------- Movement ----------

    def move(self,d):
        if d in self.current.locked_exits:
            print("That way is closed for now.")
            return
        if d in self.current.exits:
            self.current=self.current.exits[d]
            self.current.describe()
        else:
            print("You can't go that way.")

    # ---------- Basic ----------

    def take(self,item):
        if item in self.current.items:
            self.current.items.remove(item)
            self.inventory.append(item)
            print("You pick it up gently.")
        else: print("You don't see that.")

    def rest(self):
        print("You sit quietly and breathe.")
        self.metrics["Rest"]+=1

    # ---------- NPC ----------

    def talk(self,npc):
        r=self.current.name

        if npc=="baker" and r=="Bakery":
            print("“Cold ovens chill whole streets.”")

        elif npc=="forager":
            print("“Gather fallen wood only.”")
            self.metrics["Care"]+=1

        elif npc=="clockmaker":
            if self.flags["windmill"] and "brass medallion" not in self.inventory:
                print("The clockmaker gifts you a brass medallion.")
                self.inventory.append("brass medallion")
            else:
                print("“Rhythm comes before precision.”")

        elif npc=="librarian":
            print("“Shelve one row at a time.”")
            self.metrics["Order"]+=1

        elif npc=="ferrier":
            print("“Cross when the river glows.”" if not self.flags["docklit"] else "“Whenever you wish.”")

        elif npc=="caretaker":
            if self.flags["docklit"] and "bellows" not in self.inventory:
                print("The caretaker hands you bellows.")
                self.inventory.append("bellows")
            else:
                print("“Plants like warm villages.”")

        elif npc=="mayor":
            self.check_gate()

        elif npc=="host":
            print("Tea warms you.")
            self.metrics["Rest"]+=2

        else: print("They nod politely.")

    # ---------- Use ----------

    def use(self,item):
        r=self.current.name

        if item not in self.inventory and item!="hearth":
            print("You don't have that.")
            return

        if item=="oil flask" and r=="Windmill Loft" and not self.flags["windmill"]:
            print("The sails begin turning.")
            self.flags["windmill"]=True
            self.metrics["Order"]+=2
            self.rooms["Lantern Fields"].locked_exits.pop("north",None)
            return

        if r=="River Dock" and item=="kettle" and not self.flags["docklit"]:
            if {"glow-caps","dry wick"}.issubset(self.inventory):
                print("Lanterns blaze across the water.")
                self.flags["docklit"]=True
                self.metrics["Glow"]+=3
                self.rooms["River Dock"].locked_exits.pop("east",None)
            else:
                print("The lantern lacks fuel and wick.")
            return

        if r=="Bakery" and item in ("matches","bellows","kindling"):
            if not self.flags["oven"] and {"matches","bellows","kindling"}.issubset(self.inventory):
                print("The oven glows warmly. The baker gifts you a honey roll.")
                self.inventory.append("honey roll")
                self.flags["oven"]=True
                self.metrics["Warmth"]+=3
            else:
                print("The oven needs more tending.")
            return

        if r=="Hearth Chamber" and item=="hearth":
            self.final_ritual()
            return

        print("That doesn’t belong here.")

    # ---------- Final ----------

    def check_gate(self):
        need={"brass medallion","honey roll","bellows","kettle"}
        if need.issubset(self.inventory):
            print("The mayor opens the stair.")
            self.rooms["Town Hall"].locked_exits.pop("down",None)
        else:
            print("“The hearth wants patience.”")

    def final_ritual(self):
        need={"brass medallion","honey roll","bellows","kettle"}
        if need.issubset(self.inventory):
            print("\nThe hearth flares. Lanterns bloom outward.\n")
            self.endgame()
        else:
            print("The hearth waits gently.")

    # ---------- Ending ----------

    def endgame(self):
        score=sum(self.metrics.values())

        if score>=15:
            print("Music rises. You ascend to the balcony and watch the valley glow.")
        elif score>=8:
            print("Villagers gather with scarves and mugs.")
        else:
            print("The hearth glows steady and sure.")

        print("\n🌙 THANK YOU FOR PLAYING 🌙\n")
        sys.exit()

if __name__=="__main__":
    Game().play()
