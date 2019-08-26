var ws;
var Pin = url.href.split("/").slice(-1)[0];
var ConnectInter;
var KeyboardShortcuts;
var KeyEvents = new Map();
var GameEnd = false;
//Setting up all the variables in the javascript file
$(".winningdiv").hide(); //Hiding the Winning div
HideControls(); //Make sure that it hides the control since it doesn't know whos go it is

if (!getCookie("KeyboardShortcuts")) { //if there isn't a KeyboardShortcuts cookie it will create a new one
  document.cookie = 'KeyboardShortcuts=["q", "a", "w", "s", "e", "d", "r", "f", "t", "g", "y", "h"]'; // I added this for future update, when i add a settings page to change the KeyboardShortcuts
}
KeyboardShortcuts = JSON.parse(getCookie("KeyboardShortcuts")); //Converts the cookie which is a string into json formate

for (i = 0; i < $(".C button").length; i++) {
  KeyEvents.set(KeyboardShortcuts[i],$(".C button")[i]) //loops through all the code buttons $(".C button") in the html file and adds it to a collection with the key of the button the same indexed value in KeyboardShortcuts
}
window.addEventListener('keydown', function(e) {//we setup a keydown event when the user press a key it will run this function
  if (e.isComposing || e.keyCode === 229) {
    return;
  } else if (KeyEvents.has(e.key)) {
    KeyEvents.get(e.key).click(); //If the key is in the KeyEvents collection then it will call it which is the button and simulate a click
  } else if (e.key == "Enter"){
    $("#GameForm").submit(); //If the key is enter then it calls the submit function on the GameForm
  }
}, true);
function Connect() {
  ws = new WebSocket("ws://" + window.location.host + "/G/ws");//this sets up the WebSocket which lets js talk to the python webserver
  ws.onopen = function() {
    SendCommand("cu", getCookie("id"), Pin); // It sends a command to the ws telling it that it has connect and sends the Gamepin and UserID
    $(".se-pre-con").fadeOut("slow"); //this fadeout will remove the loading sign show that the website is ready to be used
    clearTimeout(ConnectInter); //if there is a Timeout set from js trying to reconnect to the websocket it will remove the timeout so it doesn't continue to try and reconnect to it

  };

  ws.onmessage = function(evt) {
    var message = JSON.parse(evt.data) //converts the stringed data to json formate that can be properly indexed
    switch (message["action"]) { //a switch command that find the action in which the webserver want js to do
      case "sa":
        console.log("Action Successfully"); //If the command that js sent was Successfully the webserver will submit this action to js and js will log the Successfully action
        break;
      case "fa":
        console.error("Action Failed") //If the command that js sent wasn't Successfully the webserver will submit this action to js and js will throw an error to the console
        break
      case "cc":
        $(".C")[message["Arg"][0]].children[1].style.backgroundColor = message["Arg"][1]; //this changes the colour of the boxes so that everyone is in sync
        break;
      case "pr":
        AddCode(...message["Arg"]); //When a user submits a code this will send the results that the python webserver as made to a function which will preappend it to Attempts div
        break;
      case "nt":
        NextTurn(...message["Arg"]); //this tells the client side (js) whos go it is
        break;
      case "W":
        GameOver(...message["Arg"]); //this is when someone wins and the game is over
        break;
      default:
        console.warn("Unknown Action") // if all the case for the actions had failed it will warn the user
    }
  };

  ws.onclose = function() {
    console.log("Game Websocket closed"); //If the websocket is close (disconnected) then the client (js) will log this
    if (!GameEnd){ // if the game as ended then it will not continue but if it did
    ConnectInter = setTimeout(function() {  //it will setup a timeout for every 5000ms it will try and reconnect to the server
      Connect();
      console.warn("Reconnecting at 5000 intervals")
      Loading(); //while it trys to reconnect it will show a loading gif that intcates to the user that they have losed connection with the webserver
    }, 5000);}


  }
};

function GameOver(turns, User, UserID, RC, code, RP){
  GameEnd = true;
  var HtmlScript = '<div class="row"> <div class="Number text-right BlackResults">' + RC + '</div>'
  for (i = 0; i < code.length; i++) {
    HtmlScript += '<div class="col RC" style="background-color: ' + code[i] + '"></div>'
  }
  HtmlScript += '<div class="Number text-left WhiteResults">' + RP + '</div></div> '
  $(".WinningCode").append(HtmlScript)
  $(".player").prepend(User)
  $(".turns").prepend(turns+" ")
  $(".Game").hide();
  $(".winningdiv").show();
}

$(".C button").click(function() {
  var Index = Colours.indexOf($(this)[0].parentElement.children[1].style.backgroundColor)
  var Index = Index != -1 ? Index : 0

  console.log(Index)
  if ($(this)[0].name == "UP") {
    $(this)[0].parentElement.children[1].style.backgroundColor = Colours[(Index != Colours.length - 1) ? Index + 1 : 0];
  } else {
    $(this)[0].parentElement.children[1].style.backgroundColor = Colours[(Index != 0) ? Index - 1 : Colours.length - 1];
  }
  if (Team) {
    SendCommand("cc", $(".C").index($(this)[0].parentElement), $(this)[0].parentElement.children[1].style.backgroundColor)
  }
})

$("#UserForm").submit(function(event) {
  SendCommand("uu", $("#UserName").val())
  event.preventDefault();
});

function AddCode(UserID, RC, code, RP) {
  var HtmlScript = '<div class="row"> <div class="Number text-right BlackResults">' + RC + '</div>'
  for (i = 0; i < code.length; i++) {
    HtmlScript += '<div class="col RC" style="background-color: ' + code[i] + '"></div>'
  }
  HtmlScript += '<div class="Number text-left WhiteResults">' + RP + '</div></div> '
  $("#codes").prepend(HtmlScript)
}

$("#GameForm").submit(function(event) {
  event.preventDefault();
  HideControls()
  var code = [];
  for (i = 0; i < $(".C").length; i++) {
    code.push($(".C")[i].children[1].style.backgroundColor);
  };
  SendCommand("pg", code);
})

function SendCommand(action, ...Args) {
  var string = "";
  for (i = 0; i < Args.length; i++) {
    string = string + '"' + Args[i] + '",';
  }
  ws.send('{"action":"' + action + '", "Arg":[' + string.slice(0, -1) + ']}')
}

function HideControls() {
  $("#GameForm button").hide();
  $("#GameForm h4").show();
  $("#GameForm .C .Box").css("height", "60%");
  $("#GameForm .C .Box").css("padding", "20% 0");
}

function NextTurn(UserID) {
  if (UserID == getCookie("id")) {
    $("#GameForm button").show();
    $("#GameForm h4").hide();
    $("#GameForm .C .Box").css("height", "33%");
    $("#GameForm .C .Box").css("padding", "0");
  } else {
    console.log(UserID)
  }

}
Connect()
