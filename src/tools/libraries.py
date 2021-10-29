import gc
import machine
import uasyncio as asyncio
gc.collect()
import sys
import uos
import uio
import utime
from logging import getLogger, basicConfig
gc.collect()
from logging.handlers import RotatingFileHandler
from collections import OrderedDict
from tools import manage_data, smartthings_handler
from tools.conf import PORT_PIN_MAPPING, LOG_DIR, SD_MOUNTING, WATER_LEVEL_SENSOR_PIN
from tools.wifi import is_connected, get_mac_address
gc.collect()

_logger = getLogger("libraries")


async def get_irrigation_status():
    gc.collect()
    systems_info = await get_irrigation_configuration()

    if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
        for key, values in systems_info["pump_info"].items():
            systems_info["pump_info"][key]["pump_status"] = "on" if await read_gpio(
                PORT_PIN_MAPPING.get(values["connected_to_port"], {}).get("pin_pump")) else "off"
            moisture = await read_adc(PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
            systems_info["pump_info"][key]["moisture"] = moisture
            #systems_info["pump_info"][key]["humidity"] = await moisture_to_hum(values["connected_to_port"], moisture)
            #systems_info["pump_info"][key]["threshold_pct"] = await moisture_to_hum(values["connected_to_port"], values["moisture_threshold"])

    systems_info["water_level"] = await get_watter_level()
    gc.collect()
    return systems_info


async def moisture_to_hum(port, moisture):
    gc.collect()
    try:
        dry = PORT_PIN_MAPPING.get(port).get("dry_value")
        wet = PORT_PIN_MAPPING.get(port).get("water_value")
        if moisture >= dry:
            hum = 0.0
        elif moisture <= wet:
            hum = 100.0
        else:
            hum = 100*((moisture-dry)/(wet-dry))
    except:
        hum = -1.0
    finally:
        gc.collect()
        return round(hum, 1)


async def start_irrigation(port, moisture, threshold, max_irrigation_time_ms=2000):
    gc.collect()
    _logger.info("Starting irrigation on Port {}".format(port))
    sensor_pin = PORT_PIN_MAPPING.get(port).get("pin_sensor")
    started = await start_pump(port=port, notify=False)
    if started:
        t = utime.ticks_ms()
        while moisture > threshold * 0.9 and abs(utime.ticks_diff(utime.ticks_ms(), t)) < max_irrigation_time_ms:
            moisture = await read_adc(sensor_pin)
            asyncio.sleep_ms(100)

        await stop_pump(port=port, notify=False)

    st = await get_st_handler(retry_num=1, retry_sec=1)
    if st:
        payload = {
            "type": "moisture_status",
            "body": {port: moisture_to_hum(port, moisture)}
        }
        await st.notify(payload)


async def read_gpio(pin):
    gc.collect()
    return machine.Pin(pin).value()


async def read_adc(pin):
    gc.collect()
    adc = machine.ADC(machine.Pin(pin))  # create ADC object on ADC pin
    adc.atten(machine.ADC.ATTN_11DB)  # set 11dB input attenuation (voltage range roughly 0.0v - 3.3v)
    adc.width(machine.ADC.WIDTH_12BIT)
    read = 0
    for i in range(0, 8):
        read += adc.read()
        await asyncio.sleep_ms(10)

    gc.collect()
    return int(read / 8)


async def initialize_irrigation_app():
    gc.collect()
    _logger.info("Initializing Ports")
    st_payload = []
    try:
        st = await get_st_handler(retry_num=1, retry_sec=1)
        for key, value in PORT_PIN_MAPPING.items():
            #  Initialize Pumps pin as OUT_PUTS
            machine.Pin(value["pin_pump"], machine.Pin.OUT, value=0)
            if st:
                st_payload.append({"type": "pump_status", "body": {key: "off"}})

        # initialize webrepl Status
        await manage_data.save_webrepl_config(**{"enabled": False})
        # initialize ftp Server Status
        await manage_data.save_ftp_config(**{"enabled": False})

        # initialize Water Tank Level
        pin = machine.Pin(WATER_LEVEL_SENSOR_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        w_level = await get_watter_level(pin.value())
        if st:
            st_payload.append({
                "type": "water_level_status",
                "body": {
                    "status": w_level
                }
            })
            st.notify(st_payload)

        await manage_data.save_irrigation_state(**{"running": True})

    except Exception as e:
        await manage_data.save_irrigation_state(**{"running": False})
        _logger.exc(e, "Cannot initialize Irrigation APP")
        raise RuntimeError("Cannot initialize Irrigation APP: error: {}".format(e))
    finally:
        gc.collect()


async def start_pump(port, notify=True):
    gc.collect()
    started = False
    pin = PORT_PIN_MAPPING.get(port).get("pin_pump")
    try:
        if await get_watter_level() != "empty":
            _logger.info("Starting Port {} in Pin: {}".format(port, pin))
            machine.Pin(pin).on()
            started = True
            if notify:
                st = await get_st_handler(retry_num=1, retry_sec=1)
                if st:
                    payload = {"type": "pump_status", "body": {port: "on"}}
                    await st.notify([payload])
        else:
            _logger.info("cannot start 'pump {}' since tank is empty".format(port))
    except Exception as e:
        _logger.exc(e, "Failed Starting Pump")
    finally:
        gc.collect()
        return started


async def stop_pump(port, notify=True):
    gc.collect()
    pin = PORT_PIN_MAPPING.get(port).get("pin_pump")
    try:
        _logger.info("Stopping Port {} in Pin {}".format(port, pin))
        machine.Pin(pin).off()
        if notify:
            st = await get_st_handler(retry_num=1, retry_sec=1)
            if st:
                payload = [{"type": "pump_status", "body": {port: "off"}}]
                await st.notify(payload)

    except Exception as e:
        _logger.exc(e, "Failed Stopping Pump")
    finally:
        gc.collect()


async def stop_all_pumps():
    gc.collect()
    try:
        _logger.info("Stopping all pumps")
        for key, value in PORT_PIN_MAPPING.items():
            await stop_pump(key)
    except Exception as e:
        _logger.exc(e, "Failed Stopping ALL Pump")
    finally:
        gc.collect()


async def test_irrigation_system():
    gc.collect()
    try:
        systems_info = await get_irrigation_configuration()
        _logger.info("systems_info: {}".format(systems_info))

        if systems_info and "pump_info" in systems_info.keys() and len(systems_info["pump_info"]) > 0:
            systems_info["pump_info"] = OrderedDict(sorted(systems_info["pump_info"].items(), key=lambda t: t[0]))
            for key, values in systems_info["pump_info"].items():
                _logger.info("testing port {}".format(values["connected_to_port"]))
                moisture = await read_adc(PORT_PIN_MAPPING.get(values["connected_to_port"]).get("pin_sensor"))
                _logger.info("moisture_port_{}: {}".format(values["connected_to_port"], moisture))
                if await start_pump(values["connected_to_port"], notify=False):
                    await asyncio.sleep(4)
                    await stop_pump(values["connected_to_port"], notify=False)

    except Exception as e:
        _logger.exc(e, "Failed Test Irrigation System")
        await stop_all_pumps()
    finally:
        gc.collect()


async def get_st_handler(retry_sec=1, retry_num=1):
    gc.collect()
    smartthings = None
    try:
        st_conf = await get_smartthings_configuration()
        if st_conf.get("enabled", {}):
            smartthings = smartthings_handler.SmartThings(st_ip=st_conf.get("st_ip"),
                                                          st_port=st_conf.get("st_port"),
                                                          retry_sec=retry_sec,
                                                          retry_num=retry_num)
    except Exception as e:
        _logger.exc(e, "Failed to get ST handler")
    finally:
        gc.collect()
        return smartthings


async def get_net_configuration():
    gc.collect()
    data = {"connected": False, "ssid": None, "ip": None, "mac": None}
    try:
        ip = await is_connected()
        if ip:
            net_config = await manage_data.get_network_config()
            data.update({"connected": True, "ssid": net_config.get('ssid', {}), "ip": ip})
        data.update({"mac": await get_mac_address()})
    except Exception as e:
        _logger.exc(e, "Failed to get Network Configuration")
    finally:
        gc.collect()
        return data


async def get_irrigation_configuration():
    gc.collect()
    conf = {
        "total_pumps": 0,
        "pump_info": {},
        "water_level": None
    }
    try:
        storage_conf = await manage_data.read_irrigation_config()
        if storage_conf:
            conf.update(storage_conf)
    except Exception as e:
        _logger.exc(e, "Failed to get Irrigation configuration")
    finally:
        gc.collect()
        return conf


async def get_web_repl_configuration():
    gc.collect()
    conf = {
        "enabled": False
    }
    try:
        storage_conf = await manage_data.read_webrepl_config()
        if storage_conf:
            conf.update(storage_conf)
    except Exception as e:
        _logger.exc(e, "Failed to get webrepl configuration")
    finally:
        gc.collect()
        return conf


async def get_smartthings_configuration():
    gc.collect()
    conf = {
        "enabled": False,
        "st_ip": None,
        "st_port": None
    }
    try:
        storage_conf = await manage_data.read_smartthings_config()
        if storage_conf:
            conf.update(storage_conf)
    except Exception as e:
        _logger.exc(e, "Failed to get ST configuration")
    finally:
        gc.collect()
        return conf


async def get_ftp_configuration():
    gc.collect()
    conf = {
        "enabled": False
    }
    try:
        storage_conf = await manage_data.read_ftp_config()
        if storage_conf:
            conf.update(storage_conf)
    except Exception as e:
        _logger.exc(e, "Failed to get ftp configuration")
    finally:
        gc.collect()
        return conf


async def get_irrigation_state():
    gc.collect()
    state = {
        "running": None
    }
    try:
        storage_conf = await manage_data.read_irrigation_state()
        if storage_conf:
            state.update(storage_conf)
    except Exception as e:
        _logger.exc(e, "Failed Getting Irrigation State")
    finally:
        gc.collect()
        return state


async def get_log_files_names():
    gc.collect()
    files = []
    try:
        files = uos.listdir(LOG_DIR)
        files.sort()
    except Exception as e:
        _logger.exc(e, "cannot get the log files name")
    finally:
        gc.collect()
        return files


async def get_logs_files_info():
    gc.collect()
    files_info = []
    try:
        files = await get_log_files_names()
    except Exception as e:
        _logger.exc(e, "Cannot get the logs files")

    if files:
        for file in files:
            try:
                file_gen = (row for row in open("{}/{}".format(LOG_DIR, file), "r"))
                ts_from = ""
                for row in file_gen:
                    ts = await validate_timestamp(row.split(",")[0])
                    if ts:
                        ts_to = ts
                        if not ts_from:
                            ts_from = ts

                #with open("{}/{}".format(LOG_DIR, file), "r") as f:
                #   ts_from = ""
                #   for row in f:
                #       ts = await validate_timestamp(row.split(",")[0])
                #       if ts:
                #           ts_to = ts
                #           if not ts_from:
                #               ts_from = ts

                files_info.append({
                    "file_name": file,
                    "ts_from": ts_from,
                    "ts_to": ts_to
                })
            except Exception as e:
                _logger.exc(e, "Cannot read file '{}'".format(file))

    gc.collect()
    return files_info

async def validate_timestamp(string):
    timestamp = ""
    try:
        date, time = string.split(" ")
        year, month, day = [int(x) for x in date.split("-")]
        assert (year > 0)
        assert (1 <= month <= 12)
        assert (1 <= day <= 31)
        hour, min, sec = [int(x) for x in time.split(":")]
        assert (0 <= hour <= 24)
        assert (0 <= min <= 59)
        assert (0 <= sec <= 59)
        timestamp = string
    except Exception:
        pass
    return timestamp

def initialize_root_logger(level, logfile=None):
    gc.collect()
    try:
        basicConfig(level=level)
        _logger = getLogger()
        if logfile:
            rfh = RotatingFileHandler(logfile, maxBytes=20*1024, backupCount=5)
            _logger.addHandler(rfh)
        else:
            rfh = RotatingFileHandler(logfile, maxBytes=10 * 1024, backupCount=2)
            _logger.addHandler(rfh)

    except Exception as e:
        buf = uio.StringIO()
        sys.print_exception(e, buf)
        raise RuntimeError("Cannot Initialize loggers.\nError: {}".format(buf.getvalue()))
    finally:
        gc.collect()


def unmount_sd_card():
    try:
        if SD_MOUNTING and str(SD_MOUNTING) != "" and SD_MOUNTING in uos.listdir():
            uos.umount(SD_MOUNTING)
    # There is nothing to unmount
    except Exception as e:
        pass


def mount_sd_card():
    gc.collect()
    sd_mounted = False
    if SD_MOUNTING and str(SD_MOUNTING) != "":
        try:
            sd = machine.SDCard(slot=2, sck=18, miso=19, mosi=23, cs=5, freq=80000000)
        except Exception as e:
            buf = uio.StringIO()
            sys.print_exception(e, buf)
            print("Cannot Create SDCard Object.\nError: {}".format(buf.getvalue()))
        else:
            try:
                uos.mount(sd, "/{}".format(SD_MOUNTING))
            except Exception as e:
                sd.deinit()
                buf = uio.StringIO()
                sys.print_exception(e, buf)
                print("Cannot Mount SD Card.\nError: {}".format(buf.getvalue()))
            else:
                sd_mounted = True
    gc.collect()
    return sd_mounted


async def get_watter_level(value=None):
    try:
        if not value:
            value = await read_gpio(WATER_LEVEL_SENSOR_PIN)
    except Exception as e:
        _logger.exc(e, "Cannot read tank level")
        value = 1
    return "empty" if value else "good"


def datetime_to_iso(time):
    gc.collect()
    return "{}-{}-{}T{}:{}:{}".format(*time)
