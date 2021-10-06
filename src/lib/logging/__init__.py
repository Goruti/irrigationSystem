import gc
import utime
import sys
import uio

CRITICAL = 50
ERROR    = 40
WARNING  = 30
INFO     = 20
DEBUG    = 10
NOTSET   = 0

_level_dict = {
    CRITICAL: "CRITICAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG",
}

class Logger:

    level = NOTSET

    def __init__(self, name):
        self.name = name
        self.handlers = None
        self.parent = None

    def _level_str(self, level):
        l = _level_dict.get(level)
        if l is not None:
            return l
        return "LVL%s" % level

    def setLevel(self, level):
        self.level = level

    def isEnabledFor(self, level):
        return level >= self.level

    def log(self, level, msg, *args):
        gc.collect()
        dest = self
        ct = "{0}-{1}-{2} {3}:{4}:{5}".format(*utime.localtime())

        while dest.level == NOTSET and dest.parent:
            dest = dest.parent
        if level >= dest.level:
            msg = "{}, {}, {}, mem_free: {}, {}".format(ct, self.name, _level_dict.get(level, None), gc.mem_free(), msg)
            if args:
                msg = msg % args
            if dest.handlers:
                for hdlr in dest.handlers:
                    hdlr.emit(msg)
        gc.collect()

    def debug(self, msg, *args):
        self.log(DEBUG, msg, *args)

    def info(self, msg, *args):
        self.log(INFO, msg, *args)

    def warning(self, msg, *args):
        self.log(WARNING, msg, *args)

    def error(self, msg, *args):
        self.log(ERROR, msg, *args)

    def critical(self, msg, *args):
        self.log(CRITICAL, msg, *args)

    def exc(self, e, msg, *args):
        buf = uio.StringIO()
        sys.print_exception(e, buf)
        self.log(ERROR, msg + "\n" + buf.getvalue(), *args)

    def exception(self, msg, *args):
        raise NotImplementedError()

    def addHandler(self, hdlr):
        if self.handlers is None:
            self.handlers = []
        self.handlers.append(hdlr)


def getLogger(name=None):
    if name is None:
        name = "root"
    if name in _loggers:
        return _loggers[name]
    l = Logger(name)
    # For now, we have shallow hierarchy, where parent of each logger is root.
    l.parent = root
    _loggers[name] = l
    return l


def info(msg, *args):
    getLogger(None).info(msg, *args)


def debug(msg, *args):
    getLogger(None).debug(msg, *args)


def warning(msg, *args):
    getLogger(None).warning(msg, *args)


def error(msg, *args):
    getLogger(None).error(msg, *args)


def critical(msg, *args):
    getLogger(None).critical(msg, *args)


def exception(msg, *args):
    getLogger(None).exception(msg, *args)


def basicConfig(level=INFO, filename=None, stream=None, format=None):
    root.setLevel(level)
    assert filename is None  # filename is not supported, you need to add it manually afterward using RotatingFileHandler
    assert format is None  # format is not supported
    h = StreamHandler(stream)
    root.handlers.clear()
    root.addHandler(h)


class StreamHandler():
    def __init__(self, stream=None):
        super().__init__()
        self._stream = stream or sys.stderr
        self.terminator = "\n"

    def emit(self, record):
        self._stream.write(record + self.terminator)

    def flush(self):
        pass

root = Logger("root")
root.setLevel(WARNING)
sh = StreamHandler()
root.addHandler(sh)
_loggers = {"root": root}