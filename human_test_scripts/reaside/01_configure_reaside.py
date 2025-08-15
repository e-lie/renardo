
from renardo.reaper_backend.reaside import configure_reaper, start_reaper, stop_reaper
import time

start_reaper()

time.sleep(5)

configure_reaper()
time.sleep(2)

stop_reaper()
time.sleep(2)
start_reaper()

