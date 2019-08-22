import tornado.ioloop
import time
import random
import string
import json
import sys
from tornado.util import _websocket_mask
import tornado.websocket
import tornado.web
from tornado import template
import MasterMinds as MM
import getopt


def Debug(*input):
    if "-d" in sys.argv[1:] or "--degug" in sys.argv[1:]:
        if len(input) > 0:
            print("# DEBUG: ", *input)
        return True
    return False


def Connected(self):
    if (not self.get_cookie("id")) or MM.UserTB.search(MM.query.UserID == self.get_cookie("id")) == []:
        Id = MM.CreateUniqID(6)
        self.set_cookie("id", Id)
        MM.UserTB.insert({"UserID": Id, "LastLogin": time.time(
        ), "UserName": None, "Wins": None})
        Debug("Added New User:", Id)
        return Id
    MM.UserTB.update({"LastLogin": time.time()},
                     MM.query.UserID == self.get_cookie("id"))
    return self.get_cookie("id")


class Home(tornado.web.RequestHandler):
    def get(self):
        Id = Connected(self)
        Debug("User", self.get_cookie("id"), "Joins the 'Home Page'")
        Debug(MM.UserTB.get(MM.query.UserID == self.get_cookie("id")))
        self.render("Templates/Form.html", OwnedGames=list(MM.GameTB.search(MM.query.Creator == Id)), Form='Home',
                    Username=MM.UserTB.get(MM.query.UserID == Id)["UserName"] if MM.UserTB.get(MM.query.UserID == Id)["UserName"] else "")


class JoinGame(tornado.web.RequestHandler):
    def get(self):
        Id = Connected(self)
        Debug("User", Id, "Joins the 'Join Game Page'")
        self.render("Templates/Form.html", Form='Join', Username=MM.UserTB.get(MM.query.UserID ==
                                                                               Id)["UserName"] if MM.UserTB.get(MM.query.UserID == Id)["UserName"] else "")


class CreateGame(tornado.web.RequestHandler):
    def get(self):
        Id = Connected(self)
        Debug("User", self.get_cookie("id"), "Joins the 'Create Game Page'")
        self.render("Templates/Form.html", Form='Create', Username=MM.UserTB.get(MM.query.UserID ==
                                                                                 Id)["UserName"] if MM.UserTB.get(MM.query.UserID == Id)["UserName"] else "")


class Game(tornado.web.RequestHandler):
    def get(self, GamePin):
        GameValues = MM.GameTB.search(MM.query.GamePin == GamePin)
        if not GameValues:
            self.redirect("/Join?Pin=" + GamePin)
        if (not self.get_cookie("id")) or MM.UserTB.get(MM.query.UserID == self.get_cookie("id")) == []:
            Debug("IDless User tryed to join Game <:> User sent back to the /join")
            # Sends the MM.query to back to the join page due to the MM.query not have a id or username
            self.redirect("/Join")
        else:
            if not MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))["UserName"]:
                Debug("Nameless User tryed to join Game <:> User sent back to the /join")
                # Send the MM.query to back to the join page due to the MM.query not have a username
                self.redirect("/Join")
            else:
                GameValues = GameValues[0]
                Debug("User", self.get_cookie("id"),
                      "Sign into Game:", GamePin)
                Code = GameValues["Code"] if Debug() else []
                if GameValues["Playing"]:
                    bw = "true" if GameValues["Team"] or "-lb" in sys.argv[1:
                                                                           ] or "--low_bandwidth" in sys.argv[1:] else "false"
                    self.render("Templates/Game.html", Lowbandwidth=bw, Username=MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))[
                                "UserName"], Colours=MM.GetObject(GamePin).liveInput, Turns=MM.GetObject(GamePin).Turns(self.get_cookie("id")), Code=Code, AvailableColours=MM.GameTB.search(MM.query.GamePin == GamePin)[0]["AvailableColours"])
                    return
                self.render("Templates/Waiting.html", UsersConnected=MM.GetObject(GamePin).GetUsers()[1:], Username=MM.UserTB.get(
                    MM.query.UserID == self.get_cookie("id"))["UserName"] if MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))["UserName"] else "")

    def post(self, GamePin):
        MM.GameTB.update({"Playing": True}, MM.query.GamePin == GamePin)
        [SendCommand(user, "rd", "/g/" + GamePin)
         for user in MM.GetObject(GamePin).GetWebSockets()]
        Code = MM.GameTB.search(MM.query.GamePin == GamePin)[
            0]["Code"] if Debug() else []
        Debug("Game has Started")
        bw = "true" if MM.GameTB.get(MM.query.GamePin == GamePin)[
            "Team"] or "-lb" in sys.argv[1:] or "--low_bandwidth" in sys.argv[1:] else "false"
        self.render("Templates/Game.html", Lowbandwidth=bw, Username=MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))
                    ["UserName"], Colours=MM.GetObject(GamePin).liveInput, Turns=MM.GetObject(GamePin).Turns(self.get_cookie("id")), Code=Code, AvailableColours=MM.GameTB.search(MM.query.GamePin == GamePin)[0]["AvailableColours"])


class MainWebsocket(tornado.websocket.WebSocketHandler):
    def open(self):
        pass

    def on_message(self, message):
        Debug("Received Main WebSocket:", message)
        caseswitch = {"cu": self.connect,
                      "uu": self.UpdateUser, "cg": self.CreateGame, "rg": self.RemoveGame}
        try:
            message = json.loads(message)
            if message["action"] in caseswitch.keys():
                if caseswitch[message["action"]](*message["Arg"]):
                    SendCommand(self, "sa")
                    return
        except TypeError:
            print("Invalid Arguments")
        except json.decoder.JSONDecodeError:
            print("Invalid JSON string")
        except AttributeError:
            print("Invalid Client")
        SendCommand(self, "fa")

    def on_close(self):
        pass

    def connect(self, UserID):
        if self.get_cookie("id") == UserID:
            self.UserID = UserID
            return True
        else:
            self.close()

    def UpdateUser(self, UserName):
        Debug("Added a UserName of", UserName, "to", self.UserID)
        MM.UserTB.update({"UserName": UserName},
                         MM.query.UserID == self.UserID)

    def CreateGame(self, *Arg):
        Game = MM.GameEngine().CreateGame(self.UserID, *Arg)
        if Game:
            SendCommand(self, "rd", "/G/" + Game.GamePin)
        return Game

    def RemoveGame(self, GamePin):
        return MM.GetObject(GamePin).delete(self.UserID)


class GameWebsocket(tornado.websocket.WebSocketHandler):
    def open(self):
        pass

    def on_message(self, message):
        Debug("Received Game WebSocket:", message)
        caseswitch = {"cu": self.connect,
                      "qg": self.Quit, "pg": self.Play, "cc": self.Colour}
        try:
            message = json.loads(message)
            if message["action"] in caseswitch.keys():
                caseswitch[message["action"]](*message["Arg"])
                SendCommand(self, "sa")
                return
        except TypeError:
            print("Invalid Arguments")
        except json.decoder.JSONDecodeError:
            print("Invalid JSON string")
        SendCommand(self, "fa")

    def on_close(self):
        Debug("User", self.get_cookie("id"), "disconnected")
        try:
            if MM.GetObject(self.GamePin).PlayerPlaying == self.UserID and MM.GetObject(self.GamePin).RemoveUser(self.UserID):
                MM.GetObject(self.GamePin).NextTurn()
                [SendCommand(ws, "nt", MM.GetObject(self.GamePin).PlayerPlaying)
                 for ws in MM.GetObject(self.GamePin).GetWebSockets()]
        except:
            pass

    def connect(self, UserID, GamePin):
        if self.get_cookie("id") == UserID:
            self.UserID = self.get_cookie("id")
            self.GamePin = GamePin
            MM.GetObject(self.GamePin).AddUser(self.get_cookie("id"), self)
            if MM.GetObject(self.GamePin).PlayerPlaying == None:
                MM.GetObject(
                    self.GamePin).PlayerPlaying = self.get_cookie("id")
                [SendCommand(ws, "nt", self.get_cookie("id"))
                 for ws in MM.GetObject(self.GamePin).GetWebSockets()]
        else:
            self.close()

    def Start(self):
        pass

    def Play(self, Code):
        results = MM.GetObject(self.GamePin).Play(self.UserID, Code.split(","))
        [SendCommand(ws,"pr",*results) for ws in MM.GetObject(self.GamePin).GetWebSockets()]
        [SendCommand(ws, "nt", MM.GetObject(self.GamePin).PlayerPlaying) for ws in MM.GetObject(self.GamePin).GetWebSockets()]

    def Quit(self):
        pass

    def Colour(self, Index, Colour):
        Index = int(Index)
        MM.GetObject(self.GamePin).liveInput[Index] = Colour
        [SendCommand(ws,"cc", Index, Colour) for ws in MM.GetObject(
            self.GamePin).GetWebSockets(self.UserID)]


def SendCommand(self, action, *Arg):
    try:
        Debug("Sending", '{"action":"' + action +
              '","Arg":' + str(list(Arg)).replace("'", '"') + '}')

        self.write_message(
            ('{"action":"' + action + '","Arg":' + str(list(Arg)).replace("'", '"') + '}'))
    except :
        print("WebSocket Failed to Send to", self.UserID)


def Start():
    return tornado.web.Application([
        (r"/", Home),
        (r"/Join", JoinGame),
        (r"/join", JoinGame),
        (r"/j", JoinGame),
        (r"/J", JoinGame),
        (r"/ws", MainWebsocket),
        (r"/G/ws", GameWebsocket),
        (r"/Game/Create", CreateGame),
        (r"/game/Create", CreateGame),
        (r"/G/Create", CreateGame),
        (r"/g/Create", CreateGame),
        (r"/Game/([^/]+)", Game),
        (r"/game/([^/]+)", Game),
        (r"/G/([^/]+)", Game),
        (r"/g/([^/]+)", Game),
        (r'/Static/(.*)', tornado.web.StaticFileHandler, {'path': "Static/"})

    ], cookie_secret="qwrQzP8pyuykv7PGjReAmANxtLtAHz95")


if __name__ == "__main__":

    argument = None
    Options = {}
    for i in sys.argv[1:]:
        if "-" in i or "--" in i:
            argument = i
        else:
            Options[argument] = i
    if "-p" in Options.keys():
        port = Options["-p"]
    elif "--port" in Options.keys():
        port = Options["--port"]
    else:
        port = 80

    Debug("You are in Debugging Mode")
    print("Starting Webserver on port", port)
    app = Start()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
