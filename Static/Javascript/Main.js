var url = new URL(window.location.href);
setInterval(function() {colorMate();}, 5000);

function getUrlVars() {
  var vars = {};
  var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
    vars[key] = value;
  });
  return vars;
}

function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
}
if (Object.keys(getUrlVars()).includes("Pin")) {
  $("#GamePin").addClass("is-invalid")
  $("#Help").addClass("is-invalid")
  $("#GamePin").val(getUrlVars()["Pin"])
}

ws.onopen = function() {
  ws.send('{"action":"Connected","ID":"' + getCookie("id") + '"}');
  $(".se-pre-con").fadeOut("slow");
};

ws.onmessage = function(evt) {
  if (evt.data != '{"action":"<action>", any other arguments}') {
    var message = JSON.parse(evt.data)
    var action = message["action"]
    if (action == "Username") {
      $("#UserName").val(message["val"]);
    } else if (action == "redirect") {
      window.location = "/Game/" + message["pin"];
    };
  } else {
    console.log(evt.data)
  }
};
$("#UserForm").submit(function(event) {
  ws.send('{"action":"updateUser","key":"Name","value":"' + $("#UserName").val() + '"}')
  event.preventDefault();
});
//animate body background using color picker function
function colorMate() {
  var colour = pickColor()
  $('body').animate({
    "background-color": colour
  }, 2000);
  $('html').animate({
    "background-color": colour
  }, 2000);
  $('html').animate({
    "background-color": colour
  }, 2000);
}

//declare array of colors to be used when page loads
var colors = ['#206ba4', '#BBD9EE', '  #faebeb', '#c1c1c1', '#e7d3d3', '#F1EFE2', '#52ADDA', '#df6892', '#DBDBDB', '#AACD4B', '#C5AE87'];
var curcolor = 0;
//picks random color from array, different from current one
function pickColor() {
  var rand = Math.floor(Math.random() * 11);
  if (rand == curcolor) {
    pickColor();
  } else {
    curcolor = rand;
    return colors[rand];
  }
}

function Loading() {
  $('body').animate({
    "background-color": "#DBDBDB"
  }, 2000);
  $(".se-pre-con").fadeIn("slow");;
  $("#Card").fadeOut("slow");;
}

$("#GameForm").submit(function(event) {
  event.preventDefault()
  ws.send('{"action":"create","col":' + $('input[name=Number]:checked', '#GameForm').val() + ',"bro":' + $('input[name=Broadcast]:checked', '#GameForm').val() + ',"size":' + $('input[name=Code]:checked', '#GameForm').val() + '}');
  Loading();
})
$("#PinForm").submit(function(event) {
  event.preventDefault()
  ws.send('{"action":"updateUser","key":"Name","value":"' + $("#UserName").val() + '"}')
  window.location = "/Game/" + $("#GamePin").val()
})
