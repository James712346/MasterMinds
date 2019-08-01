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
patch_tornado()


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

class WSMain(tornado.websocket.WebSocketHandler):
    def open(self):
        self.cooldown = time.time()

    def on_message(self, message):
        try:
            message = json.loads(message)
        except:
            self.write_message('{"action":"<action>", any other arguments}')
            print("Error:", message)
            return
        action = message["action"]
        if action == "Connected":
            print("User Successfully connected to WebSocket")
            self.id = message["ID"]
            MainClients.append(self)

        elif action == "sendtoall" and self.cooldown <= time.time():
            sendclient(MainClients, message["msg"])
            self.cooldown = time.time() + 5  # this makes sure that the user can't spam the line
        elif action == "updateUser" and self.cooldown <= time.time():
            if len(message["value"]) != 0:
                Users.update(
                    {message["key"]: message["value"]}, User.ID == self.id)
            print("?")
            self.cooldown = time.time() + 5  # this makes sure that the user can't spam the line

    def on_close(self):
        MainClients.remove(self)
        pass


class WSGame(tornado.websocket.WebSocketHandler):
    def open(self):
        self.cooldown = time.time()
        self.id = ""
        self.IP = self.request.remote_ip
        pass

    def on_message(self, message):
        try:
            message = json.loads(message)
        except:
            self.write_message('{"action":"<action>", any other arguments}')
            print("Error:", message)
            return
        action = message["action"]
        if action == "Connected":

            self.id = message["ID"]

            if "Pin" in message.keys():
                self.pin = message["Pin"]
                sendclient(GameClients[self.pin],
                           '{"action":"UserJoining","Username":""}')
                GameClients[self.pin].append(self)
                GameObjects[self.pin].UserJoin(self.id)
                sendmsg = '{"action":"Colour", "Colours": ' + str(
                    GameObjects[self.pin].SelectedColours) + ', "Colour": ' + str(GameObjects[self.pin].Colours) + '}'
                self.write_message(sendmsg.replace("'", '"'))
                if len(GameClients[self.pin]) == 1:
                    GameObjects[self.pin].Nextid()
                    self.write_message('{"action":"UrTurn"}')

        elif action == "Quit":
            sendclient(GameClients[self.pin], '{"action":"Quiting"}')
            GameObjects[self.pin].RemoveGame()
            pass

        elif action == "updateUser" and self.cooldown <= time.time():
            if len(message["value"]) != 0:
                Users.update(
                    {message["key"]: message["value"]}, User.ID == self.id)
            self.cooldown = time.time() + 5  # this makes sure that the user can't spam the line

        elif action == "create":
            print("Create")
            G = Game(ID=self.id, Col=int(message["col"]), Bro=self.IP if int(
                message["bro"]) else 0, size=int(message["size"]))
            if int(message["bro"]):
                if self.IP in Broadcasting.keys():
                    Broadcasting[self.IP].append(G)
                else:
                    Broadcasting[self.IP] = [G]
            GameObjects[G.Pin] = G
            GameClients[G.Pin] = []
            self.write_message('{"action":"redirect","pin":"' + G.Pin + '"}')

        elif action == "SubmitPlay":
            if self.id == GameObjects[self.pin].Nextid():
                print("Submiting Play for", self.id)
                sendclient(GameClients[self.pin], '{"action":"PlayResults","results":' + str(
                    GameObjects[self.pin].Play(self.id, message["code"].split(","))).replace("'", '"') + '}')
                GameClients[self.pin][[Client.id for Client in GameClients[self.pin]].index(
                    GameObjects[self.pin].Nextid())].write_message('{"action":"UrTurn"}')
                pass
            print("-----------------------------")

        elif action == "ColoursChange":
            GameObjects[self.pin].SelectedColours[message["index"]
                                                  ] = message["colour"]
            sendclient(GameClients[self.pin], str(
                message).replace("'", '"'), [self])
            # Game[self.pin]

    def on_close(self):
        try:
            GameObjects[self.pin].UserLeft(self.id)
            GameClients[self.pin].remove(self)
            GameClients[self.pin][[Client.id for Client in GameClients[self.pin]].index(
                GameObjects[self.pin].Nextid())].write_message('{"action":"UrTurn"}')
            pass
        except:
            pass

# Handlers


def Join(self):
    if not self.get_cookie("id"):
        id = ''.join([random.choice(string.ascii_letters + string.digits)
                      for n in range(1, 10)])
        while Users.search(User.ID == id):
            id = ''.join([random.choice(string.ascii_letters +
                                        string.digits) for n in range(1, 10)])
        self.set_cookie("id", id)
        Users.insert({"ID": id, "Creation": time.time(
        ), "Expiration": time.time() + UserExpiry, "Name": None, "Games": []})
    else:
        print("Logined in:", self.get_cookie("id"))
        Users.update({"Expiration": time.time() + UserExpiry},
                     User.ID == self.get_cookie("id"))


class HMain(tornado.web.RequestHandler):
    def get(self):
        print(self.get_cookie("id"))
        if not self.get_cookie("id"):
            id = ''.join([random.choice(string.ascii_letters +
                                        string.digits) for n in range(1, 10)])
            while Users.search(User.ID == id):
                id = ''.join(
                    [random.choice(string.ascii_letters + string.digits) for n in range(1, 10)])
            self.set_cookie("id", id)
            Users.insert({"ID": id, "Creation": time.time(
            ), "Expiration": time.time() + UserExpiry, "Name": None, "Games": []})
        else:
            print("Logined in:", self.get_cookie("id"))
            Users.update({"Expiration": time.time() + UserExpiry},
                         User.ID == self.get_cookie("id"))

        print(Users.get(User.ID == self.get_cookie("id"))["Name"])
        self.render("Templates/Start.html", Username=(Users.get(User.ID == self.get_cookie("id"))
                                                      ["Name"] if Users.get(User.ID == self.get_cookie("id"))["Name"] else ""))


class HJoin(tornado.web.RequestHandler):
    def get(self):
        if not self.get_cookie("id"):
            id = ''.join([random.choice(string.ascii_letters +
                                        string.digits) for n in range(1, 10)])
            while Users.search(User.ID == id):
                id = ''.join(
                    [random.choice(string.ascii_letters + string.digits) for n in range(1, 10)])
            self.set_cookie("id", id)
            Users.insert({"ID": id, "Creation": time.time(
            ), "Expiration": time.time() + UserExpiry, "Name": None, "Games": []})
        else:
            print("Logined in:", self.get_cookie("id"))
            Users.update({"Expiration": time.time() + UserExpiry},
                         User.ID == self.get_cookie("id"))

        self.render("Templates/Join.html", Username=Users.get(User.ID == self.get_cookie("id"))
                    ["Name"] if Users.get(User.ID == self.get_cookie("id"))["Name"] else "")


class HGame(tornado.web.RequestHandler):
    def get(self, GamePin):
        print("OOF")
        if not self.get_cookie("id"):
            id = ''.join([random.choice(string.ascii_letters +
                                        string.digits) for n in range(1, 10)])
            while Users.search(User.ID == id):
                id = ''.join(
                    [random.choice(string.ascii_letters + string.digits) for n in range(1, 10)])
            self.set_cookie("id", id)
            Users.insert({"ID": id, "Creation": time.time(
            ), "Expiration": time.time() + UserExpiry, "Name": None, "Games": []})
        else:
            print("Logined in:", self.get_cookie("id"))
            Users.update({"Expiration": time.time() + UserExpiry},
                         User.ID == self.get_cookie("id"))

        if Games.search(User.Pin == GamePin):
            print("User", self.get_cookie("id"), "Signed into", GamePin)
            self.render("Templates/Game.html", Colours=GameObjects[GamePin].SelectedColours, Turns=[
                        Turn for Turn in GameObjects[GamePin].Turns if Turn != []][::-1])
        elif GamePin in GameOjects.keys():
            pass
        else:
            print("User", self.get_cookie("id"),
                  "failed to connect to", GamePin)
            self.redirect("/Join?Pin=" + GamePin)
            return

    def post(self, GamePin):
        GameObjects[GamePin].syncDB()


class HCreateGame(tornado.web.RequestHandler):
    def get(self):
        if not self.get_cookie("id"):
            id = ''.join([random.choice(string.ascii_letters +
                                        string.digits) for n in range(1, 10)])
            while Users.search(User.ID == id):
                id = ''.join(
                    [random.choice(string.ascii_letters + string.digits) for n in range(1, 10)])
            self.set_cookie("id", id)
            Users.insert({"ID": id, "Creation": time.time(
            ), "Expiration": time.time() + UserExpiry, "Name": None, "Games": []})
        else:
            print("Logined in:", self.get_cookie("id"))
            Users.update({"Expiration": time.time() + UserExpiry},
                         User.ID == self.get_cookie("id"))

        self.render("Templates/CreateGame.html", Username=Users.get(User.ID == self.get_cookie("id"))
                    ["Name"] if Users.get(User.ID == self.get_cookie("id"))["Name"] else "")


class Exit(tornado.web.RequestHandler):
    def get(self):
        tornado.ioloop.IOLoop.current().stop()


class Game():
    def __init__(self, Pin=False, ID="SUDO", Sel=0, Bro=0, Col=4, size=4, Users=[], Turns=[], Code=None):
        self.Pin = Pin
        self.Creator = ID
        self.Selection = Sel
        self.Broadcast = Bro
        self.Owner = [ID, None]  # Master, Temperary
        self.Colours = Colours[:Col]
        self.Users = Users
        self.Turns = Turns
        if not Code:
            if not Sel:
                # if sel is 0 then choice a random list of colours
                self.Code = [random.choice(self.Colours)
                             for i in range(0, size)]
                self.Users.append(ID)
            elif Sel == 1:
                self.Code = [None] * int(size)
                self.Selector = None
                self.Users.append(ID)
            else:
                self.Code = [None] * int(size)
        else:
            self.Code = Games.get(User.Pin == self.Pin)["Code"]
        self.SelectedColours = Colours[:len(self.Code)]
        if not (self.Pin or ID == "SUDO"):
            self.Pin = ''.join(
                [random.choice(string.ascii_letters + string.digits) for n in range(0, 5)])
            while Games.search(User.Pin == self.Pin):
                self.Pin = ''.join(
                    [random.choice(string.ascii_letters + string.digits) for n in range(0, 5)])

    def syncDB(self, UpdExpiry=False, RootRequest=False):
        if Games.search(User.Pin == self.Pin):
            if UpdExpiry:
                Games.update({"Expiration": time.time() +
                              GameExpiry}, User.Pin == self.Pin)
            Games.update({"Owner": self.Owner, "Selection": self.Selection, "Code": self.Code, "Broadcast": self.Broadcast, "Users": self.Users, "Turns": [
                         turn for turn in self.Turns if turn != []], "Colours": len(self.Colours)}, User.Pin == self.Pin)
        elif RootRequest:
            Games.insert({"Pin": self.Pin, "Owner": self.Owner, "Selection": self.Selection, "Code": self.Code, "Broadcast": self.Broadcast, "Users": self.Users,
                          "Expiration": time.time() + GameExpiry, "Turns": [turn for turn in self.Turns if turn != []], "Colours": len(self.Colours)})

    def UserLeft(self, User):
        if self.Owner[0] == User:
            self.Owner[1] = "NexttoJoin" if len(
                GameObjects[self.pin]) == 0 else random.choice(GameObjects[self.pin]).id
        self.syncDB()

    def UserJoin(self, User):
        print("Join")
        if self.Owner[0] == User:
            self.Owner[1] = None
        elif self.Owner[1] == "NexttoJoin":
            self.Owner[1] = User
        print(User, self.Users)
        if User not in self.Users:
            self.Users.append(User)
            print("ADded user")
        self.syncDB(True)

    def Restart(self):
        self.Users = []
        self.Turns = []
        if not self.Selection:
            # if sel is 0 then choice a random list of colours
            self.Code = [random.choice(self.Colours)
                         for i in range(0, len(self.Code))]
        elif self.Selection == 1:
            self.Code = [None] * int(size)
            self.Selector = None
        else:
            self.Code = [None] * int(size)
        db.remove(where('Pin') == self.Pin)

    def RemoveGame(self):
        # delete from DB and Dict
        pass

    def Nextid(self):
        while True:
            if self.Users[len(self.Turns) - int(len(self.Turns) / len(self.Users)) * len(self.Users)] in [Client.id for Client in GameClients[self.Pin]]:
                return self.Users[len(self.Turns) - int(len(self.Turns) / len(self.Users)) * len(self.Users)]
                break
            elif len(GameClients[self.Pin]) == 0:
                return "Unknown"
            else:
                self.Turns.append([])
                self.syncDB()

    def Play(self, User, Code):
        if len(Code) != len(self.Code):
            return False
        Turn = [User, Code, 0, 0]
        RightCode = self.Code[:]
        print(RightCode)

        for i in range(0, (len(Code))):
            if RightCode[i].lower() == Code[i]:
                if Code[i] not in RightCode:
                    Turn[2] -= 1
                    print("OOF")
                elif Code[i].isupper():
                    RightCode[RightCode.index(Code[i])] = Code[i].upper()
                Turn[3] += 1
                RightCode[i] = None
            elif Code[i] in RightCode:
                Turn[2] += 1
                RightCode[RightCode.index(Code[i])] = Code[i].upper()
        print(RightCode)
        print(Code)
        self.Turns.append(Turn)
        self.syncDB()
        return Turn


def make_app():
    return tornado.web.Application([
        (r"/", HMain),
        (r"/stop", Exit),
        (r"/Join", HJoin),
        (r"/ws", WSMain),
        (r"/Game/ws", WSGame),
        (r"/Game/Create", HCreateGame),
        (r"/Game/([^/]+)", HGame),
        (r'/Static/(.*)', tornado.web.StaticFileHandler, {'path': "Static/"})

    ], cookie_secret="qwrQzP8pyuykv7PGjReAmANxtLtAHz95")
