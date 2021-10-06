# This file is executed on every boot (including wake-boot from deepsleep)
import gc
import micropython


micropython.alloc_emergency_exception_buf(200)
gc.collect()
