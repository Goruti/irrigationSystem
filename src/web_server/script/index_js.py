import gc

def irrigation_state(data):
    gc.collect()
    yield """var wrapper = document.getElementById("irrigation_state");"""
    yield """wrapper.removeAttribute("style");"""
    yield """wrapper.classList.remove("loader");"""
    yield """var div = document.createElement("Div");"""
    yield """div.style.fontSize="14px";"""
    yield """div.style.textAlign="right";"""
    yield """if (\"""" + str(data.get("irrigationState", {}).get("running", {})) + """\" === "True") {"""
    yield """    div.style.color="green";"""
    yield """    div.innerHTML = "Running";"""
    yield """} else {"""
    yield """    div.style.color="red";"""
    yield """    div.innerHTML = "Stopped";"""
    yield """}"""
    yield """wrapper.appendChild(div);"""


def button_config(data):
    gc.collect()
    yield """var wrapper = document.getElementById(\""""+ str(data.get("getElementById", {})) +"""\");"""
    yield """wrapper.classList.remove("loader");"""
    yield """var en_btn = document.createElement("button");"""
    yield """en_btn.innerHTML="Enable";"""
    yield """var dis_btn = document.createElement("button");"""
    yield """dis_btn.innerHTML="Disable";"""
    yield """dis_btn.style.marginLeft = "1em";"""
    yield """if (\"""" + str(data.get("enabled", {})) + """\" === "True") {"""
    yield """    en_btn.disabled = true;"""
    yield """    en_btn.style.fontWeight = "bold";"""
    yield """    en_btn.style.borderWidth = "thin";"""
    yield """    en_btn.style.opacity = 0.6;"""
    yield """    dis_btn.disabled = false;"""
    yield """    dis_btn.onclick =  function(){"""
    yield """        window.location = '/""" + str(data.get("actionEndPoint", {})) + """?action=disable';"""
    yield """    };"""
    yield """} else {"""
    yield """    en_btn.disabled = false;"""
    yield """    en_btn.onclick = function(){"""
    yield """        window.location = '/""" + str(data.get("actionEndPoint", {})) + """?action=enable';"""
    yield """      }; """
    yield """    dis_btn.disabled = true;"""
    yield """    dis_btn.style.fontWeight = "bold";"""
    yield """    dis_btn.style.borderWidth = "thin";"""
    yield """    dis_btn.style.opacity = 0.6;"""
    yield """}"""
    yield """wrapper.appendChild(en_btn);"""
    yield """wrapper.appendChild(dis_btn);"""


def web_repl_config(data):
    gc.collect()
    conf = {
        "enabled": data.get("WebRepl", {}).get("enabled", {}),
        "getElementById": "web_repl_config",
        "actionEndPoint": "enable_web_repl"
    }
    yield from button_config(conf)


def ftp_config(data):
    gc.collect()
    conf = {
        "enabled": data.get("ftp", {}).get("enabled", {}),
        "getElementById": "ftp_config",
        "actionEndPoint": "enable_ftp"
    }
    yield from button_config(conf)


def smartthings_config(data):
    gc.collect()
    yield """var wrapper = document.getElementById("smartthings_config");"""
    yield """wrapper.classList.remove("loader");"""
    yield """var ip = document.createElement("p");"""
    yield """var port = document.createElement("p");"""
    yield """var en_btn = document.createElement("button");"""
    yield """en_btn.innerHTML="Enable";"""
    yield """var dis_btn = document.createElement("button");"""
    yield """dis_btn.innerHTML="Disable";"""
    yield """dis_btn.style.marginLeft = "1em";"""
    yield """if (\"""" + str(data.get("smartThings", {}).get("enabled", {})) + """\" === "True") {"""
    yield """    en_btn.disabled = true;"""
    yield """    en_btn.style.fontWeight = "bold";"""
    yield """    en_btn.style.borderWidth = "thin";"""
    yield """    en_btn.style.opacity = 0.6;"""
    yield """    dis_btn.disabled = false;"""
    yield """    dis_btn.onclick =  function(){"""
    yield """        window.location = '/enable_smartthings?action=disable';"""
    yield """        showDiv();"""
    yield """    };"""
    yield """    ip.innerHTML="<u>SmartTings IP</u>: <b>""" + str(data.get("smartThings", {}).get("st_ip", {})) + """</b>";"""
    yield """    port.innerHTML="<u>SmartTings Port</u>: <b>""" + str(data.get("smartThings", {}).get("st_port", {})) + """</b>";"""
    yield """} else {"""
    yield """    en_btn.disabled = false;"""
    yield """    en_btn.onclick = function(){"""
    yield """        window.location = '/enable_smartthings?action=enable';"""
    yield """      }; """
    yield """    dis_btn.disabled = true;"""
    yield """    dis_btn.style.fontWeight = "bold";"""
    yield """    dis_btn.style.borderWidth = "thin";"""
    yield """    dis_btn.style.opacity = 0.6;"""
    yield """}"""
    yield """wrapper.appendChild(ip);"""
    yield """wrapper.appendChild(port);"""
    yield """wrapper.appendChild(en_btn);"""
    yield """wrapper.appendChild(dis_btn);"""
    yield """function showDiv() {"""
    yield """      document.getElementById('smartthings_config').style.display = "none";"""
    yield """      document.getElementById('smartthingsSpinnerLoader').style.display = "block";"""
    yield """}"""

#TODO CLEAN THIS UP
def network_configuration(data):
    gc.collect()
    yield """var wrapper = document.getElementById("network_configuration");"""
    yield """wrapper.classList.remove("loader");"""
    yield """var myHTML = `<p><u>Wifi Connected</u>: <b>""" + str(data.get("net_config", {}).get("connected", {})) + """</b></p>`;"""
    yield """if (\"""" + str(data.get("net_config", {}).get("connected", {})) + """\" === "True") {"""
    yield """    myHTML += `<p><u>SSID</u>: <b>""" + str(data.get("net_config", {}).get("ssid", {})) + """</b></p>`;"""
    yield """    myHTML += `<p><u>IP</u>: <b>""" + str(data.get("net_config", {}).get("ip", {})) + """</b></p>`;"""
    yield """    myHTML += `<p><u>Mac Address</u>: <b>""" + str(data.get("net_config", {}).get("mac", {})) + """</b></p>`;"""
    yield """    myHTML += `<p><button onclick="window.location = '/enable_ap';">Reconfigure Wifi</button>`;"""
    yield """} else {"""
    yield """     myHTML += `<p style="margin-left: 40px; text-align: left; color: #ff5722"><b>You need to configure a Wifi Network</b></p>`;"""
    yield """     myHTML += `<p style="margin-left: 40px; text-align: left;"><button onclick="window.location = '/config_wifi';">Configure Wifi</button>`;"""
    yield """}"""
    yield """wrapper.innerHTML = myHTML;"""


#TODO CLEAN THIS UP
def irrigation_configuration(data):
    gc.collect()
    yield """var wrapper = document.getElementById("irrigation_configuration");"""
    yield """wrapper.classList.remove("loader");"""
    yield """var myHTML = ``;"""
    yield """myHTML += `<p><u>Water Level:</u> <b>""" + str(data.get("irrigation_config", {}).get("water_level", {})) + """</b></p>`;"""
    yield """if ( \"""" + str(data.get("irrigation_config", {}).get("total_pumps", {})) + """\" !== "0" ) {"""
    yield """    var total_pump =""" + str(data.get("irrigation_config", {}).get("total_pumps", {})) + """;"""
    yield """    var pump_info =""" + str(data.get("irrigation_config", {}).get("pump_info", {})) + """;"""
    yield """    myHTML += `<p><u>Number of Plant(s) to Irrigate:</u> <b>` + total_pump + `</b></p>`;"""
    yield """    myHTML += `<p><u>Plant(s) Details</u></p>`;"""
    yield """    myHTML +=  `<table class="tg">`;"""
    yield """    myHTML +=  `<thead>`;"""
    yield """    myHTML +=  `<tr>`;"""
    yield """    myHTML +=  `<th class="tg-18eh" rowspan="2">Plant #</th>`;"""
    yield """    myHTML +=  `<th class="tg-18eh" rowspan="2">Connected to Port</th>`;"""
    yield """    myHTML +=  `<th class="tg-18eh" rowspan="2">Pump Status</th>`;"""
    yield """    myHTML +=  `<th class="tg-18eh" colspan="3">Moisture</th>`;"""
    yield """    myHTML +=  `<th class="tg-18eh" colspan="2" rowspan="2">Action</th>`;"""
    yield """    myHTML +=  `</tr>`;"""
    yield """    myHTML +=  `<tr>`;"""
    yield """    myHTML +=  `<td class="tg-18eh">Value</td>`;"""
    yield """    myHTML +=  `<td class="tg-18eh">Threshold</td>`;"""
    #yield """    myHTML +=  `<td class="tg-18eh">Humidity</td>`;"""
    yield """    myHTML +=  `</tr>`;"""
    yield """    myHTML +=  `</thead>`;"""
    yield """    myHTML +=  `<tbody>`;"""
    yield """    for (var i = 1; i <= total_pump; i++) {"""
    yield """        myHTML += `<tr>`;"""
    yield """        myHTML += `<td class="tg-xwyw">#` + i + `</td>`;"""
    yield """        myHTML += `<td class="choice_` + pump_info[i]["connected_to_port"] + `">` + pump_info[i]["connected_to_port"] + `</td>`;"""
    yield """        myHTML += `<td class="tg-xwyw">` + pump_info[i]["pump_status"] + `</td>`;"""
    yield """        myHTML += `<td class="tg-xwyw">` + pump_info[i]["moisture"] + `</td>`;"""
    yield """        myHTML += `<td class="tg-xwyw">` + pump_info[i]["moisture_threshold"] + `</td>`;"""
    #yield """        myHTML += `<td class="tg-xwyw">` + pump_info[i]["moisture_threshold"] + ` (` + pump_info[i]["threshold_pct"].toFixed(1) + `%)</td>`;"""
    #yield """        myHTML += `<td class="tg-xwyw">` + pump_info[i]["humidity"].toFixed(1) + `%</td>`;"""
    yield """        if ( pump_info[i]["pump_status"] === "on") {"""
    yield """            myHTML += `<td class="tg-xwyw"><button disabled onclick="onStartButton('` + pump_info[i]["connected_to_port"] + `')" style="opacity:0.6">Start</button></td>`;"""
    yield """            myHTML += `<td class="tg-xwyw"><button onclick="window.location = '/pump_action?action=off&pump=` + pump_info[i]["connected_to_port"] + `';" style="border-width: thin">Stop</button></td>`;"""
    yield """        }"""
    yield """        else {"""
    yield """            myHTML += `<td class="tg-xwyw"><button onclick="onStartButton('` + pump_info[i]["connected_to_port"] + `')" style="border-width: thin">Start</button></td>`;"""
    yield """            myHTML += `<td class="tg-xwyw"><button disabled onclick="window.location = '/pump_action?action=off&pump=` + pump_info[i]["connected_to_port"] + `';" style="opacity:0.6">Stop</button></td>`;"""
    yield """        }"""
    yield """        myHTML += `<tr>`;"""
    yield """    }"""
    yield """    myHTML += `</tbody>`;"""
    yield """    myHTML += `</table>`;"""
    yield """    myHTML += `<p><button onclick="window.location = '/irrigation_config';">Reconfigure Irrigation System</button></p>`;"""
    yield """} else {"""
    yield """     myHTML += `<p style="margin-left: 40px; color: #ff5722"><b>You need to configure your Irrigation System</b></p>`;"""
    yield """     myHTML += `<p><button onclick="window.location = '/irrigation_config';">Configure Irrigation System</button>`;"""
    yield """}"""
    yield """wrapper.innerHTML = myHTML;"""
    yield """function onStartButton(pump_port) {"""
    yield """    if ( \"""" + str(data.get("irrigation_config", {}).get("water_level", {})) + """\" === "empty" ) {"""
    yield """        alert("Water level is to low. Please refill the water tank before starting the pump");"""
    yield """    } else {"""
    yield """        window.location = '/pump_action?action=on&pump=' + pump_port;"""
    yield """    }"""
    yield """}"""

#TODO CLEAN THIS UP
def logs_files(data):
    gc.collect()
    yield """var wrapper = document.getElementById("logs_files");"""
    yield """wrapper.classList.remove("loader");"""
    yield """var myHTML = ``;"""
    yield """myHTML += `<table class="tg">`;"""
    yield """myHTML += `<thead>`;"""
    yield """myHTML += `<tr>`;"""
    yield """myHTML += `<th class="tg-18eh">Filename</th>`;"""
    yield """myHTML += `<th class="tg-18eh">From</th>`;"""
    yield """myHTML += `<th class="tg-18eh">To</th>`;"""
    yield """myHTML += `<th class="tg-18eh">Action</th>`;"""
    yield """myHTML += `</tr>`;"""
    yield """myHTML += `</thead>`;"""
    yield """myHTML += `<tbody>`;"""
    yield """var files_info =["""
    for log_file in data.get("log_files", {}):
        yield "{},".format(str(log_file))
    yield """];"""
    yield """files_info.forEach(file => {"""
    yield """    myHTML += `<tr>`;"""
    yield """    myHTML += `<td class="tg-xwyw">` + file["file_name"] + `</td>`;"""
    yield """    myHTML += `<td class="tg-xwyw">` + file["ts_from"] + `</td>`;"""
    yield """    myHTML += `<td class="tg-xwyw">` + file["ts_to"] + `</td>`;"""
    yield """    myHTML += `<td class="tg-xwyw"><button onclick="window.location = '/get_log_file?file_name=` + file["file_name"] + `';">View</button></td>`;"""
    yield """    myHTML += `</tr>`;"""
    yield """});"""
    yield """myHTML += `</tbody>`;"""
    yield """myHTML += `</table>`;"""
    yield """wrapper.innerHTML = myHTML;"""
