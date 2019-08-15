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



setInterval(function(){colorMate();},5000);
