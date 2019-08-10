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
from tinydb import TinyDB, Query
import MasterMinds
import getopt
patch_tornado()


def Debug(*input):
    if "-d" in sys.argv[1:] or "--degug" in sys.argv[1:]:
        if len(input) > 0:
            print(*input)
        return True
    return False


DB = TinyDB('Database.json')
UserTB = DB.table("UserID")
GameTB = DB.table("GamesPins")
TurnTB = DB.table("Turns")
query = Query()


class Home(tornado.web.RequestHandler):
    def get(self):
        if not self.get_cookie("id"):
            self.set_cookie("id", MasterMinds.CreateUniqID())
            UserTB.insert({"UserID": self.get_cookie("id"), "LastLogin": time.time(
            ), "UserName": None, "Games": None, "Wins": None})
            Debug("Added New User")
        else:
            UserTB.update({"LastLogin": time.time()},
                          query.UserID == self.get_cookie("id"))
        Debug("User", self.get_cookie("id"), "Joins the 'Home Page'")
        self.render("Templates/Home.html")


class JoinGame(tornado.web.RequestHandler):
    def get(self):
        if not self.get_cookie("id"):
            self.set_cookie("id", MasterMinds.CreateUniqID())
            UserTB.insert({"UserID": self.get_cookie("id"), "LastLogin": time.time(
            ), "UserName": None, "Games": None, "Wins": None})
            Debug("Added New User")
        else:
            UserTB.update({"LastLogin": time.time()},
                          query.UserID == self.get_cookie("id"))
        Debug("User", self.get_cookie("id"), "Joins the 'Join Game Page'")
        self.render()


class CreateGame(tornado.web.RequestHandler):
    def get(self):
        if not self.get_cookie("id"):
            self.set_cookie("id", MasterMinds.CreateUniqID())
            UserTB.insert({"UserID": self.get_cookie("id"), "LastLogin": time.time(
            ), "UserName": None, "Games": None, "Wins": None})
            Debug("Added New User")
        else:
            UserTB.update({"LastLogin": time.time()},
                          query.UserID == self.get_cookie("id"))
        Debug("User", self.get_cookie("id"), "Joins the 'Create Game Page'")
        self.render()


class Game(tornado.web.RequestHandler):
    def get(self, GamePin):
        if not GameTB.search(query.GamePin == GamePin):
            self.redirect("/Join?Pin=" + GamePin)
        if not self.get_cookie("id"):
            Debug("IDless User tryed to join Game <:> User sent back to the /join")
            # Sends the query to back to the join page due to the query not have a id or username
            self.redirect("/Join")
        else:
            UserTB.update({"LastLogin": time.time()},
                          query.UserID == self.get_cookie("id"))
            if not UserTB.get(query.UserID == self.get_cookie("id"))["UserName"]:
                Debug("Nameless User tryed to join Game <:> User sent back to the /join")
                # Send the query to back to the join page due to the query not have a username
                self.redirect("/Join")
            else:
                if Game.get(query.ID == self.get_cookie("id"))["UserName"]:
                    pass
                Debug("User", self.get_cookie("id"),
                      "Sign into Game:", GamePin)
                self.render("/Templates/Game.html")


class MainWebsocket(tornado.websocket.WebSocketHandler):

    def open(self):
        pass

    def on_message(self, message):
        caseswitch = {"cu": self.connect,
                      "uu": self.UpdateUser, "cg": self.CreateGame}
        try:
            message = json.loads(message)
            if message["action"] in caseswitch.keys():
                caseswitch[message["action"]](*message["Arg"])
        except TypeError:
            print("Invalid Arguments")
        except json.decoder.JSONDecodeError:
            print("Invalid JSON string")

    def on_close(self):
        pass

    def connect(self, UserID):
        self.UserID = UserID
        pass

    def UpdateUser(self, UserName):
        pass

    def CreateGame(self, LengthofCode, Grade, NumberofColours, Broadcasttype, Team):
        pass


class GameWebsocket(tornado.websocket.WebSocketHandler):
    def open(self):
        pass

    def on_message(self, message):
        caseswitch = {"cu": self.connect,
                      "qg": self.Quit, "pg": self.Play, "gc": self.Colour}
        try:
            message = json.loads(message)
            if message["action"] in caseswitch.keys():
                caseswitch[message["action"]](*message["Arg"])
        except TypeError:
            print("Invalid Arguments")
        except json.decoder.JSONDecodeError:
            print("Invalid JSON string")

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


app = Start()
app.listen(80)
tornado.ioloop.IOLoop.current().start()
