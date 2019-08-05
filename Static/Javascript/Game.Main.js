var url = new URL(window.location.href);
var Pin = url.href.split("/").slice(-1)[0]
var Colours;
var ws;

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}
function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
}
//animate body background using color picker function
function colorMate(){
          var colour = pickColor()
          $('body').animate({"background-color": colour},2000);
          $('html').animate({"background-color": colour},2000);
          $('html').animate({"background-color": colour},2000);
}


function Connect(){
  ws = new WebSocket("ws://"+window.location.host+"/Game/ws");
  ws.onopen = function() {
     ws.send('{"action":"Connected","ID":"'+ getCookie("id") +'","Pin":"'+Pin+'"}');
     clearTimeout(ConnectInter);
     HideControls()
     $(".se-pre-con").fadeOut("slow");
  };
  ws.onmessage = function (evt) {
    if (evt.data != '{"action":"<action>", any other arguments}'){
     var message = JSON.parse(evt.data)
     var action = message["action"]
     if (action == "Colour"){
       Colours =  message["Colour"]
       console.log(Colours)
       for (i = 0; i < $(".C").length; i++) {
             $(".C")[i].children[1].style.backgroundColor = message["Colours"][i]
         }

     } else if (action == "ColoursChange") {
       $(".C")[message["index"]].children[1].style.backgroundColor = message["colour"]
     } else if (action == "UrTurn"){
       ShowControls();
     } else if (action == "PlayResults"){
       var results = message["results"];

       AddCode(results[1], results[2], results[3]);
       if (results[3] == $(".C").length){
         console.log(results[0]+"Won")
         var timeleft = 10;
         var downloadTimer = setInterval(function(){
          $("#Countdown").innerHTML = timeleft + " seconds remaining";
          timeleft -= 1;
          if(timeleft <= 0){
            clearInterval(downloadTimer);
            $("#Countdown").innerHTML = "Finished"
          }
        }, 1000);
       }
     };
   }else{
     console.log(evt.data)
   }
  };

  ws.onclose = function(){
    ConnectInter = setTimeout(function(){Connect();},5000);
    Loading();
    console.log("Close");

  }
};
var ConnectInter = setTimeout(function(){Connect();},5000);

//declare array of colors to be used when page loads
var colors = ['#206ba4','#BBD9EE','  #faebeb','#c1c1c1','#e7d3d3','#F1EFE2','#52ADDA','#df6892','#DBDBDB','#AACD4B','#C5AE87'];
var curcolor = 0;
//picks random color from array, different from current one
function pickColor(){
  var rand = Math.floor(Math.random() * 11);
  if (rand == curcolor){
      pickColor();
  }
  else {
      curcolor = rand;
      return colors[rand];
  }
}
function Loading(){
  $('body').animate({"background-color": "#DBDBDB"},2000);
  $(".se-pre-con").fadeIn("slow");;
  $("#Card").fadeOut("slow");;
}
$( "#UserForm" ).submit(function( event ) {
  ws.send('{"action":"updateUser","key":"Name","value":"'+$("#UserName").val()+'"}')
  event.preventDefault();
});
// if (!ws.CONNECTING && !Colours){
//   ws.send('{"action":"Connected","ID":"'+ getCookie("id") +'","Pin":"'+Pin+'"}');
// }

$("#GameForm").submit(function(event){
    event.preventDefault();
    HideControls()
    var code = [];
    for (i = 0; i < $(".C").length; i++) {
      code.push($(".C")[i].children[1].style.backgroundColor);
    };
    ws.send('{"action":"SubmitPlay","code":"'+code+'"}');

})
function HideControls(){
$("#GameForm button").hide();
$("#GameForm h4").show();
$("#GameForm .C .Box").css("height","60%");
$("#GameForm .C .Box").css("padding","20% 0");
}
function ShowControls(){
$("#GameForm button").show();
$("#GameForm h4").hide();
$("#GameForm .C .Box").css("height","33%");
$("#GameForm .C .Box").css("padding","0");
}
function AddCode(code, RC, RP){
  var HtmlScript = '<div class="row"> <div class="Number text-right">'+RC+'</div>'
  for (i = 0; i < code.length; i++){
    HtmlScript+= '<div class="col RC" style="background-color: '+code[i]+'"></div>'
  }
  HtmlScript+='<div class="Number text-left">'+RP+'</div></div> '
  $("#Results").prepend(HtmlScript)
}

$(".C button").click(function(){
      var Index = Colours.indexOf($(this)[0].parentElement.children[1].style.backgroundColor)
      var Index = Index != -1 ? Index : 0

      console.log(Index)
      if ($(this)[0].name == "UP"){
       $(this)[0].parentElement.children[1].style.backgroundColor = Colours[(Index != Colours.length-1) ? Index+1 : 0];
       ws.send('{"action":"ColoursChange","index":'+ $(".C").index($(this)[0].parentElement) +',"colour":"'+Colours[(Index != Colours.length-1) ? Index+1 : 0]+'"}');
      }
      else{
       $(this)[0].parentElement.children[1].style.backgroundColor = Colours[(Index != 0) ? Index-1 : Colours.length-1];
       ws.send('{"action":"ColoursChange","index":'+ $(".C").index($(this)[0].parentElement) +',"colour":"'+Colours[(Index != 0) ? Index-1 : Colours.length-1]+'"}');
      }
})

setInterval(function(){colorMate();},5000);
