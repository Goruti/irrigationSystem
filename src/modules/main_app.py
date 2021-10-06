import gc
gc.collect()
from web_server import irr_web_server
gc.collect()
import uasyncio as asyncio
from tools.libraries import initialize_irrigation_app, unmount_sd_card
from modules.main_loops import initialize_rtc, reading_moister, reading_water_level
import logging
gc.collect()


_logger = logging.getLogger("app")

def start():
    gc.collect()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(initialize_irrigation_app())
    try:
        loop.create_task(initialize_rtc(frequency_loop=3600))
        loop.create_task(reading_water_level())
        loop.create_task(reading_moister(frequency_loop_ms=600000, report_freq_ms=1800000))
        irr_web_server.webapp.run(host="0.0.0.0", port=80)

    except Exception as e:
        _logger.exc(e, "GOODBYE DUDE!!!")

    finally:
        if loop:
            loop.close()
        unmount_sd_card()
