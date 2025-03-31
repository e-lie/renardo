
try:
    import mido
    import jack
    class MIDIddleware:
        def __init__(self, current_outchannel=0, root=0, scale=[0,1,2,3,4,5,6,7,8,9,10,11]):
            self.rtmidi = mido.Backend('mido.backends.rtmidi')
            self.inport = self.rtmidi.open_input("MIDIdlewareIN", virtual=True)
            self.outport = self.rtmidi.open_output("MIDIdlewareOUT", virtual=True)
            self.current_outchannel = current_outchannel
            self.transpose_mode = None
            self.auto_connect()
            self.state = "base"
            self.root = root
            self.scale = scale
            self.inport.callback = self.update_msg

        def auto_connect(self):
            def connect_from_dict(connection_dict):
                client=jack.Client("jack_python_connector", "jack_python_connector")
                for out_port_name, in_port_names in connection_dict.items():
                    if isinstance(in_port_names, str):
                        in_port_names = [in_port_names]
                    for in_port_name in in_port_names:
                        out_ports = client.get_ports(name_pattern=f"^{out_port_name}$")
                        in_ports = client.get_ports(name_pattern=f"^{in_port_name}$")
                        # try:
                            # assert len(out_ports) == 1
                            # assert len(in_ports) == 1
                        for oport in out_ports:
                            for iport in in_ports:
                                try:
                                    client.connect(oport, iport)
                                    print(f"{out_port_name} -> {in_port_name}")
                                except:
                                    print(f"Error connecting     {out_port_name} -> {in_port_name} --- Skipping")
                            # out_port = out_ports[0]
                            # in_port = in_ports[0]
                            # client.connect(out_port, in_port)
                        # print(f"{out_port_name} -> {in_port_name}")
                        # except:
                            # print(f"Error connecting     {out_port_name} -> {in_port_name} --- Skipping")
            connections = {
                ".*MIDIdlewareOUT.*": "REAPER:MIDI Input 1",
                ".*MPK mini 3.*capture.*": ".*MIDIdlewareIN.*",
            }
            connect_from_dict(connections)

        def update_msg(self, msg):
            if msg.type == "program_change":
                # print(self.state)
                if self.state == "base":
                    if msg.program % 8 == 0: # modulo 8 to "disable" bank A/B switch when selecting the mode
                        self.state = "channel_select"
                    if msg.program % 8 == 1: # modulo 8 to "disable" bank A/B switch when selecting the mode
                        self.state = "transpose_mode_select"
                elif self.state == "channel_select":
                    self.current_outchannel = msg.program
                    self.state = "base"
                elif self.state == "transpose_mode_select":
                    if msg.program == 0:
                        self.transpose_mode = None
                    elif msg.program == 1:
                        self.transpose_mode = "scale_and_root"
                    elif msg.program == 2:
                        self.transpose_mode = "root_only"
                    elif msg.program == 3:
                        self.transpose_mode = "scale_only"
                    self.state = "base"
            msg.channel = self.current_outchannel    
            # print(msg)
            if "note_" in msg.type:
                # transpose note in current scale and root
                if self.transpose_mode == "scale_and_root":
                    msg.note = self.midinote_in_current_scale_and_root(msg.note, scale=self.scale, root=self.root)
                if self.transpose_mode == "root_only":
                    msg.note = self.midinote_in_current_scale_and_root(msg.note, scale=list(range(12)), root=self.root)
                if self.transpose_mode == "scale_only":
                    msg.note = self.midinote_in_current_scale_and_root(msg.note, scale=self.scale, root=0)
            # print(msg)
            # print(self.current_outchannel)
            self.outport.send(msg)

        def midinote_in_current_scale_and_root(self, midinote, scale, root):
            "force midinote to be played in some Scale and at some root (shift/transpose)"
            scale = list(scale)*5
            root = int(root)
            steps_per_octave = 12
            degree_chromatic = midinote % steps_per_octave # note number in nearest octave in chromatic numbering
            octave = midinote // steps_per_octave
            res = None
            for i,d in enumerate(scale[:-1]):
                if degree_chromatic == d:
                    res = midinote + root # no scale translation to do but still root transpose
                    break
                elif degree_chromatic > d and degree_chromatic < scale[i+1]:
                    distance_to_d = abs(d - degree_chromatic)
                    distance_d_dnext = abs(scale[i+1] - d)
                    degree_in_scale = i + distance_to_d / distance_d_dnext # example degree 2.5 in scale minor is 4 in degree chromatic because mid distance between 2nd and 3rd note
                    res = scale[round(degree_in_scale)] + octave * steps_per_octave + int(root) # round degree in scale to force it to play in the scale
                    res = int(res) # in case of scale Pvar, scale[i] is a ChildTimevar to convert to int
                    break
            if res is None: # if degree_chromatic > max(scale) => use the last degree of the scale
                res = scale[-1] + octave * steps_per_octave
                res = int(res)
            return res

### TODO
#
# - try to fix not consistent note_off message by handling note_off as a sort of callback using a buffer of entering notes
# - add a kill all remaining notes in buffer 
# - The missing record function !! use Clock.now() and the Clock phase to record durations and produce a ZPattern
# - Fix bug of
#

except Exception as e:
    print("Jack client lib or mido not available. Aborting MIDIddleware...")