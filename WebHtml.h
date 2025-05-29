const char MAIN_page[] PROGMEM = R"=====(
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
  
h1 {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  background: #ccc;
  display: inline-block;
  padding: 7px;
}
body {
  margin: 0;
  padding: 0;
  text-align: center;
  color: #222;
}
label {
  display: block;
  margin-top: 20px;
}
input {
  width: 50%;
}

    
    </style>
  </head>
  <body>

    <h1>GE Creative - NodeMCU ESP8266</h1>
    <br><br>
    <div class="container">
    <div class="leftside wfxc">
      <div class="slidecontainer">
        <label>Rotation</label>
        <input type="range" min="0" max="180" value="0" id="myRange">
      </div>
      
      <div class="slidecontainer">
        <label>Gripper</label>
        <input type="range" min="0" max="35" value="0" id="myRange1">
      </div>
    </div>
    <div class="rightside wfxc">
      <div class="slidecontainer">
      <label>Up - Down</label>
        <input type="range" min="50" max="150" value="50" id="myRange2"/>
      </div>
      
      <div class="slidecontainer">
      <label>Forward - Back</label>
        <input type="range" min="40" max="120" value="40" id="myRange3"/>
      </div>
    </div>
    </div>

    <script>
      function sendData(pos1,pos2,pos3,pos4) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
          }
        };
        xhttp.open("GET", "setPOS?servoPOS1="+pos1+"&servoPOS2="+pos2+"&servoPOS3="+pos3+"&servoPOS4="+pos4, true);
        xhttp.send();
      } 
    
    var s1=0,s2=0,s3=0,s4=0;
    
      var slider1 = document.getElementById("myRange");
      var slider2 = document.getElementById("myRange1");
      var slider3 = document.getElementById("myRange2");
      var slider4 = document.getElementById("myRange3");
      //var output = document.getElementById("demo");
      //output.innerHTML = slider.value;

      slider1.oninput = function() {
        //output.innerHTML = this.value;
    s1 = slider1.value;
        sendData(s1, s2, s3, s4);
      }
    slider2.oninput = function() {
        //output.innerHTML = this.value;
    s2 = slider2.value;
        sendData(s1, s2, s3, s4);
      }
    slider3.oninput = function() {
        //output.innerHTML = this.value;
    s3 = slider3.value;
        sendData(s1, s2, s3, s4);
      }
    slider4.oninput = function() {
        //output.innerHTML = this.value;
    s4 = slider4.value;
        sendData(s1, s2, s3, s4);
      }
    </script>

  </body>
</html>
)=====";
