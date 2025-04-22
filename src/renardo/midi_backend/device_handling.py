import mido
import time
from mido.backends.rtmidi import Output


def display_output_devices():
    print(mido.get_output_names())

def select_output_device(device_index: int):
    try:
        selected_device = mido.open_output(mido.get_output_names()[device_index])
        return selected_device
    except IndexError as e:
        print(f"MIDI device of index {device_index} not found !")
    return None

def send_short_note(output_device: Output):
        print(output_device)
        note = 60  # middle C
        velocity = 64  # medium velocity
        channel = 0  # MIDI channel 1 (zero-indexed)
        note_on = mido.Message('note_on', channel=channel, note=note, velocity=velocity)
        output_device.send(note_on)
        print(f"Sent note_on: note={note}, velocity={velocity}")
        time.sleep(.2)
        # Create and send noteOff message
        note_off = mido.Message('note_off', channel=channel, note=note, velocity=0)
        output_device.send(note_off)
        print(f"Sent note_off: note={note}")
        # Close the port
        output_device.close()
        print("Port closed")