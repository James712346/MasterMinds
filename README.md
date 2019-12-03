# < MasterMind.io >

![](https://img.shields.io/badge/MasterMind.io-0.0.1-brightgreen)![](https://img.shields.io/badge/Python-3.7.4-brightgreen)![](https://img.shields.io/badge/Tornado-6.0.3-brightgreen)![](https://img.shields.io/badge/TinyDB-3.13-brightgreen)

MasterMind.io is a Game Webserver that can be ran on a schools network where students can connect to the website and play with friends. MasterMind is a game in which students can use to improve thier problem-solving skills.

## Features

- Mutiable users are allowed to play the same game
- Realtime Updates between users
- Easy to setup
- Cheat Free
- Debugging Mode

## Installation
Install python 3.7 at https://www.python.org/downloads/
Then by using pip You need to install TinyDB, Tornado

`python -m pip install tornado`

`python -m pip install tinydb`

Once that is install then you should download the src folder in this github repository and save it to a easy directory that you can reach in a command prompt

## Usage
Open a command prompt in the same directory as the src folder and type to start the webserver
`python webserver.py`

To place the webserver under debugging mode use this command instead
`python webserver.py -d` or `python webserver.py --debug`

To change the Port of the webserver user the command
`python webserver.py -p 80` or `python webserver.py --port 80`

## Game Play
### Setting up or Joining a Game
To create a Game, click new game, select your grade level or use custom setting by choices custom as your grade level. After choosing a grade level you will need to set a username, or you will not be able to create a game

To Join a game, you must provide a Game Pin found in the top left of your teacher’s or friends window, and you must also provide a username, or you will not be able to join the Game.

### When Playing
When you first Join you may not be your turn, so wait until you see arrows appear and a send button

You can use these arrows to roll through different colours or use the keyboard shortcuts where use the key “q” for the first box to change the colour in a positive direction or use the “a” key to change the colour in a negative direction. This pattern is continued along the keyboard with the next colour being
`w = +` `s = -`  & `e = +` `d = -` & etc

To submit your answer, click the send button or press the enter key on your keyboard

You submitted answer will then appear under the Attempts title with Black Number being the number of colours in the right place and the White Number being the number of colours that found but not in the right place
