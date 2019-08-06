Colours = ["red", "orange", "yellow", "green","blue", "purple", "pink", "brown"]
Objects = []

class GameEngine():
    def __init__(self, GamePin):
        self.GamePin = GamePin
        self.WS = []
        self.req = query.GamePin == self.GamePin
        self.liveInput = GameTB.get(req)["AoC"] if GamePin else None
        Objects.append(self)

    def CreateGame(self, Length=4, NoC=4, Grade="3-4", UserID, Team):
        self.GamePin = CreateUniqID(5)
        self.req = query.GamePin == self.GamePin
        self.liveInput = [Colours[i] for i in range(0,Length)]
        GameTB.insert({"GamePin":self.GamePin, "Code": [random.choice(self.Colours) for i in range(0, Length)], "AvailableColours": NoC, "Grade":Grade, "Creation": time.time(), "Playing": False, "Team": Team})


    def play(self, UserID, ICode, Code=None):
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
        print(ICode, Code)
        return (UserID, ICode, Code.count(None), len([i for i in list(filter(None, Code)) if i.isupper()]))

    def Turns(self, UserID):
        if GameTB.get(req)["Gamemode"] == 'Solo':
            return TurnTB.search(self.req & query.UserID == UserID)
        else:
            return TurnTB.search(self.req)

def GetObject(self, GamePin):
    return Objects[[Object.GamePin for Object in Objects].index(GamePin)]

def CreateUniqID(length):
    id = ''.join([random.choice(string.ascii_letters + string.digits)
                  for _ in range(1, length)])
    while UserTB.search(query.UserID == id):
        id = ''.join([random.choice(string.ascii_letters + string.digits)
                      for n in range(1, length)])
    return id


if __name__ == "__main__":
    from tinydb import TinyDB, Query
    import time
    DB = TinyDB('Database.json')
    UserTB = DB.table("UserID")
    GameTB = DB.table("GamesPins")
    TurnTB = DB.table("Turns")
    query = Query()
    GameEngine()
    while True:
        if
