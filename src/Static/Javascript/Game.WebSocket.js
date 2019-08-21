var Pin = url.href.split("/").slice(-1)[0]
var GConnectInter;

function Connect(){
  Gamews = new WebSocket("ws://"+window.location.host+"/G/ws");
  Gamews.onopen = function() {
     GSendCommand("cu", getCookie("id"), Pin);
     $(".se-pre-con").fadeOut("slow");
     clearTimeout(GConnectInter);
     HideControls();
  };

  Gamews.onmessage = function (evt) {
    var message = JSON.parse(evt.data)
    switch (message["action"]){
      case "sa":
        console.log("Action Successfully");
        break;
      case "fa":
        console.log("Action Failed")
      case "gc":
        $(".C")[message["Arg"][0]].children[1].style.backgroundColor = message["Arg"][1];
        break;
      case "qg":
        console.log("Quiting")
        break;
      case "pr":
        AddCode(...message["Arg"]);
        break;
      case "nt":
        NextTurn(...message["Arg"]);
        break;
      default:
        console.log("Unknown Action")
    }
  };

  Gamews.onclose = function(){
    console.log("Game Websocket closed");
    GConnectInter = setTimeout(function(){Connect();},5000);
    console.log("Reconnecting at 5000 intervals")
    Loading();
  }
};

$(".C button").click(function(){
      var Index = Colours.indexOf($(this)[0].parentElement.children[1].style.backgroundColor)
      var Index = Index != -1 ? Index : 0

      console.log(Index)
      if ($(this)[0].name == "UP"){
       $(this)[0].parentElement.children[1].style.backgroundColor = Colours[(Index != Colours.length-1) ? Index+1 : 0];
      }
      else{
       $(this)[0].parentElement.children[1].style.backgroundColor = Colours[(Index != 0) ? Index-1 : Colours.length-1];
      }
      GSendCommand("cc", $(".C").index($(this)[0].parentElement), $(this)[0].parentElement.children[1].style.backgroundColor)
})

function AddCode(UserID, RC, code, RP){
  var HtmlScript = '<div class="row"> <div class="Number text-right">'+RC+'</div>'
  for (i = 0; i < code.length; i++){
    HtmlScript+= '<div class="col RC" style="background-color: '+code[i]+'"></div>'
  }
  HtmlScript+='<div class="Number text-left">'+RP+'</div></div> '
  $("#Results").prepend(HtmlScript)
}

$("#GameForm").submit(function(event){
    event.preventDefault();
    HideControls()
    var code = [];
    for (i = 0; i < $(".C").length; i++) {
      code.push($(".C")[i].children[1].style.backgroundColor);
    };
    GSendCommand("pg", Pin, code);
})

function GSendCommand(action, ...Args){
  var string = "";
  for (i = 0; i < Args.length; i++){
    string = string + '"' + Args[i] + '",';
  }
  Gamews.send('{"action":"'+action+'", "Arg":['+string.slice(0, -1)+']}')
}
function HideControls(){
  $("#GameForm button").hide();
  $("#GameForm h4").show();
  $("#GameForm .C .Box").css("height","60%");
  $("#GameForm .C .Box").css("padding","20% 0");
}
function NextTurn(UserID){
  if (UserID == getCookie("id")){$("#GameForm button").show();
  $("#GameForm h4").hide();
  $("#GameForm .C .Box").css("height","33%");
  $("#GameForm .C .Box").css("padding","0");}else{
    console.log(UserID)
  }

}
Connect()
