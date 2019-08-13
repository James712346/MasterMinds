var ws;
function Connect(){
  ws = new WebSocket("ws://"+window.location.host+"/ws");
  if (!("GameGamews" in window)){
    ws.onopen = function() {
      SendCommand("cu", getCookie("id"))
      $(".se-pre-con").fadeOut("slow");
    };
  }

  ws.onmessage = function(evt) {
    var message = JSON.parse(evt.data)
    var action = message["action"]
    if ("Failed" != action) {
      var message = JSON.parse(evt.data)
      if (action == "uu") { //Users Username
        $("#UserName").val(message["val"]);
      } else if (action == "rd") { //Redirect
        window.location = "/Game/" + message["pin"];
      };
    } else {
      console.error("Action Failed")
    }
  };
  ws.onclose = function(){
    console.warn("Main WebSocket Closed")
    ConnectInter = setTimeout(function(){Connect();},5000);
    console.warn("Reconnecting at 5000 intervals")
    Loading();
  };
};

$("#CreateGameForm").submit(function(event) {
  event.preventDefault()
  SendCommand("uu",$("#UserName").val())
  SendCommand("cg", getCookie("id"), )
  Loading();
})
$("#PinForm").submit(function(event) {
  event.preventDefault()
  SendCommand("uu",$("#UserName").val())
  window.location = "/Game/" + $("#GamePin").val()
})

$("#UserForm").submit(function( event ) {
  SendCommand("uu",$("#UserName").val())
  event.preventDefault();
});

function SendCommand(action, ...Args){
  var string = "";
  for (i = 0; i < Args.length; i++){
    string = string + '"' + Args[i] + '",';
  }
  ws.send('{"action":"'+action+'", "Arg":['+string.slice(0, -1)+']}')
}

Connect()
