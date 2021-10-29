import gc
from logging import getLogger, DEBUG
import uasyncio as asyncio
from tools.wifi import start_ap, stop_ap, wifi_connect
from tools.manage_data import create_dir, get_network_config
from tools.conf import DB_DIR, AP_SSID, AP_PWD, SD_MOUNTING, LOG_DIR, LOG_FILENAME
from tools.libraries import initialize_root_logger, unmount_sd_card, mount_sd_card
from modules import main_app
gc.collect()

loop = asyncio.get_event_loop()

##  Mount SD Card and Initialize Logging ##
#create LOG Directory
if LOG_DIR and mount_sd_card():
    log_dir = "{}/{}".format(SD_MOUNTING, LOG_DIR)
else:
    log_dir = "/{}".format(LOG_DIR)

loop.run_until_complete(create_dir(log_dir))
logfile = "{}/{}".format(log_dir, LOG_FILENAME)

initialize_root_logger(level=DEBUG, logfile=logfile)

_logger = getLogger("main")
gc.collect()

_logger.info("############# STARTING IRRIGATION SYSTEM #############")
#create database Directory
loop.run_until_complete(create_dir(DB_DIR))

try:
    net_config = loop.run_until_complete(get_network_config())
    loop.run_until_complete(wifi_connect(net_config=net_config))
except Exception as e:
    _logger.exc(e,"Failed to connect to Wifi")
    _logger.info("Device is Offline. Start AP")
    loop.run_until_complete(start_ap(AP_SSID, AP_PWD))
else:
    stop_ap()

gc.collect()
try:
    main_app.start()
except Exception as e:
    unmount_sd_card()
    _logger.exc(e, "failed starting main application")
