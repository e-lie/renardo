""" Module for converting handling MIDI in/out and functions relating to MIDI pitch calculation. """


from renardo.lib.InstrumentProxy import InstrumentProxy

try:
    import rtmidi
    from rtmidi import midiconstants
    TIMING_CLOCK          = midiconstants.TIMING_CLOCK
    SONG_POSITION_POINTER = midiconstants.SONG_POSITION_POINTER
    SONG_START            = midiconstants.SONG_START
    SONG_STOP             = midiconstants.SONG_STOP 
except ImportError as _err:
    pass

import time


class MidiInputHandler(object):

    """Midi Handler CallBack Function"""

    def __init__(self, midi_ctrl):

        self.midi_ctrl = midi_ctrl
        self.bpm_group = []
        self.played = False
        self.bpm = 120.0
        self.tt = False
        self.tt_bpm = self.bpm
        self.tt_time = time.time()
        self.tt_ptime = self.tt_time
        self.msg = [0, 0, 0]
        self.msg_list = []
        self.print_msg = False

    def __call__(self, event, data=None):

        message, delta = event

        self.msg = message

        if self.print_msg == True:
            print(self.msg)

        if(self.msg[0] == 144 or self.msg[0] == 145):
            if len(self.msg_list) == 0:
                self.msg_list.append(self.msg)
            else:
                if self.msg not in self.msg_list:
                    self.msg_list.append(self.msg)
        elif self.msg[0] == 128:
            if len(self.msg_list) > 0:
                for count, item in enumerate(self.msg_list):
                    if self.msg[1] == item[1]:
                        self.msg_list.remove(self.msg_list[count])
        elif self.msg[0] == 129:
            for count, item in enumerate(self.msg_list):
                if self.msg[1] == item[1]:
                    self.msg_list[count][2] = 0
        else:
            if len(self.msg_list) == 0:
                self.msg_list.append(self.msg)
            else:
                if self.msg not in self.msg_list:
                    self.msg_list.append(self.msg)
                else:
                    for count, item in enumerate(self.msg_list):
                        if self.msg[1] == item[1]:
                            self.msg_list.remove(self.msg_list[count])
                            self.msg_list.append(self.msg)

        #print(self.msg_list)

        if self.tt and message[0] == 128 and message[1] == 0:
            self.tt_time = time.time()
            if self.tt_ptime < self.tt_time:
                self.tt_bpm = (1/(self.tt_time - self.tt_ptime)) * 60
                self.tt_ptime = self.tt_time

        self.midi_ctrl.delta += delta

        #if TIMING_CLOCK in datatype and not self.played:
        if not self.played:
            self.midi_ctrl.pulse += 1
            

            if self.midi_ctrl.pulse == self.midi_ctrl.ppqn:

                t_master = 60.0
                
                self.midi_ctrl.bpm = round(60.0 / self.midi_ctrl.delta,0)

                self.midi_ctrl.pulse = 0
                self.midi_ctrl.delta = 0.0

                #print("CONTROLLER BPM : " + repr(self.midi_ctrl.bpm))


class MidiIn:
    metro = None
    def __init__(self, port_id=0):
        """ Class for listening for MIDI clock messages
            from a midi device """
        try:

            self.device = rtmidi.MidiIn()

        except NameError:

            raise ImportError("Rtmidi not imported")

        self.available_ports = self.device.get_ports()

        if not self.available_ports:

            raise MIDIDeviceNotFound

        else:

            print("MidiIn: Connecting to " + self.available_ports[port_id])

        self.device.open_port(port_id)
        self.device.ignore_types(timing=False)


        self.pulse = 0
        self.delta = 0.0
        self.bpm = 120.0
        self.tt_bpm = 120.0
        self.ppqn = 24
        self.beat = 0
        self.ctrl_value = 0
        self.note = 0
        self.velocity = 0
        self.handler = MidiInputHandler(self)
        self.device.set_callback(self.handler)
        self.msg = self.handler.msg

    @classmethod
    def set_clock(cls, tempo_clock):
        cls.metro = tempo_clock
        return

    def tempo_tapper(self, tt_bool):
        self.handler.tt = tt_bool
        return

    def tempo_tapper_bpm(self):
        self.bpm = self.handler.tt_bpm
        return self.bpm

    def get_ctrl(self, channel):
        for i in range(len(self.handler.msg_list)):
            if self.handler.msg_list[i][1] == channel:
                self.ctrl_value = self.handler.msg_list[i][2]
        return self.ctrl_value

    def get_note(self):
        self.note = ()
        if len(self.handler.msg_list) > 0:
            for i in range(len(self.handler.msg_list)):
                self.note = self.note + (self.handler.msg_list[i][1],)
        else:
            self.note = self.note + (0, )
        return self.note

    def get_velocity(self):
        self.velocity = ()
        if len(self.handler.msg_list) > 0:
            for i in range(len(self.handler.msg_list)):
                self.velocity = self.velocity + \
                    (self.handler.msg_list[i][2] / 64, )
        else:
            self.velocity = (0, )
        return self.velocity

    def get_delta(self):
        self.delta = self.handler.delta
        return self.delta

    def print_message(self, boolmsg):
        self.handler.print_msg = boolmsg
        return self.handler.print_msg

    def close(self):
        """ Closes the active port """
        self.device.close_port()
        return

class MidiInstrumentProxy(InstrumentProxy):
    """ Instrument proxy for sending midi message via supercollider """
    def __init__(self, degree=0, **kwargs):
        InstrumentProxy.__init__(self, self.__class__.__name__, degree, kwargs)

class ReaperInstrumentProxy(MidiInstrumentProxy):
    """Instrument proxy to handle MIDI + reaper integration"""
    def __init__(self, degree=0, **kwargs):
        if isinstance(degree, str) and "midi_map" not in kwargs.keys():
            raise Exception("No midi map defined to translate playstring")
        MidiInstrumentProxy.__init__(self, degree, **kwargs)


midi = MidiOut = MidiInstrumentProxy # experimental alias

# Midi information exceptions

class MIDIDeviceNotFound(Exception):
    def __str__(self):
        return self.__class__.__name__ + " Error"

class rtMidiNotFound(Exception):
    def __str__(self):
        return self.__class__.__name__ + ": Module 'rtmidi' not found"


if __name__ == "__main__":

    a = MidiIn()
