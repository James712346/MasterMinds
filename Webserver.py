import tornado.ioloop, time, random, string, json
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

    ],cookie_secret = "qwrQzP8pyuykv7PGjReAmANxtLtAHz95")
