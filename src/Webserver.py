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
import re
#import all the librarys used in for this program

def Debug(*input):
    if "-d" in sys.argv[1:] or "--degug" in sys.argv[1:]: #if there is an argument of -d or --degug it will print any thing that is parsed to this function
        if len(input) > 0: # this is if input is bigger than 0 or it won't print anything
            print("# DEBUG: ", *input) #print "# DEBUG: " infront of the input value
        return True #returning true that it is in debugging mode
    return False #returning false that it isn't in debugging mode


def Connected(self):
    if (not self.get_cookie("id")) or MM.UserTB.search(MM.query.UserID == self.get_cookie("id")) == []: #if the Client doesn't have a set cookie of id or that id isn't in the DataBase
        Id = MM.CreateUniqID(6) #then it creates a Uniq ID that 6 charaters long
        self.set_cookie("id", Id) #sets the new Uniq ID to a cookie called id
        MM.UserTB.insert({"UserID": Id, "LastLogin": time.time(
        ), "UserName": None, "Wins": None}) #and adds the User (client) to the database
        Debug("Added New User:", Id)
        return Id #returning the UniqID
    MM.UserTB.update({"LastLogin": time.time()},
                     MM.query.UserID == self.get_cookie("id")) #or it will update the last time the user login
    return self.get_cookie("id") #returning the id


class Home(tornado.web.RequestHandler):
    def get(self):
        Id = Connected(self) #calls the Connect function above
        Debug("User", self.get_cookie("id"), "Joins the 'Home Page'")
        Debug(MM.UserTB.get(MM.query.UserID == self.get_cookie("id")))
        self.render("Templates/Form.html", OwnedGames=list(MM.GameTB.search(MM.query.Creator == Id)), Form='Home',
                    Username=MM.UserTB.get(MM.query.UserID == Id)["UserName"] if MM.UserTB.get(MM.query.UserID == Id)["UserName"] else "") #renders the form page with the form type of home and username to the users ID collected from the Database (it empty if there isn't a set username)


class JoinGame(tornado.web.RequestHandler):
    def get(self):
        Id = Connected(self) #calls the Connect function above
        Debug("User", Id, "Joins the 'Join Game Page'")
        self.render("Templates/Form.html", Form='Join', Username=MM.UserTB.get(MM.query.UserID ==
                                                                               Id)["UserName"] if MM.UserTB.get(MM.query.UserID == Id)["UserName"] else "")#renders the form page with the form type of Join and username to the users ID collected from the Database (it empty if there isn't a set username)


class CreateGame(tornado.web.RequestHandler):
    def get(self):
        Id = Connected(self) #calls the Connect function above
        Debug("User", self.get_cookie("id"), "Joins the 'Create Game Page'")
        self.render("Templates/Form.html", Form='Create', Username=MM.UserTB.get(MM.query.UserID ==
                                                                                 Id)["UserName"] if MM.UserTB.get(MM.query.UserID == Id)["UserName"] else "")#renders the form page with the form type of create and username to the users ID collected from the Database (it empty if there isn't a set username)


class Game(tornado.web.RequestHandler):
    def get(self, GamePin):
        GamePin = re.sub('[\W_]+', '', GamePin) #removes any forgin charaters that will not be in a valid GamePin
        GameValues = MM.GameTB.search(MM.query.GamePin == GamePin) #searchs for that GamePin in the database (which should only send 1 item in a list)
        if not GameValues: # if the GameValues is empty then
            self.redirect("/Join?Pin=" + GamePin) #redirect teh user to the join page
        if (not (self.get_cookie("id") or MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))["UserName"])) or MM.UserTB.get(MM.query.UserID == self.get_cookie("id")) == []: #if the user has no UserName or setup ID then the user is sent back to the join page where they are force to make one
            Debug("IDless/UserNameless tryed to join Game <:> User sent back to the /join")
            # Sends the MM.query to back to the join page due to the MM.query not have a id or username
            self.redirect("/Join?UserName") #redirect the user to the join page
        else:
            GameValues = GameValues[0] #This 0 index of the GameValues is selected as there should only be one GamePin in the database
            Debug("User", self.get_cookie("id"),
                  "Sign into Game:", GamePin)
            Code = GameValues["Code"] if Debug() else [] #checks to see if the user is in debugging mode, if so then it will let the user view the answer
            if GameValues["Playing"]: #If the game is in a playing state and not on waiting page then
                bw = "true" if GameValues["Team"] or "-lb" in sys.argv[1:
                                                                       ] or "--low_bandwidth" in sys.argv[1:] else "false" #check if the game is in solo mode or the program is in low bandwith mode to limit the request from to the webserver
                self.render("Templates/Game.html", Lowbandwidth=bw, Username=MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))[
                            "UserName"], Colours=MM.GetObject(GamePin).liveInput, Turns=MM.GetObject(GamePin).Turns(self.get_cookie("id"))[::-1], Code=Code, AvailableColours=MM.GameTB.search(MM.query.GamePin == GamePin)[0]["AvailableColours"], GamePin=GamePin) #render the Game.html template with all the need arguments
                return
            self.render("Templates/Waiting.html", UsersConnected=MM.GetObject(GamePin).GetUsers()[1:], Username=MM.UserTB.get(
                MM.query.UserID == self.get_cookie("id"))["UserName"] if MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))["UserName"] else "") #else render the waiting page instead of the game template

    def post(self, GamePin): #if a user click the starts button
        GameValues = MM.GameTB.search(MM.query.GamePin == GamePin) #check if the game still exists
        if GameValues: #if so
            GamePin = re.sub('[\W_]+', '', GamePin) #remove any forgin charaters
            MM.GameTB.update({"Playing": True}, MM.query.GamePin == GamePin) #update the database say that the game is now in a playing state
            [SendCommand(user, "rd", "/g/" + GamePin)
             for user in MM.GetObject(GamePin).GetWebSockets()] #redirect all the users that are connected to this GamePin
            Code = MM.GameTB.search(MM.query.GamePin == GamePin)[
                0]["Code"] if Debug() else [] #checks to see if the user is in debugging mode, if so then it will let the user view the answer
            Debug("Game has Started")
            bw = "true" if MM.GameTB.get(MM.query.GamePin == GamePin)[
                "Team"] or "-lb" in sys.argv[1:] or "--low_bandwidth" in sys.argv[1:] else "false" #check if the game is in solo mode or the program is in low bandwith mode to limit the request from to the webserver
            self.render("Templates/Game.html", Lowbandwidth=bw, Username=MM.UserTB.get(MM.query.UserID == self.get_cookie("id"))
                        ["UserName"], Colours=MM.GetObject(GamePin).liveInput, Turns=MM.GetObject(GamePin).Turns(self.get_cookie("id"))[::-1], Code=Code, AvailableColours=MM.GameTB.search(MM.query.GamePin == GamePin)[0]["AvailableColours"], GamePin=GamePin) #render the Game.html template with all the need arguments
        else:
            self.redirect("/Join?Pin=" + GamePin) #else it will send the user to the join page


class MainWebsocket(tornado.websocket.WebSocketHandler): #This WebSocket is for all the form pages that have no gameplay

    def on_message(self, message): #when the websocket Receives a message it will
        Debug("Received Main WebSocket:", message)
        caseswitch = {"cu": self.connect,
                      "uu": self.UpdateUser, "cg": self.CreateGame, "rg": self.RemoveGame}
        try:
            message = json.loads(message) #Turn it into a json variable (dictornary)
            if message["action"] in caseswitch.keys(): #check if the action is in the caseswitch dictornary's keys
                if caseswitch[message["action"]](*message["Arg"]): #runns the function that is indexed by the action
                    SendCommand(self, "sa") #if the function was Successfully it will return the message as Successfully
                    return
        except TypeError:
            print("Invalid Arguments") #print in console that there was an invalid argument that the client didn't send
        except json.decoder.JSONDecodeError:
            print("Invalid JSON string") #prints in the console that the json parsing was incorrect
        SendCommand(self, "fa") #sends a message to the client telling it that the action failed


    def connect(self, UserID):
        if self.get_cookie("id") == UserID: #checks if the userID matches the users cookie
            self.UserID = UserID #set the UserID to the class
            return True
        else: #if so then it an invalid client
            self.close()

    def UpdateUser(self, UserName):
        Debug("Added a UserName of", UserName, "to", self.UserID)
        MM.UserTB.update({"UserName": UserName},
                         MM.query.UserID == self.UserID) #add the new username set by the user to the database

    def CreateGame(self, *Arg):
        Game = MM.GameEngine().CreateGame(self.UserID, *Arg) #create the game with the argument sent in the message
        if Game:
            SendCommand(self, "rd", "/G/" + Game.GamePin) #redirects the user to the game if it was Successfully made
        return Game

    def RemoveGame(self, GamePin):
        return MM.GetObject(GamePin).delete(self.UserID) #removes the game from the DataBase


class GameWebsocket(tornado.websocket.WebSocketHandler):
    def on_message(self, message): #when the websocket Receives a message it will
        Debug("Received Game WebSocket:", message)
        caseswitch = {"cu": self.connect,
                 "pg": self.Play, "uu": self.UpdateUser, "cc": self.Colour}
        try:
            message = json.loads(message) #Turn it into a json variable (dictornary)
            if message["action"] in caseswitch.keys(): #check if the action is in the caseswitch dictornary's keys
                if caseswitch[message["action"]](*message["Arg"]): #runns the function that is indexed by the action
                    SendCommand(self, "sa") #if the function was Successfully it will return the message as Successfully
                    return
        except TypeError:
            print("Invalid Arguments") #print in console that there was an invalid argument that the client didn't send
        except json.decoder.JSONDecodeError:
            print("Invalid JSON string") #prints in the console that the json parsing was incorrect
        SendCommand(self, "fa") #sends a message to the client telling it that the action failed

    def on_close(self):
        Debug("User", self.get_cookie("id"), "disconnected") #if the user Disconnects
        try:
            MM.GetObject(self.GamePin).RemoveUser(self.UserID) #remove the user from the GameObject
            if MM.GetObject(self.GamePin).PlayerPlaying == self.UserID: #if its the users go and he leaves
                MM.GetObject(self.GamePin).NextTurn() #it will find a new player to continue the game
                [SendCommand(ws, "nt", MM.GetObject(self.GamePin).PlayerPlaying)
                 for ws in MM.GetObject(self.GamePin).GetWebSockets()] #and send the message to all the clients that is connected to the same gamePin
        except:
            pass

    def UpdateUser(self, UserName):
        Debug("Added a UserName of", UserName, "to", self.UserID)
        MM.UserTB.update({"UserName": UserName},
                         MM.query.UserID == self.UserID)  #add the new username set by the user to the database

    def connect(self, UserID, GamePin): #if the user send "cu"
        GamePin = re.sub('[\W_]+', '', GamePin) #removes any forgin charaters from the sent gamePin
        Debug(UserID,"Connected")
        if self.get_cookie("id") == UserID: #checks if the userID sent matches the id in the clients cookies
            self.UserID = self.get_cookie("id") #set the UserID to a class variable
            self.GamePin = GamePin #also sets the gamepin to a class variable
            Debug(MM.GetObject(GamePin))
            MM.GetObject(self.GamePin).AddUser(self.get_cookie("id"), self) #add the userid to the GameObject
            Debug(MM.GetObject(self.GamePin).WS)
            if MM.GetObject(self.GamePin).PlayerPlaying == None: #if this is the first user to connect then the turn cycle will start with them
                MM.GetObject(
                    self.GamePin).PlayerPlaying = self.get_cookie("id")
                [SendCommand(ws, "nt", self.get_cookie("id"))
                 for ws in MM.GetObject(self.GamePin).GetWebSockets()]
        else:
            self.close()

    def Play(self, Code):
        results = MM.GetObject(self.GamePin).Play(self.UserID, Code.split(",")) #When the play submits a code the webserver will send it to the Play function in the GameObject that will return the User's ID, black colours, code and white colours
        if results[1] != len(results[2]): #if the black colour is not equal to the len of the code it send a message to all the client of the new code found with its results and the next users turn
            [SendCommand(ws,"pr",*results) for ws in MM.GetObject(self.GamePin).GetWebSockets()]
            [SendCommand(ws, "nt", MM.GetObject(self.GamePin).PlayerPlaying) for ws in MM.GetObject(self.GamePin).GetWebSockets()]
        else: #else if it is the length of the code then it is counted as a win removing any trace of the game from the database and sending a command on who won and the final finishing code (also the number of turn until the code was worked out)
            Turns = MM.GetObject(self.GamePin).Turns(self.get_cookie("id"))
            [SendCommand(ws,"W",len(Turns),MM.UserTB.get(MM.query.UserID == self.UserID)["UserName"],*results) for ws in MM.GetObject(self.GamePin).GetWebSockets()]
            [ws.close() for ws in MM.GetObject(self.GamePin).GetWebSockets()]
            MM.GetObject(self.GamePin).delete()

    def Colour(self, Index, Colour):
        if self.UserID == MM.GetObject(self.GamePin).PlayerPlaying: #make sure that the it the users go before changing the colours on everyones screens
            Index = int(Index) #turns the Index from a string to an interger
            MM.GetObject(self.GamePin).liveInput[Index] = Colour #updates the colour in the index of index on the GameObject's liveInput variable
            [SendCommand(ws,"cc", Index, Colour) for ws in MM.GetObject(
                self.GamePin).GetWebSockets(self.UserID)] #sends it updated value to all the players


def SendCommand(self, action, *Arg):
    Debug("Sending", '{"action":"' + action +
          '","Arg":' + str(list(Arg)).replace("'", '"') + '}')
    try:
        self.write_message(
            ('{"action":"' + action + '","Arg":' + str(list(Arg)).replace("'", '"') + '}')) #converts all the items into a json string
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
        (r'/Static/(.*)', tornado.web.StaticFileHandler, {'path': "Static/"}), #sets up all the paths that may be used
        (r"/(.*)", Home) #any unknown paths will be sent to the main page (Home page )

    ]) #there was a cookie_secret of "qwrQzP8pyuykv7PGjReAmANxtLtAHz95" but i found it uneeded as I was not using any secure cookies as its not needed


if __name__ == "__main__":
    argument = None
    Options = {}
    for i in sys.argv[1:]:
        if "-" in i or "--" in i:
            argument = i
        else:
            Options[argument] = i

    if "-p" in Options.keys():
        port = Options["-p"] #set the port to the -p value
    elif "--port" in Options.keys():
        port = Options["--port"] #set the port to the --port value
    else:
        port = 80 #if no port was set then it will default to 80

    Debug("You are in Debugging Mode")
    print("Starting Webserver on port", port) #tells the user what port that the server will be starting on
    app = Start() #calls the starting function
    app.listen(port) #set the port of the webserver
    tornado.ioloop.IOLoop.current().start() #starts the webserver's loop
