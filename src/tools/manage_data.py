import gc
import ujson as json
import btree
import uos

from ucontextlib import contextmanager
from tools.conf import DB_DIR, DB_FILENAME
gc.collect()


@contextmanager
def _get_db():
    """
    Context manager to return an instance of a database
    """
    try:
        db_file = open("{}/{}".format(DB_DIR, DB_FILENAME), 'r+b')
    except OSError:
        db_file = open("{}/{}".format(DB_DIR, DB_FILENAME), 'w+b')
    db = btree.open(db_file)
    yield db
    db.close()
    db_file.close()


#@contextmanager
#def open_log_file(fn):
#    try:
#        file = open(fn, 'r')
#    except OSError:
#        file = open(fn, 'a')
#
#    try:
#        yield file
#    finally:
#        file.close()


async def _get_db_entry(key, default=None, as_json=True):
    """
    Get a value out of the database

    :param key: The key to look up
    :param default: The default value if the key doesn't exist
    :param as_json: The value is stored as json, load it into a dict
    :returns: The value in teh database, or None
    """
    if isinstance(key, str):
        key = key.encode('utf8')
    with _get_db() as db:
        value = db.get(key)
    if value and as_json:
        value = json.loads(value.decode('utf8'))
    elif not value:
        value = default
    return value


async def _save_db_entry(key, value):
    """
    Save a value to the database

    :param key: The key to save the data under
    :param value: The value to save, must either be a dict or a str
    """
    if isinstance(key, str):
        key = key.encode('utf8')
    if isinstance(value, str):
        value = value.encode('utf8')
    elif isinstance(value, dict):
        value = json.dumps(value).encode('utf8')
    with _get_db() as db:
        db[key] = value

"""
    DB STRUCTURE
    
    {
        'network': {
                    'ssid': yyyyy,
                    'password': xxxx
        },
        'irrigation_config': {
                    "total_pumps": 3,
                    "pump_info": {
                        1: { 
                            "moisture_threshold": 31,
                            "connected_to_port": "B"
                        },
                        2: {
                            "moisture_threshold": 23,
                            "connected_to_port": "C"
                        },
                        3: {
                            "moisture_threshold": 65,
                            "connected_to_port": "F"
                        }
                    }
        },
        "irrigation_state": {
                        "running": True
        },
        "WebRepl": {
                        "enabled": False,
                        "password": "asdas"
        },
        "smartThings": {
                        "enabled": True,
                        "st_ip": "x.x.x.x"
                        "st_port": "39500"
        }
    }
"""


async def save_network(**kwargs):
    """
    Write the network config to file
    """
    await _save_db_entry('network', kwargs)


async def get_network_config():
    """
    Get the WiFi config. If there is none, return None.
    """
    return await _get_db_entry('network')


async def save_irrigation_config(**kwargs):
    """
    Save the irrigation configuration
    """
    await _save_db_entry('irrigation_config', kwargs)


async def read_irrigation_config():
    """
    Load the irrigation configuration
    """
    return await _get_db_entry('irrigation_config')


async def save_webrepl_config(**kwargs):
    """
    Save the webrepl configuration
    """
    await _save_db_entry('WebRepl', kwargs)


async def read_webrepl_config():
    """
    Load the webrepl configuration
    """
    return await _get_db_entry('WebRepl')


async def save_ftp_config(**kwargs):
    """
    Save the FTP configuration
    """
    await _save_db_entry('ftp', kwargs)


async def read_ftp_config():
    """
    Load the FTP configuration
    """
    return await _get_db_entry('ftp')


async def save_smartthings_config(**kwargs):
    """
    Save the SmartThings configuration
    """
    await _save_db_entry('smartThings', kwargs)


async def read_smartthings_config():
    """
    Load the SmartThings configuration
    """
    return await _get_db_entry('smartThings')


async def save_irrigation_state(**kwargs):
    """
    Save the irrigation status
    """
    await _save_db_entry('irrigation_state', kwargs)


async def read_irrigation_state():
    """
    Load the irrigation status
    """
    return await _get_db_entry('irrigation_state')


async def create_dir(directory):
    folds = directory.split("/")
    root = ""
    try:
        for fld in folds:
            if fld.strip() != "":
                if fld not in uos.listdir(root):
                    root = "{}/{}".format(root, fld)
                    uos.mkdir(root)
                else:
                    root = "{}/{}".format(root, fld)
    except Exception as e:
        raise e
    finally:
        gc.collect()
