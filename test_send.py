import time
import logging
from renardo.runtime import *

# Set logging level to DEBUG to see all messages
logging.getLogger('renardo').setLevel(logging.DEBUG)
logging.getLogger('renardo.reaper_backend').setLevel(logging.DEBUG)
logging.getLogger('renardo.reaside').setLevel(logging.DEBUG)

# Add console handler if not present
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(name)s] %(levelname)s: %(message)s')
console_handler.setFormatter(formatter)

# Add handler to all relevant loggers
for logger_name in ['renardo.reaper_backend.reaper_music_resource', 
                     'renardo.reaside.core.param',
                     'renardo.reaside.core.track',
                     'renardo.reaside.tools.reaper_client']:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

print("=== Starting send test ===")

reaproject.clear_reaper()

bass303 = ReaperInstrument(
    shortname='bass303',
    fullname='Bass 303',
    description='Acid bass with TB-303 resonance',
    fxchain_path='bass303.RfxChain',
    arguments={},
    bank='0_renardo_core',
    category='bass'
)

print("\n=== Creating bus track 'cool' ===")
reaproject.create_bus_track("cool")

# Check if sends were created
print("\n=== Checking sends on bass303 track ===")
if hasattr(bass303, '_reatrack'):
    print(f"Track sends dict: {bass303._reatrack.sends}")
    print(f"Track sends keys: {list(bass303._reatrack.sends.keys())}")
else:
    print("No _reatrack attribute on bass303")

print("\n=== Setting cool send to 1 ===")
b1 >> bass303([0,4,5,3], cool=1, amp=1)
time.sleep(2)

print("\n=== Setting cool send to 0.5 ===")
b1 >> bass303([0,4,5,3], cool=0.5, amp=1)
time.sleep(2)

print("\n=== Test complete ===")