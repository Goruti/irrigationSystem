import gc
gc.collect()
from tinyweb.server import parse_query_string, HTTPException
gc.collect()
import uasyncio as asyncio
gc.collect()
import machine
from logging import getLogger
gc.collect()
import ujson as json
gc.collect()
from tools.conf import AP_SSID, AP_PWD, LOG_DIR, WEBREPL_PWD
from tools.wifi import is_connected, wifi_disconnect, start_ap, stop_ap, get_available_networks,\
    wifi_connect
gc.collect()
from tools.libraries import get_net_configuration, get_irrigation_state, get_irrigation_status,\
    test_irrigation_system, get_web_repl_configuration, get_logs_files_info, get_smartthings_configuration,\
    start_pump, stop_pump, get_st_handler, get_ftp_configuration
from tools.manage_data import save_network, save_webrepl_config, save_smartthings_config,\
    save_irrigation_config, read_irrigation_config, save_ftp_config
from web_server.script import wifi_js, index_js

gc.collect()

_logger = getLogger("route_functions")


async def index_get(req, resp):
    gc.collect()
    _logger.info("Running 'index_get'")

    if b"text/html" in req.headers[b'Accept']:
        try:
            await resp.send_file("web_server/html/index.html.gz", content_encoding="gzip", max_age=0)
        except HTTPException as e:
            _logger.exc(e, "Fail getting Home Page")
            gc.collect()
            await resp.error(e.code)
        except Exception as e:
            _logger.exc(e, "Fail getting Home Page")
            gc.collect()
            await resp.error(500, "Internal Error.\nServer couldn't complete your request")
        else:
            gc.collect()

    elif b"application/json" in req.headers[b'Accept']:
        try:
            data = {
                "type": "refresh",
                "body": await get_irrigation_status()
            }
            _logger.debug("data: {}".format(json.dumps(data)))
            await resp.start_json()
            await resp.send(json.dumps(data))
        except Exception as e:
            _logger.exc(e, "Fail getting Home Page")
            gc.collect()
            await resp.error(500, "Internal Error.\nServer couldn't complete your request")
        else:
            gc.collect()


async def index_scripts(req, resp, fn):
    gc.collect()

    gen_script = ""
    script_to_load = fn.split(".")[0]
    try:
        if script_to_load == "irrigation_state":
            _logger.info("Getting Script 'irrigation_state'")
            data = { "irrigationState": await get_irrigation_state() }
            gen_script = index_js.irrigation_state(data)

        elif script_to_load == "web_repl_config":
            _logger.info("Getting Script 'web_repl_config'")
            data = { "WebRepl": await get_web_repl_configuration() }
            gen_script = index_js.web_repl_config(data)

        elif script_to_load == "smartthings_config":
            _logger.info("Getting Script 'smartthings_config'")
            data = { "smartThings": await get_smartthings_configuration() }
            gen_script = index_js.smartthings_config(data)

        elif script_to_load == "ftp_config":
            _logger.info("Getting Script 'ftp_config'")
            data = { "ftp": await get_ftp_configuration() }
            gen_script = index_js.ftp_config(data)

        elif script_to_load == "network_config":
            _logger.info("Getting Script 'network_config'")
            data = { "net_config": await get_net_configuration() }
            gen_script = index_js.network_configuration(data)

        elif script_to_load == "irrigation_config":
            _logger.info("Getting Script 'irrigation_config'")
            data = { "irrigation_config": await get_irrigation_status() }
            gen_script = index_js.irrigation_configuration(data)

        elif script_to_load == "logs_files":
            _logger.info("Getting Script 'logs_files'")
            data = { "log_files": await get_logs_files_info() }
            gen_script = index_js.logs_files(data)

    except Exception as e:
        _logger.exc(e, "Fail getting index_script")
        gc.collect()
        await resp.error(500, "Internal Error.\nServer couldn't complete your request")
    else:
        gc.collect()
        if gen_script:
            await __send_page_generator(resp, gen_script)
        else:
            await resp.error(404, "file not found")


async def send_css(req, resp, fn):
    gc.collect()
    _logger.info("Running 'send_css'")
    try:
        await resp.send_file('web_server/css/{}.gz'.format(fn), content_encoding="gzip")
    except HTTPException as e:
        _logger.exc(e, "Fail to send css file")
        gc.collect()
        await resp.error(e.code)
    except Exception as e:
        _logger.exc(e, "Fail to send css file")
        gc.collect()
        await resp.error(500, "Internal Error.\nServer couldn't complete your request")
    else:
        gc.collect()


async def enable_ap(req, resp):
    gc.collect()
    _logger.info("Running 'enable_ap'")
    try:
        html_page = wifi_js.enable_ap(await start_ap(AP_SSID, AP_PWD))
        if html_page:
            gc.collect()
            await __send_page_generator(resp, html_page)
    except Exception as e:
        _logger.exc(e, "Fail Enabling AP")
        gc.collect()
        await resp.error(500, "Internal Error.\nServer couldn't complete your request")


async def wifi_config(req, resp):
    gc.collect()
    _logger.info("Running 'wifi_config'")

    if req.method == b"GET":
        await wifi_config_get(req, resp)
    elif req.method == b"POST":
        await wifi_config_post(req, resp)


async def wifi_config_get(req, resp):
    gc.collect()
    _logger.info("Running 'wifi_config_get'")

    try:
        html_page = wifi_js.get_form(await get_available_networks())
        if html_page:
            gc.collect()
            await __send_page_generator(resp, html_page)
    except Exception as e:
        _logger.exc(e, "Fail Configuring Wifi")
        gc.collect()
        await resp.error(500, "Internal Error.\nServer couldn't complete your request")


async def wifi_config_post(req, resp):
    gc.collect()
    _logger.info("Running 'wifi_config_post'")

    net_config = {}
    try:
        data = await req.read_parse_form_data()
        for key in ['ssid', 'password']:
            value = data.get(key, {})
            if value:
                net_config[key] = value
            else:
                _logger.error("Bad Request: {}".format(data))
                await resp.error(400,
                                 "Bad Request. key '{}' not found in the requestData or value is empty.\n requestData: {}".format(
                                     key, data))
                return
            # Now try to connect to the WiFi network
        _logger.debug("trying to connect to wifi with {}".format(net_config))
        await wifi_connect(net_config=net_config)

    except Exception as e:
        _logger.exc(e, "Fail connecting to wifi")
        gc.collect()
        await resp.error(500, "Internal Error. Server couldn't complete your request")
    else:
        try:
            gc.collect()
            await save_network(**net_config)
            data = [net_config['ssid'], await is_connected()]
            html_page = wifi_js.confirmation(data)
            await __send_page_generator(resp, html_page)

            #await asyncio.sleep(5)
            #_logger.debug("restarting ESP-32")
            #machine.reset()
            stop_ap()

        except Exception as e:
            _logger.exc(e, "Fail to save wifi configuration and re-start the system")
            gc.collect()
            await resp.error(500, "Internal Error.\nServer couldn't complete your request")


async def irrigation_config(req, resp):
    gc.collect()
    _logger.info("Running 'wifi_config'")
    if req.method == b"GET":
        await irrigation_config_get(req, resp)
    elif req.method == b"POST":
        await irrigation_config_post(req, resp)


async def irrigation_config_get(req, resp):
    gc.collect()
    try:
        await resp.send_file("web_server/html/config_irrigation.html.gz", content_encoding="gzip")

    except HTTPException as e:
        _logger.exc(e, "Cannot get irrigation Configuration")
        gc.collect()
        await resp.error(e.code)
    except Exception as e:
        _logger.exc(e, "Cannot get irrigation Configuration")
        gc.collect()
        await resp.error(500, "Internal Error.\nServer couldn't complete your request")
    finally:
        gc.collect()


async def irrigation_config_post(req, resp):
    gc.collect()
    try:
        data = await req.read_parse_form_data()
        config = {}
        for key in ['total_pumps']:
            value = data.get(key, {})
            if value:
                config[key] = value
            else:
                _logger.error("Bad Request: {}".format(data))
                await resp.error(400,
                                 "Bad Request. key '{}' not found in the requestData or value is empty.\n requestData: {}".format(key, data))
                return

        pump_info = {}
        for pump in range(1, int(config.get("total_pumps"))+1):
            pump_info[pump] = {
                "moisture_threshold": int(data.get("moisture_threshold_{}".format(pump), {})),
                "connected_to_port": data.get("connected_to_port_{}".format(pump)),
            }
        config.update({"pump_info": pump_info})

        st = await get_st_handler(retry_sec=1, retry_num=2)
        if st:
            net_conf = await get_net_configuration()
            payload = {
                "type": "system_configuration",
                "body": {
                    "ssid": net_conf["ssid"],
                    "ip": net_conf["ip"],
                    "system": config
                }
            }
            await st.notify([payload])
        await save_irrigation_config(**config)
        gc.collect()

    except Exception as e:
        _logger.exc(e, "Fail Saving Irrigation Configuration")
        gc.collect()
        await resp.error(500, "Internal Error.\nServer couldn't complete your request")

    else:
        gc.collect()
        try:
            await resp.send_file("web_server/html/restart_system.html.gz", content_encoding="gzip", max_age=0)
        except HTTPException as e:
            _logger.exc(e, "Cannot get restart_system HTML")
            gc.collect()
            await resp.error(e.code)
        except Exception:
            pass
        _logger.info("Sleeping.......")
        await asyncio.sleep(2)
        await wifi_disconnect()
        machine.reset()


async def pump_action(req, resp):
    gc.collect()
    _logger.info("Running 'pump_action'")
    try:
        if req.query_string != b'':
            qs = req.query_string.decode('utf-8')
            qs_form = parse_query_string(qs)

        port = qs_form.get("pump", {})
        action = qs_form.get("action", {})
        assert port and action, "Bad request"
        api_data = {
            "type": "pump_status",
            "body": {
                port: "off"
            }
        }
        if action == "on":
            started = await start_pump(port, False)
            if started:
                await asyncio.sleep(4)
                await stop_pump(port, False)
                api_data["body"][port] = "on"
        elif action == "off":
            await stop_pump(port, False)

        if b"text/html" in req.headers[b"Accept"]:
            gc.collect()
            await resp.redirect("/", "redirected to the home page")
        else:
            gc.collect()
            await resp.send(json.dumps(api_data))

    except AssertionError as e:
        _logger.exc(e, "Pump Action- Bad Request: '{}'".format(qs))
        gc.collect()
        await resp.error(400, "Bad Request")

    except Exception as e:
        _logger.exc(e, "Fail to start/stop the pump")
        gc.collect()
        await resp.error(500, "Internal Error. Server couldn't complete your request")


async def enable_smartthings(req, resp):
    gc.collect()
    _logger.info("Running 'enable_smartthings'")

    if req.method == b"GET":
        await enable_smartthings_get(req, resp)
    elif req.method == b"POST":
        await enable_smartthings_post(req, resp)


async def enable_smartthings_get(req, resp):
    gc.collect()
    _logger.info("Running 'enable_smartthings_get'")
    try:
        if req.query_string != b'':
            qs = req.query_string.decode('utf-8')
            qs_form = parse_query_string(qs)

            if qs_form.get("action", {}) == "enable":
                gc.collect()
                try:
                    await resp.send_file("web_server/html/config_smartthings.html.gz", content_encoding="gzip")
                except HTTPException as e:
                    _logger.exc(e, "Cannot get SmartThings Configuration")
                    gc.collect()
                    await resp.error(e.code)
                except Exception:
                    pass

            elif qs_form.get("action", {}) == "disable":
                st = await get_st_handler(retry_sec=1, retry_num=2)
                if st:
                    payload = {
                        "type": "system_configuration",
                        "body": {
                            "status": "disable"
                        }
                    }
                    await st.notify([payload])

                st_conf = {
                    "enabled": False,
                    "st_ip": None,
                    "st_port": None
                }
                await save_smartthings_config(**st_conf)
                gc.collect()
                await resp.redirect("/", "redirected to the home page")

            else:
                gc.collect()
                await resp.error(400, "Bad Request. 'action' not found in the Query String or 'action type' not valid.\nQuery String: '{}'".format(qs))
        else:
            gc.collect()
            await resp.error(400, "Bad Request. Query String is empty")

    except Exception as e:
        _logger.exc(e, "Fail Enable/Disable SmartThings")
        gc.collect()
        await resp.error(500, "Internal Error. Server couldn't complete your request")


async def enable_smartthings_post(req, resp):
    gc.collect()
    _logger.info("Running 'enable_smartthings_post'")
    try:
        data = await req.read_parse_form_data()
        st_config = {}
        for key in ['st_ip', 'st_port']:
            value = data.get(key, {})
            if value:
                st_config[key] = value
            else:
                _logger.error("Bad Request: {}".format(data))
                await resp.error(400, "Bad Request. key '{}' not found in the requestData or value is empty.\n requestData: {}".format(key, data))
                return

        st_config["enabled"] = True
        await save_smartthings_config(**st_config)

        st = await get_st_handler(retry_sec=1, retry_num=2)
        if st:
            net_conf = await get_net_configuration()
            payload = {
                "type": "system_configuration",
                "body": {
                    "status": "enabled",
                    "ssid": net_conf["ssid"],
                    "ip": net_conf["ip"],
                    "system": await read_irrigation_config()
                }
            }
            await st.notify([payload])
            gc.collect()
            await resp.redirect("/", "redirected to the home page")

    except Exception as e:
        _logger.exc(e, "Fail to enable SmartThings")
        gc.collect()
        await resp.error(500, "Internal Error. Server couldn't complete your request")


async def restart_system(req, resp):
    gc.collect()
    _logger.info("Running 'restart_system'")
    try:
        gc.collect()
        await resp.send_file("web_server/html/restart_system.html.gz", content_encoding="gzip", max_age=0)
    except HTTPException as e:
        _logger.exc(e, "Cannot get restart_system html")
        gc.collect()
        await resp.error(e.code)
    except Exception:
        pass
    _logger.info("Sleeping.......")
    await asyncio.sleep(2)
    await wifi_disconnect()
    machine.reset()


async def test_system(req, resp):
    gc.collect()
    _logger.info("Running 'test_system'")
    try:
        await test_irrigation_system()
    except Exception as e:
        _logger.exc(e, "Fail testing the system")
        gc.collect()
        await resp.error(500, "Internal Error. Server couldn't complete your request")
    else:
        if b"text/html" in req.headers[b"Accept"]:
            gc.collect()
            await resp.redirect("/", "redirected to the home page")
        else:
            data = {
                "type": "system_test",
                "body": "done"
            }
            gc.collect()
            await resp.start_json()
            await resp.send(json.dumps(data))


async def get_log_file(req, resp):
    gc.collect()
    _logger.info("Running 'get_log_file'")
    try:
        if req.query_string != b'':
            query_string = req.query_string.decode('utf-8')
            qs_form = parse_query_string(query_string)
            file_name = qs_form.get("file_name", {})
            if file_name:
                file_name = qs_form.get("file_name", {})
                _logger.debug("File to fetch '{}/{}'".format(LOG_DIR, file_name))
                gc.collect()
                await resp.send_file("{}/{}".format(LOG_DIR, file_name))
            else:
                gc.collect()
                await resp.error(400, "Bad Request. 'file_name' not found in the Query String.\nQuery String: '{}'".format(query_string))
        else:
            gc.collect()
            await resp.error(400, "Bad Request. Query String is empty")
    except HTTPException as e:
        _logger.exc(e, "Fail Getting the logs")
        gc.collect()
        await resp.error(e.code)
    except Exception as e:
        _logger.exc(e, "Fail Getting the logs")
        gc.collect()
        await resp.error(500, "Internal Error. Server couldn't complete your request")


async def enable_web_repl(req, resp):
    _logger.info("Running 'config_web_repl'")
    gc.collect()
    try:
        import webrepl
        gc.collect()
        await __srv_start_stop(req, resp, webrepl, save_webrepl_config, password=WEBREPL_PWD)
    except Exception as e:
        _logger.exc(e, "Fail to start/stop webrepl")
        gc.collect()
        await resp.error(500, "Internal Error. Server couldn't complete your request")


async def enable_ftp(req, resp):
    _logger.info("Running 'config_ftp'")
    gc.collect()
    try:
        import ftptiny
        gc.collect()
        ftp = ftptiny.FtpTiny()
        await __srv_start_stop(req, resp, ftp, save_ftp_config)
    except Exception as e:
        _logger.exc(e, "Fail to start/stop ftp")
        gc.collect()
        await resp.error(500, "Internal Error. Server couldn't complete your request")


async def __srv_start_stop(req, resp, srv, save_conf, **kwargs):
    gc.collect()

    try:
        assert srv, 'Service can not be null'
        assert save_conf, 'Save function can not be null'

        if req.query_string != b'':
            qs = req.query_string.decode('utf-8')
            qs_form = parse_query_string(qs)

            if qs_form.get("action", {}) == "enable":
                srv.start(**kwargs)
                await save_conf(**{"enabled": True})
                gc.collect()
                await resp.redirect("/", "redirected to the home page")
            elif qs_form.get("action", {}) == "disable":
                srv.stop()
                await save_conf(**{"enabled": False})
                gc.collect()
                await resp.redirect("/", "redirected to the home page")
            else:
                gc.collect()
                await resp.error(400, "Bad Request. 'action' not found in the Query String or 'action type' not valid.\nQuery String: '{}'".format(qs))
        else:
            gc.collect()
            await resp.error(400, "Bad Request. Query String is empty")

    except Exception as e:
        _logger.exc(e, "Fail to start/stop service")
        await resp.error(500, "Internal Error. Server couldn't complete your request")


async def __send_page_generator(resp, file):
    await resp.start_html()
    it = iter(file)
    while True:
        try:
            line = next(it)
        except StopIteration:
            break
        await resp.send(line)