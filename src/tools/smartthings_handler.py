import gc
import uasyncio as asyncio
from machine import reset
from tools.wifi import is_connected
import urequests as requests
from logging import getLogger

gc.collect()
_logger = getLogger("SmartThings")


class SmartThings:
    def __init__(self, retry_num=5, retry_sec=1, st_ip=None, st_port=None):

        if st_ip and st_port:
            self.URL = "http://{}:{}".format(st_ip, st_port)
        else:
            self.URL = None

        self.retry_num = retry_num
        self.retry_sec = retry_sec
        self.requests = requests

    async def notify(self, body):
        if await is_connected():
            try:
                attempts = self.retry_num
                _logger.debug("Smartthings.notify, Sent body: {}".format(body))
                if self.URL:
                    while attempts and await self._send_values(body):
                        attempts -= 1
                        _logger.error("Smartthings.notify, Re-try: {} - Body: {}".format((self.retry_num - attempts), body))
                        await asyncio.sleep(pow(2, (self.retry_num - attempts)) * self.retry_sec)

                    if not attempts:
                        _logger.error("Smartthings.notify - Tried: {} times and it couldn't send readings".format(self.retry_num))
                else:
                    _logger.error("SmartThings is not configured")
            except Exception as e:
                _logger.exc(e, "Failed to notify ST")
            finally:
                gc.collect()
        else:
            _logger.debug("Discarding message since device is not connected")
            _logger.info("restarting the system")
            reset()

    async def _send_values(self, body):
        gc.collect()
        failed = True
        headers = {"Content-Type": "application/json"}

        try:
            r = self.requests.post(self.URL, json=body, headers=headers)
        except Exception as e:
            _logger.exc(e, "fail to send Value - free_memory: {}".format(gc.mem_free()))
        else:
            if r.status_code == 202 or r.status_code == 200:
                failed = False
            else:
                _logger.debug("'Smartthings.send_values' - HTTP_Status_Code: '{}' - HTTP_Reason: {}".format(r.get("status_code"), r.get("reason")))
            r.close()
        finally:
            gc.collect()
            return failed
