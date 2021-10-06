import gc
gc.collect()
import tinyweb
gc.collect()
from web_server.route_functions import index_get, pump_action, test_system, index_scripts, send_css, get_log_file, enable_web_repl,\
    enable_ftp, enable_ap, restart_system, enable_smartthings, wifi_config, irrigation_config

gc.collect()

webapp = tinyweb.webserver()
webapp.add_route("/", index_get, methods=["GET"], save_headers=["Accept"])
webapp.add_route('/pump_action', pump_action, methods=['GET'], save_headers=["Accept"])
webapp.add_route('/test_system', test_system, methods=['GET'], save_headers=["Accept"])
webapp.add_route("/scripts/<fn>", index_scripts, methods=["GET"])
webapp.add_route("/css/<fn>", send_css, methods=["GET"])
webapp.add_route('/get_log_file', get_log_file, methods=['GET'])
webapp.add_route('/enable_web_repl', enable_web_repl, methods=['GET'])
webapp.add_route('/enable_ftp', enable_ftp, methods=['GET'])
webapp.add_route('/enable_ap', enable_ap, methods=['GET'])
webapp.add_route('/restart_system', restart_system, methods=['GET'])
webapp.add_route('/config_wifi', wifi_config, methods=['GET', 'POST'], save_headers=["Content-Length", "Content-Type"])
webapp.add_route('/enable_smartthings', enable_smartthings, methods=['GET', 'POST'], save_headers=["Content-Length", "Content-Type"])
webapp.add_route('/irrigation_config', irrigation_config, methods=['GET', 'POST'], save_headers=["Content-Length", "Content-Type"])



