var newScript = document.createElement("script");
newScript.type = "text/javascript";
newScript.src = location.pathname.substring(0, location.pathname.lastIndexOf('/') + 1) + "khan-exercise.js";
document.getElementsByTagName("head")[0].appendChild(newScript);