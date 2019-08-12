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
var rad = $("");
for(var i = 0; i < rad.length; i++) {
  rad[i].onclick = function () {
    if(this == rad[0]) {
      console.log(this.value)
    } else {
      console.log("Gay")
    }
  };
}
