import sys
import getopt
from tinydb import TinyDB, Query
import time
import random
import string

Colours = ["red", "orange", "yellow", "green",
           "blue", "purple", "pink", "brown"]

Objects = []

DB = TinyDB('Database.json')
UserTB = DB.table("UserID")
GameTB = DB.table("GamesPins")
TurnTB = DB.table("Turns")
query = Query()

def Debug(*input):
    if "-d" in sys.argv[1:] or "--degug" in sys.argv[1:]:
        if len(input) > 0:
            print("# DEBUG: ",*input)
        return True
    return False


class GameEngine():
    def __init__(self, GamePin=None):
        self.GamePin = GamePin
        self.WS = []
        self.req = query.GamePin == self.GamePin
        self.liveInput = GameTB.get(self.req)["AvailableColours"] if GamePin else None
        Objects.append(self)

    def CreateGame(self, UserID, Grade=(4,4), Team=False):
        if isinstance(Grade, str):
            try:
                Graded = {"PrePrep-1":(2,2),"2-3":(4,4),"4-6":(6,4),"7-9":(8,4),"10-12":(12,6)}[Grade]
            except:
                try:
                    Graded = [int(G) for G in Grade.split(",")]
                    Grade = "Custom"
                except:
                    Debug("Wrong Input")
                    return False
        else:
            Graded = Grade
            Grade = "Custom"

        self.GamePin = CreateUniqID(5)
        self.req = query.GamePin == self.GamePin
        self.liveInput = [Colours[i] for i in range(0, Graded[1])]
        GameTB.insert({"GamePin": self.GamePin,"Creator": UserID,"Code": [random.choice(Colours) for i in range(
            0, Graded[1])], "AvailableColours": Graded[0], "Grade": Grade, "Creation": time.time(), "Playing": False, "Team": Team})
        Debug("Created Game with a GamePin of", self.GamePin)
        return self

    def delete(self, UserID):
        if UserID == GameTB.get(self.req)["Creator"]:
            GameTB.remove(self.req)
            Objects.remove(self)
            return True
        return False

    def Play(self, UserID, ICode, Code=None):
        if not GameTB.get(self.req):
            return False
        Code = Code if Code else GameTB.get(self.req)["Code"]
        if Code == ICode:
            return (UserID, ICode, len(ICode), 0)
        for i in range(0, len(Code)):
            done = False
            if Code[i] == ICode[i]:
                Code[i] = None
                done = True
            elif Code[i].lower() == ICode[i]:
                Code[i] = None
            if ICode[i] in Code and not done:
                Code[Code.index(ICode[i])] = ICode[i].upper()
        Debug(ICode, Code)
        # add the Turn to the TurnTB
        return (UserID, Code.count(None), ICode, len([i for i in list(filter(None, Code)) if i.isupper()]))

    def Turns(self, UserID):
        if GameTB.get(req)["Gamemode"] == 'Solo':
            return TurnTB.search(self.req & query.UserID == UserID)
        else:
            return TurnTB.search(self.req)


def GetObject(GamePin):
    Debug("Finding", GamePin)
    Debug("Found", [Object for Object in Objects if Object.GamePin == GamePin])
    return [Object for Object in Objects if Object.GamePin == GamePin][0]


def GetWebSocket(GamePin, UserID):
    return [User for User in GetObject(GamePin) if User.UserID == UserID][0]


def CreateUniqID(length):
    id = ''.join([random.choice(string.ascii_letters + string.digits)
                  for _ in range(1, length)])
    while UserTB.search(query.UserID == id):
        id = ''.join([random.choice(string.ascii_letters + string.digits)
                      for n in range(1, length)])
    return id


Debug([GameEngine(Game["GamePin"]) for Game in GameTB])

if __name__ == "__main__":
    Debug("You are in Debugging Mode")
    GN = input("What your Uniq ID:>")
    GP = input("GamePin ('n' if you don't have one):>")
    if GP.lower() == "n":
        print("--Grades--\nPrePrep-1:(2,2)\n2-3:(4,4)\n4-6:(6,4)\n7-9:(8,4)\n10-12:(12,6)\n2-4 is defaulted")
        GP = input("Grade:")
        GP = GameEngine().CreateGame(GN,GP if GP else "2-4")
        print("Your GamePin is:",GP.GamePin)
    else:
        GP = GameEngine(GP)
    Debug("Your Game Code is:",GameTB.get(GP.req)["Code"])
    while True:
        print(GP.Play("CMD",input("Code:").split(","))[1:])
