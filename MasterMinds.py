from tinydb import TinyDB, Query

class GameEngine():
    def __init__(self, GamePin):
        self.GamePin = GamePin
        self.WS = []
        self.req = query.GamePin == self.GamePin
        self.liveInput = GameTB.get(req)["AvC"]

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
        print(ICode,Code)
        return (UserID, ICode, Code.count(None), len([i for i in list(filter(None, Code)) if i.isupper()]))
    def Turns(self, UserID):
        if GameTB.get(req)["Gamemode"] == 'Solo':
            return TurnTB.search(self.req & query.UserID == UserID)
        else:
            return TurnTB.search(self.req)







if __name__ == "__main__":
    query = Query()
    DB = TinyDB('Database.json')
    UserTB = DB.table("UserID")
    GameTB = DB.table("GamesPins")
    TurnTB = DB.table("Turns")
    GameEngine()
    while True:
        if
