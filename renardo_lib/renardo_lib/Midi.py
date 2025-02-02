"""
Module for converting handling MIDI in/out and functions relating to MIDI pitch
calculation.
"""
from renardo_lib.SynthDefManagement import SynthDefProxy
from renardo_lib.Settings import FOXDOT_MIDI_MAPS
from renardo_lib.Utils import midi_cmd

try:
    import rtmidi
    from rtmidi import midiconstants
    TIMING_CLOCK = midiconstants.TIMING_CLOCK
    SONG_POSITION_POINTER = midiconstants.SONG_POSITION_POINTER
    SONG_START = midiconstants.SONG_START
    SONG_STOP = midiconstants.SONG_STOP
    MODULATION = midiconstants.MODULATION
    CONTROL_CHANGE = midiconstants.CONTROL_CHANGE
    CHANNEL_VOLUME = midiconstants.CHANNEL_VOLUME
    EXPRESSION_CONTROLLER = midiconstants.EXPRESSION_CONTROLLER
except ImportError:
    pass
import time
import json
import os
from threading import Thread
from renardo_lib.Code import execute


class MidiInputHandler(object):
    """Midi Handler CallBack Function"""

    def __init__(self, midi_ctrl, port_id=0):
        self.port_id = port_id
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
        if self.print_msg is True:
            print(self.msg)
        if self.msg[0] == 144:
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

        # print(self.msg_list)
        if self.tt and message[0] == 128 and message[1] == 0:
            self.tt_time = time.time()
            if self.tt_ptime < self.tt_time:
                self.tt_bpm = (1/(self.tt_time - self.tt_ptime)) * 60
                self.tt_ptime = self.tt_time

        self.midi_ctrl.delta += delta
        # if TIMING_CLOCK in datatype and not self.played:
        if not self.played:
            self.midi_ctrl.pulse += 1

            if self.midi_ctrl.pulse == self.midi_ctrl.ppqn:
                t_master = 60.0
                self.midi_ctrl.bpm = round(60.0 / self.midi_ctrl.delta, 0)
                self.midi_ctrl.pulse = 0
                self.midi_ctrl.delta = 0.0
                # print("CONTROLLER BPM : " + repr(self.midi_ctrl.bpm))


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
        self.mmap_path = os.path.join(FOXDOT_MIDI_MAPS, "")
        self.mmaps = []
        self.midimap_name = ""
        self.valmap_name = ""
        self.command = ""
        self.name = ""
        self.midimap = {}
        self.valmap = {}
        self.layers = 0
        self.a = ""
        self.new_val = 0
        for map in os.listdir(self.mmap_path):
            if map.endswith(".json"):
                map = os.path.splitext(map)[0]
                self.mmaps.append(map)
        self.mmaps.sort()
        self.pulse = 0
        self.delta = 0.0
        self.bpm = 120.0
        self.ppqn = 24
        self.beat = 0
        self.ctrl_value = 0
        self.note = 0
        self.velocity = 0
        self.handler = MidiInputHandler(self, port_id=port_id)
        self.device.set_callback(self.handler)
        self.msg = self.handler.msg
        self.cur_msg = []
        self.tt_bpm = 120.0
        self.midi_cmd = midi_cmd()
        self.midi_cmd.is_running = False

    @classmethod
    def set_clock(cls, tempo_clock):
        cls.metro = tempo_clock
        return

    # def tempo_tapper(self, tt_bool):
    #     self.handler.tt = tt_bool
    #     return

    # def tempo_tapper_bpm(self):
    #     self.bpm = self.handler.tt_bpm
    #     return self.bpm

    # def get_note(self):
    #     self.note = ()
    #     try:
    #         if len(self.handler.msg_list) > 0:
    #             for i in range(len(self.handler.msg_list)):
    #                 self.note = self.note + (self.handler.msg_list[i][1],)
    #         else:
    #             self.note = self.note + (0, )
    #         return self.note
    #     except Exception:
    #         pass

    # def get_velocity(self):
    #     self.velocity = ()
    #     try:
    #         if len(self.handler.msg_list) > 0:
    #             for i in range(len(self.handler.msg_list)):
    #                 self.velocity = self.velocity + \
    #                     (self.handler.msg_list[i][2] / 64, )
    #         else:
    #             self.velocity = (0, )
    #         return self.velocity
    #     except Exception:
    #         pass

    def get_delta(self):
        self.delta = self.handler.delta
        return self.delta

    def print_message(self, boolmsg):
        self.handler.print_msg = boolmsg
        return self.handler.print_msg

    # def get_value(self, channel):
    #     self.msg = self.handler.msg
    #     for i in range(len(self.handler.msg_list)):
    #         try:
    #             if self.handler.msg_list[i][1] == channel:
    #                 self.msg_value = self.handler.msg_list[i][2]
    #             return self.msg_value
    #         except Exception:
    #             pass

    def midimaps(self):
        # Show all available midi maps
        print(self.mmaps)

    # Loads the midimap file and returns it as dictionary
    def load_midimap(self, id=0):
        # Use position in midimaps to load the responding json into dictionary
        path = self.mmap_path+self.mmaps[id]+".json"
        with open(path) as json_file:
            data = json.load(json_file)
            self.midimap_name = list(data.keys())[0]
            self.midimap = data.get(self.midimap_name)
        return self.midimap

    # Loads the valmap file and returns it as dictionary
    def load_valmap(self, path, layers=3):
        self.valstore = {}
        self.valmap = {}
        self.layers = layers
        self.valmap_name = ""
        try:
            # Open the json file and read it into a dictionary
            with open(path) as json_file:
                data = json.load(json_file)
                try:
                    self.valmap_name = list(data.keys())[0]
                    self.valmap = data.get(self.valmap_name)
                    for key in self.valmap.keys():
                        if self.valmap[key][0] == "Switch" or self.valmap[key][0] == "Count":
                            self.valstore[key] = 0
                        else:
                            rng = self.valmap[key][0]
                            if rng == "0-127" or rng == "-64-64":
                                self.valstore[key] = [[], 0]
                                for i in range(self.layers):
                                    self.valstore[key][0].append(0)
                except Exception:
                    print("This ValMap is compromised or empty!")
            return self.valmap
        except FileNotFoundError:
            # If there is no file, that is given by path
            print("No file found. Please check given path/file.json")

    def del_value(self, name, attr):
        self.valmap[name][1].pop(attr)

    # Add values by giving name of MidiMap element, attribute, min value
    # und max value
    def set_value(self, name, attr, list):
        if bool(self.valmap) is False:
            print("Please use load_valmap(path) function first to load a map!")
        else:
            etype = self.valmap[name][0]
            if etype != "Count" and etype != "Switch" and etype != "Push":
                if len(list) == 3:
                    self.valmap[name][1][attr] = list
                else:
                    print("Create list with minimum, maximum, and default value of the attribute.")
            elif etype == "Count":
                if attr == "Group":
                    self.valmap[name][1][attr] = list
                else:
                    print("Remember use name 'Group' as attribute. Set all element names in a list, e.g. ['U1:E0', 'U1:E1', 'U1:E2'], in order to make it work.")
            elif etype == "Push" or etype == "Switch":
                if len(list) == 2:
                    if self.valmap[name][1] != {}:
                        self.valmap[name][1].popitem()
                    self.valmap[name][1][attr] = list
                else:
                    print("List too big. Set a list with [on, off(default)] values of an attribute!")
            else:
                print("This element is not a ctrl or value type. Please check your valmap again by using print(valmap_variable_name)!")

    def get_value(self, name):
        try:
            print(self.valmap[name])
        except Exception:
            print(f"Element {name} not used yet.")

    def save_valmap(self, valmap_path=""):
        if valmap_path == "":
            print("Please add '/path/filename.json' to save your valmap!")
        else:
            with open(valmap_path, "w") as outfile:
                new_map = {}
                new_map[self.valmap_name] = self.valmap
                json.dump(new_map, outfile, indent=4)
            print("ValMap saved as " + valmap_path)

    def run(self):
        if self.valmap == {} or self.midimap == {}:
            # There must be a value map and a midi map loaded as dictionary
            print("Please load a midimap and a valmap first, before you start")
        else:
            # If midi Handler returns a message, check name for channel
            # in midimap, then return value from valmap
            self.midi_cmd.is_running = True
            self.update_thread = Thread(target=self.update_val)
            self.update_thread.setDaemon(True)
            self.update_thread.start()

    def update_val(self):
        while self.midi_cmd.is_running:
            # Check if midi message has changed
            if self.handler.msg != self.cur_msg:
                # Get channel from midi message
                state = self.handler.msg[0]
                channel = self.handler.msg[1]
                value = self.handler.msg[2]
                rtype = ""
                # Get name and range type from midimap through channel
                for key, cc in self.midimap.items():
                    if cc[1] == channel:
                        if state <= 175 and ((cc[2] == "Push") or (cc[2] == "Switch") or (cc[2] == "Count")):
                            self.name = key
                            rtype = cc[2]
                        elif state > 175 and ((cc[2] == "0-127") or (cc[2] == "-64-64")):
                            self.name = key
                            rtype = cc[2]
                        else:
                            pass
                # Categories by rtype
                if rtype == "Push":
                    if state >= 144:
                        try:
                            self.a = list(self.valmap[self.name][1].keys())[0]
                            self.new_val = self.valmap[self.name][1][self.a][0]
                            self.command = f"{self.a}={self.new_val}"
                            self.midi_exe(self.command)
                            self.midi_cmd.set_msg([self.name,
                                                   self.command])
                        except Exception:
                            pass
                    else:
                        try:
                            self.a = list(self.valmap[self.name][1].keys())[0]
                            self.new_val = self.valmap[self.name][1][self.a][1]
                            self.command = f"{self.a}={self.new_val}"
                            self.midi_exe(self.command)
                            self.midi_cmd.set_msg([self.name, self.command])
                        except Exception:
                            pass
                # If switch button is pressed dwn
                # select attribute value on, and next time off
                elif rtype == "Switch":
                    if state >= 144:
                        try:
                            attr = list(self.valmap[self.name][1].keys())[0]
                            if attr != "":
                                if self.valstore[self.name] == 1:
                                    self.new_val = self.valmap[self.name][1][attr][0]
                                    self.valstore[self.name] = 0
                                elif self.valstore[self.name] == 0:
                                    self.new_val = self.valmap[self.name][1][attr][1]
                                    self.valstore[self.name] = 1
                                self.valstore[attr] = self.new_val
                                self.command = f"{attr}={self.new_val}"
                                self.midi_exe(self.command)
                                self.midi_cmd.set_msg([self.name,
                                                       self.command,
                                                       ])
                        except Exception:
                            pass
                elif rtype == "Count":
                    if state >= 144:
                        try:
                            element_list = self.valmap[self.name][1]["Group"]
                            if self.valstore[self.name] < self.layers - 1:
                                num = self.valstore[self.name]
                                num += 1
                                self.valstore[self.name] = num
                                for element in element_list:
                                    self.valstore[element][1] = num
                            else:
                                self.valstore[self.name] = 0
                                for element in element_list:
                                    self.valstore[element][1] = 0
                            try:
                                for element in element_list:
                                    self.command = ""
                                    cnt_num = self.valstore[self.name]
                                    attr = list(self.valmap[element][1].keys())[cnt_num]
                                    if attr == "":
                                        pass
                                    else:
                                        new_val = self.valstore[element][0][self.valstore[element][1]]
                                        self.command = f"{attr}={new_val}"
                                        self.midi_exe(self.command)
                                        self.midi_cmd.set_msg([self.name,
                                                               self.command,
                                                               cnt_num])
                            except Exception:
                                pass
                        except Exception:
                            print("Error Count")
                elif rtype == "0-127" or rtype == "-64-64":
                    try:
                        if rtype == "0-127":
                            vrange_min = 0
                            vrange_max = 127
                        elif rtype == "-64-64":
                            vrange_min = -64
                            vrange_max = 64
                        else:
                            print("Please only use types of 0-127 or -64-64")
                        rng = list(self.valmap[self.name][1].keys())[0]
                        if rng == "Group":
                            element_list = self.valmap[self.name][1][rng]
                            self.command = ""
                            for element in element_list:
                                cnt_num = self.valstore[element][1]
                                try:
                                    attr = list(self.valmap[element][1].keys())[cnt_num]
                                    # Map min and max to value range
                                    self.new_val = self.mapFromTo(float(value),
                                                                  vrange_min,
                                                                  vrange_max,
                                                                  self.valmap[element][1][attr][2],
                                                                  self.valstore[element][0][cnt_num])
                                    self.new_val = round(self.new_val, 3)
                                    self.command = self.command + f"{attr}={self.new_val}; "
                                    self.midi_exe(self.command)
                                    unit = self.name.split(":")[0]
                                    new_val = round(value/127, 3)
                                    ufader = f"{unit}={new_val}"
                                    self.midi_cmd.set_msg([self.name,
                                                           ufader,
                                                           cnt_num])
                                except Exception:
                                    pass

                        else:
                            cnt_num = self.valstore[self.name][1]
                            try:
                                attr = list(self.valmap[self.name][1].keys())[cnt_num]
                                # Map min and max to value range
                                self.new_val = self.mapFromTo(float(value),
                                                              vrange_min,
                                                              vrange_max,
                                                              self.valmap[self.name][1][attr][0],
                                                              self.valmap[self.name][1][attr][1])
                                self.new_val = round(self.new_val, 3)
                                self.command = f"{attr}={self.new_val}"
                                self.valstore[self.name][0][cnt_num] = self.new_val
                                self.midi_exe(self.command)
                                self.midi_cmd.set_msg([self.name,
                                                       self.command,
                                                       cnt_num])
                            except Exception:
                                print(f"Slot: {cnt_num} empty")
                    except Exception:
                        print(f"{self.name} empty")
                else:
                    pass
                # Update message to compare with new incoming message
                self.cur_msg = self.handler.msg
            # Wait a little
            time.sleep(0.1)

    def midi_exe(self, command):
        # Execute new attribute value
        execute(command, verbose=False)

    def mapFromTo(self, x, a, b, c, d):
        value = (x-a)/(b-a)*(d-c)+c
        return value

    def stop(self):
        self.midi_cmd.is_running = False
        self.update_thread.join()

    def close(self):
        """ Closes the active port """
        if self.midi_cmd.is_running:
            self.midi_cmd.is_running = False
            self.update_thread.join()
        self.device.close_port()
        return


class MidiOut(SynthDefProxy):
    """ SynthDef proxy for sending midi message via supercollider """
    def __init__(self, degree=0, **kwargs):
        SynthDefProxy.__init__(self, self.__class__.__name__, degree, kwargs)


midi = MidiOut  # experimental alias
# Midi information exceptions


class MIDIDeviceNotFound(Exception):
    def __str__(self):
        return self.__class__.__name__ + " Error"


class rtMidiNotFound(Exception):
    def __str__(self):
        return self.__class__.__name__ + ": Module 'rtmidi' not found"


if __name__ == "__main__":
    a = MidiIn()
