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
            print("# DEBUG: ", *input)
        return True
    return False


class GameEngine():
    def __init__(self, GamePin=None):
        self.GamePin = GamePin
        self.WS = []
        self.req = query.GamePin == self.GamePin
        self.liveInput = Colours[:len(GameTB.get(
            self.req)["Code"])] if GamePin else None
        self.PlayerPlaying = None
        Objects.append(self)

    def CreateGame(self, UserID, Grade=(4, 4), Team=False):
        if isinstance(Grade, str):
            try:
                Graded = {"PrePrep-1": (2, 2), "2-3": (4, 4), "4-6": (6, 4),
                          "7-9": (8, 4), "10-12": (12, 6)}[Grade]
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
        GameTB.insert({"GamePin": self.GamePin, "Creator": UserID, "Code": [random.choice(Colours[:Graded[0]]) for i in range(
            0, Graded[1])], "AvailableColours": Graded[0], "Grade": Grade, "Creation": time.time(), "Playing": False, "Team": Team})
        Debug("Created Game with a GamePin of", self.GamePin)
        return self

    def delete(self, UserID = None):
        if UserID == GameTB.get(self.req)["Creator"] or UserID == None:
            GameTB.remove(self.req)
            TurnTB.remove(self.req)
            Objects.remove(self)
            print("Gone")
            return True
        return False

    def Play(self, UserID, ICode, Code=None):
        if not GameTB.get(self.req):
            return False
        Code = Code if Code else GameTB.get(self.req)["Code"]
        if Code == ICode:
            TurnTB.insert({"Code": ICode, "RightPlace": len(
                ICode), "RightColour": 0, "UserID": UserID, "GamePin": self.GamePin})
            return (UserID, len(Code), ICode, 0)
        for i in range(0, len(Code)):
            if Code[i] == ICode[i]:
                Code[i] = None
                continue
            elif Code[i].lower() == ICode[i]:
                Code[i] = None
            if ICode[i] in Code:
                Code[Code.index(ICode[i])] = ICode[i].upper()
        Debug(ICode, Code)
        TurnTB.insert({"Code": ICode, "RightPlace": Code.count(None), "RightColour": len(
            [i for i in list(filter(None, Code)) if i.isupper()]), "UserID": UserID, "GamePin": self.GamePin})
        self.NextTurn()
        # add the Turn to the TurnTB
        return (UserID, Code.count(None), ICode, len([i for i in list(filter(None, Code)) if i.isupper()]))

    def Turns(self, UserID):
        if GameTB.get(self.req)["Team"] == 'Solo':
            return TurnTB.search(self.req & query.UserID == UserID)
        else:
            return TurnTB.search(self.req)

    def AddUser(self, UserID, ws):
        if len(self.GetUsers()) < 5 or GameTB.get(self.req)["Team"] == 'Solo':
            UserTB.update({"LastLogin": time.time()},
                          query.UserID == UserID)
            self.WS.insert(0, ws)
            return True
        return False

    def RemoveUser(self, UserID):
        if UserID == self.PlayerPlaying:
            self.NextTurn()
        UserTB.update(query.UserID == UserID)
        self.WS.remove(self.GetWebSockets(UserID, True))
        return True

    def NextTurn(self):
        if not len(self.WS):
            self.PlayerPlaying = None
        else:
            Debug(self.GetUsers(self.PlayerPlaying))
            self.PlayerPlaying = self.GetUsers()[0]
            self.WS.append(self.WS.pop(0))
        return self.PlayerPlaying

    def GetUsers(self, UserID=None):
        return [ws.UserID for ws in self.WS if ws.UserID != UserID]

    def GetWebSockets(self, UserID=None, iv=False):
        return [ws for ws in self.WS if ws.UserID == UserID][0] if iv else [User for User in self.WS if User.UserID != UserID]


def GetObject(GamePin):
    Debug("Finding", GamePin)
    Found = [Object for Object in Objects if Object.GamePin == GamePin]
    return Found[0] if Found else []


def CreateUniqID(length):
    id = ''.join([random.choice(string.ascii_letters + string.digits)
                  for _ in range(1, length)])
    while UserTB.search(query.UserID == id) or GameTB.search(query.GamePin == id):
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
        GP = GameEngine().CreateGame(GN, GP if GP else "2-4")
        print("Your GamePin is:", GP.GamePin)
    else:
        GP = GameEngine(GP)
    Debug("Your Game Code is:", GameTB.get(GP.req)["Code"])
    while True:
        print(GP.Play("CMD", input("Code:").split(","))[1:])
