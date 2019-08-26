var ws;
function Connect(){
  ws = new WebSocket("ws://"+window.location.host+"/ws");
  ws.onopen = function() {
    SendCommand("cu", getCookie("id"))
    $(".se-pre-con").fadeOut("slow");
  };

  ws.onmessage = function(evt) {
    var message = JSON.parse(evt.data)
    switch (message["action"]){
      case "sa":
        console.log("Websocket Action Successfully");
        break;
      case "fa":
        console.warn("WebSocket Action Failed")
        break;
      case "rd":
        document.location.href = message["Arg"][0]
        break;
      default:
        console.warn("Unknown Action")
    }
  };
  ws.onclose = function(){
    console.warn("Main WebSocket Closed")
    ConnectInter = setTimeout(function(){Connect();},5000);
    console.warn("Reconnecting at 5000 intervals")
    Loading();
  };
};

$("#PinForm").submit(function(event) {
  event.preventDefault()
  SendCommand("uu",$("#FUserName").val())
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
$("#CreateForm").submit(function(event){
  event.preventDefault();
  if ($("[name='Grade']:checked").val() == "C"){
    var Values = [$("[name='Colours']:checked").val(),$("[name='Length']:checked").val()]
    console.log(Values)
  } else{ var Values = $("input[name='Grade']:checked").val()}
  console.log("Sending",Values)
  SendCommand("uu",$("#FUserName").val())
  SendCommand("cg", Values, false)
  Loading();
})
$("button[name='Teams']").click(function(){
  if ($("[name='Grade']:checked").val() == "C"){
    var Values = [$("[name='Colours']:checked").val(),$("[name='Length']:checked").val()]
  } else{ var Values = $("input[name='Grade']:checked").val()}
  SendCommand("uu",$("#FUserName").val())
  SendCommand("cg", Values, true)
  Loading();
})
$(".Remover").click(function(){
  SendCommand("rg", $(this)[0].name)
  $("#"+$(this)[0].name).remove();
  if (! $(".Remover").length){
    console.log("oof")
    $("#Games").append("<p> Wow so empty </p>")
  }
})


Connect()
