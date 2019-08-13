import tornado.ioloop
import time
import random
import string
import json
import sys
from tornado.util import _websocket_mask
import tornado.websocket
import tornado.web
from pyjade.ext.tornado import patch_tornado
from tornado import template
import MasterMinds as MM
import getopt
patch_tornado()


def Debug(*input):
    if "-d" in sys.argv[1:] or "--degug" in sys.argv[1:]:
        if len(input) > 0:
            print(*input)
        return True
    return False



class Home(tornado.web.RequestHandler):
    def get(self):
        if (not self.get_cookie("id")) or MM.UserTB.search(MM.query.UserID == self.get_cookie("id")) == []:
            Id = MM.CreateUniqID(6)
            self.set_cookie("id", Id)
            MM.UserTB.insert({"UserID": Id, "LastLogin": time.time(
            ), "UserName": None, "Games": None, "Wins": None})
            Debug("Added New User:", Id)
        else:
            MM.UserTB.update({"LastLogin": time.time()},
                          MM.query.UserID == self.get_cookie("id"))
        Debug("User", self.get_cookie("id"), "Joins the 'Home Page'")
        Debug(MM.UserTB.get(MM.query.UserID == self.get_cookie("id")))
        self.render("Templates/Form.html", OwnedGames = list(MM.GameTB.search(MM.query.Creator == self.get_cookie("id"))), Form='Home', Username = MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))["UserName"] if MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))["UserName"] else "")


class JoinGame(tornado.web.RequestHandler):
    def get(self):
        if (not self.get_cookie("id")) or MM.UserTB.search(MM.query.UserID == self.get_cookie("id")) == []:
            Id = MM.CreateUniqID(6)
            self.set_cookie("id", Id)
            MM.UserTB.insert({"UserID": Id, "LastLogin": time.time(
            ), "UserName": None, "Games": None, "Wins": None})
            Debug("Added New User:", Id)
        else:
            MM.UserTB.update({"LastLogin": time.time()},
                          MM.query.UserID == self.get_cookie("id"))
        Debug("User", self.get_cookie("id"), "Joins the 'Join Game Page'")
        self.render("Templates/Form.html", Form='Join', Username = MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))["UserName"] if MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))["UserName"] else "")


class CreateGame(tornado.web.RequestHandler):
    def get(self):
        if (not self.get_cookie("id")) or MM.UserTB.search(MM.query.UserID == self.get_cookie("id")) == []:
            Id = MM.CreateUniqID(6)
            self.set_cookie("id", Id)
            MM.UserTB.insert({"UserID": Id, "LastLogin": time.time(
            ), "UserName": None, "Games": None, "Wins": None})
            Debug("Added New User:", Id)
        else:
            MM.UserTB.update({"LastLogin": time.time()},
                          MM.query.UserID == self.get_cookie("id"))
        Debug("User", self.get_cookie("id"), "Joins the 'Create Game Page'")
        self.render("Templates/Form.html", Form='Create', Username = MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))["UserName"] if MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))["UserName"] else "")


class Game(tornado.web.RequestHandler):
    def get(self, GamePin):
        if not MM.GameTB.search(MM.query.GamePin == GamePin):
            self.redirect("/Join?Pin=" + GamePin)
        if (not self.get_cookie("id")) or MM.UserTB.get(MM.query.UserID == self.get_cookie("id")) == []:
            Debug("IDless User tryed to join Game <:> User sent back to the /join")
            # Sends the MM.query to back to the join page due to the MM.query not have a id or username
            self.redirect("/Join")
        else:
            MM.UserTB.update({"LastLogin": time.time()},
                          MM.query.UserID == self.get_cookie("id"))
            if not MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))["UserName"]:
                Debug("Nameless User tryed to join Game <:> User sent back to the /join")
                # Send the MM.query to back to the join page due to the MM.query not have a username
                self.redirect("/Join")
            else:
                if Game.get(MM.query.ID == self.get_cookie("id"))["UserName"]:
                    pass
                Debug("User", self.get_cookie("id"),
                      "Sign into Game:", GamePin)
                self.render("/Templates/Game.html")


class MainWebsocket(tornado.websocket.WebSocketHandler):

    def open(self):
        pass

    def on_message(self, message):
        Debug("Received Main WebSocket:",message)
        caseswitch = {"cu": self.connect,
                      "uu": self.UpdateUser, "cg": self.CreateGame}
        try:
            message = json.loads(message)
            if message["action"] in caseswitch.keys():
                caseswitch[message["action"]](*message["Arg"])
                self.write_message('{"action":"sa"}')
                return
        except TypeError:
            print("Invalid Arguments")
        except json.decoder.JSONDecodeError:
            print("Invalid JSON string")
        self.write_message('{"action":"fa"}')
    def on_close(self):
        pass

    def connect(self, UserID):
        self.UserID = UserID
        pass

    def UpdateUser(self, UserName):
        Debug("Added a UserName of", UserName, "to", self.UserID)
        MM.UserTB.update({"UserName": UserName}, MM.query.UserID == self.UserID)
        pass

    def CreateGame(self, *Arg):
        self.Game = MM.GameEngine().CreateGame(*Arg)



class GameWebsocket(tornado.websocket.WebSocketHandler):
    def open(self):
        pass

    def on_message(self, message):
        Debug("Received Game WebSocket:",message)
        caseswitch = {"cu": self.connect,
                      "qg": self.Quit, "pg": self.Play, "gc": self.Colour}
        try:
            message = json.loads(message)
            if message["action"] in caseswitch.keys():
                caseswitch[message["action"]](*message["Arg"])
                self.write_message('{"action":"sa"}')
                return

        except TypeError:
            print("Invalid Arguments")
        except json.decoder.JSONDecodeError:
            print("Invalid JSON string")
        self.write_message('{"action":"fa"}')

    def on_close(self):
        pass

    def connect(self, UserID):
        self.UserID = UserID

    def Quit(self, GamePin):
        pass

    def Play(self, GamePin, Code):
        pass

    def Colour(self, GamePin, Index, Colour):
        if not ("-lb" in sys.argv[1:] or "--low_bandwidth " in sys.argv[1:]):
            pass


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
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()
