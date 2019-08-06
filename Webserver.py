import tornado.ioloop
import time
import random
import string
import json
from tornado.util import _websocket_mask
import tornado.websocket
import tornado.web
from pyjade.ext.tornado import patch_tornado
from tornado import template
from tinydb import TinyDB, Query
import MasterMinds
patch_tornado()


DB = TinyDB('Database.json')
UserTB = DB.table("UserID")
GameTB = DB.table("GamesPins")
TurnTB = DB.table("Turns")
query = Query()



class Home(tornado.web.RequestHandler):
    def get(self):
        print("Join")
        if not self.get_cookie("id"):
            self.set_cookie("id", MasterMinds.CreateUniqID())
            UserTB.insert({"UserID": self.get_cookie("id"), "LastLogin": time.time(), "UserName": None, "Games": None, "Wins": None})
        else:
            UserTB.update({"LastLogin": time.time() }, query.UserID == self.get_cookie("id"))
        self.render("Templates/Home.html")

class JoinGame(tornado.web.RequestHandler):
    def get(self):
        if not self.get_cookie("id"):
            self.set_cookie("id", MasterMinds.CreateUniqID())
            UserTB.insert({"UserID": self.get_cookie("id"), "LastLogin": time.time(), "UserName": None, "Games": None, "Wins": None})
        else:
            UserTB.update({"LastLogin": time.time() }, query.UserID == self.get_cookie("id"))
        self.render()

class CreateGame(tornado.web.RequestHandler):
    def get(self):
        if not self.get_cookie("id"):
            self.set_cookie("id", MasterMinds.CreateUniqID())
            UserTB.insert({"UserID": self.get_cookie("id"), "LastLogin": time.time(), "UserName": None, "Games": None, "Wins": None})
        else:
            UserTB.update({"LastLogin": time.time() }, query.UserID == self.get_cookie("id"))
        self.render()

class Game(tornado.web.RequestHandler):
    def get(self, GamePin):
        if not GameTB.search(query.GamePin == GamePin):
            self.redirect("/Join?Pin=" + GamePin)
        if not self.get_cookie("id"):
            self.set_cookie("id", MasterMinds.CreateUniqID())
            UserTB.insert({"UserID": self.get_cookie("id"), "LastLogin": time.time(), "UserName": None, "Games": None, "Wins": None})
            self.redirect("/Join") #Sends the query to back to the join page due to the query not have a id or username
        else:
            UserTB.update({"LastLogin": time.time() }, query.UserID == self.get_cookie("id"))
            if not UserTB.get(query.UserID == self.get_cookie("id"))["UserName"]:
                self.redirect("/Join") #Send the query to back to the join page due to the query not have a username
            else:
                if Game.get(query.ID == self.get_cookie("id"))["UserName"]:
                    pass
                self.render("/Templates/Game.html")

class MainWebsocket(tornado.websocket.WebSocketHandler):
    def open(self):
        pass
    def on_message(self, message):
        pass
    def on_close(self):
        pass

class GameWebsocket(tornado.websocket.WebSocketHandler):
    def open(self):
        pass
    def on_message(self, message):
        pass
    def on_close(self):
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
