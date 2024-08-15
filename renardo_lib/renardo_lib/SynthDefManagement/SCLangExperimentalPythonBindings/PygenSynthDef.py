import os

from renardo_lib.SynthDefManagement.SynthDict import SynthDefs
from renardo_lib.SynthDefManagement.SynthDefProxy import SynthDefProxy
from renardo_lib.SynthDefManagement.SCLangExperimentalPythonBindings import format_args, Env
from renardo_lib.SynthDefManagement.SCLangExperimentalPythonBindings.core import instance
from renardo_lib.ServerManager.default_server import Server
from renardo_lib.Settings import TMP_SYNTHDEF_DIR
from renardo_lib.Code import WarningMsg


class PygenSynthDefBaseClass(object):
    """
    Python generated synthdef synthetizer using SCLang bindings
    This writes a .scd supercollider file before loading it in
    the sclang server via OSCFunc
    This is the legacy mode of FoxDot
    """

    server = Server
    bus_name = 'bus'
    var = ['osc', 'env']
    defaults = {}
    container = SynthDefs
    default_env = Env.perc()

    def __init__(self, name):
        # String name of SynthDef
        self.name = name
        # Flag when Synth added to server
        self.synth_added = False
        # Initial behaviour such as amplitude / frequency modulation
        self.base = ["sus = sus * blur;"]
        self.attr = [] # stores custom attributes

        # Name of the file to store the SynthDef
        self.filename     = TMP_SYNTHDEF_DIR + "/{}.scd".format(self.name)

        # SynthDef default arguments
        self.osc         = instance("osc")
        self.freq        = instance("freq")
        self.fmod        = instance("fmod")
        self.output      = instance("output")
        self.sus         = instance("sus")
        self.amp         = instance("amp")
        self.pan         = instance("pan")
        self.rate        = instance("rate")
        self.blur        = instance("blur")
        self.beat_dur    = instance("beat_dur")

        # Envelope
        self.atk         = instance("atk")
        self.decay       = instance("decay")
        self.rel         = instance("rel") 

        self.defaults = {   "amp"       : 1,
                            "sus"       : 1,
                            "pan"       : 0,
                            "freq"      : 0,
                            "vib"       : 0,
                            "fmod"      : 0,
                            "rate"      : 0,
                            "bus"       : 0,
                            "blur"      : 1,
                            "beat_dur"  : 1,
                            "atk"       : 0.01,
                            "decay"     : 0.01,
                            "rel"       : 0.01,
                            "peak"      : 1,
                            "level"     : 0.8 }

        # The amp is multiplied by this before being sent to SC
        self.balance = 1

        # Add to list
        self.container[self.name] = self

        self.add_base_class_behaviour()

    # Context Manager
    # ---------------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.add()


    # String representation
    # ---------------------
    def __str__(self):
        Def  = "SynthDef.new(\\{},\n".format(self.name)
        Def += "{}|{}|\n".format("{", format_args(kwargs=self.defaults, delim='='))
        Def += "{}\n".format(self.get_base_class_variables())
        Def += "{}\n".format(self.get_base_class_behaviour())
        Def += "{}".format(self.get_custom_behaviour())
        Def += "osc = Mix(osc) * 0.5;\n"
        Def += "osc = Pan2.ar(osc, pan);\n"
        Def += "\tReplaceOut.ar(bus, osc)"
        Def += "}).add;\n"
        return Def

    def __repr__(self):
        return str(self.name)


    ## Combining with other SynthDefs
    ## ------------------------------
    #def __add__(self, other):
    #    if not isinstance(other, DefaultSynthDef):
    #        raise TypeError("Warning: '{}' is not a SynthDef".format(str(other)))
    #    new = copy(self)
    #    new.osc = self.osc + other.osc
    #    return new


    # Returning the SynthDefProxy
    # ---------------------------
    def __call__(self, degree=None, **kwargs):
        return SynthDefProxy(self.name, degree, kwargs)

    # Getter and setter
    # -----------------
    def __getattribute__(self, key):
        if key.startswith("_"):
            return object.__getattribute__(self, key)

        defaults    = object.__getattribute__(self, 'defaults')
        var         = object.__getattribute__(self, 'var')
        synth_added = object.__getattribute__(self, 'synth_added')

        attr = list(defaults.keys()) + var

        if synth_added:
            return object.__getattribute__(self, key)
        elif key in attr:
            return instance(key)
        else:
            return object.__getattribute__(self, key)
        raise AttributeError("Attribute '{}' not found".format(key))

    def __setattr__(self, key, value):
        try:
            if key in self.var + list(self.defaults.keys()):
                self.attr.append((key, value))
        except:
            pass
        if key not in self.__dict__ or str(key) != str(value):
            self.__dict__[key] = value


    # Defining class behaviour
    # ------------------------

    def add_base_class_behaviour(self):
        """ Defines the initial setup for every SynthDef """
        return

    def get_base_class_behaviour(self):
        return "\n".join(self.base)

    def get_base_class_variables(self):
        return "var {};".format(", ".join(self.var))

    def get_custom_behaviour(self):
        string = ""
        for arg, value in self.attr:
            arg, value = str(arg), str(value)
            if arg != value:
                string += (arg + '=' + value + ';\n')
        return string

    def get_custom_behaviour2(self):
        string = ""
        for arg in list(self.defaults.keys()) + self.var:
            if arg in self.__dict__:
                # Don't add redundant lines e.g. sus=sus;
                if str(arg) != str(self.__dict__[arg]):
                    string += (str(arg) + '=' + str(self.__dict__[arg]) + ';\n')
        return string

    def adsr(self, **kwargs):
        """ Define the envelope """
        self.defaults.update(**kwargs)
        self.env = Env.adsr()
        return


    # Adding the SynthDef to the Server
    # ---------------------------------

    def write(self):
        """  Writes the SynthDef to file """
        # 1. See if the file exists
        if os.path.isfile(self.filename):
            with open(self.filename) as f:
                contents = f.read()
        else:
            contents = ""

        # 2. If it does, check contents
        this_string = self.__str__()

        if contents != this_string:
            try:
                with open(self.filename, 'w') as f:
                    f.write(this_string)
            except IOError:
                # print("Warning: Unable to update '{}' SynthDef.".format(self.name))
                pass # TODO - add python -m --verbose to print warnings?
        return

    def has_envelope(self):
        try:
            object.__getattribute__(self, 'env')
            return True
        except:
            return False

    def load(self):
        """ Load in server"""
        return DefaultPygenSynthDef.server.loadSynthDef(self.filename)

    def add(self):
        """ This is required to add the SynthDef to the SuperCollider Server """
        if self.has_envelope():
            self.osc = self.osc * self.env
        try:
            self.synth_added = True
            # Load to server
            self.write()
            self.load()
        except Exception as e:
            WarningMsg("{}: SynthDef '{}' could not be added to the server:\n{}".format(e.__class__.__name__, self.name, e))
        return None

    #def rename(self, newname):
    #    new = copy(self)
    #    new.name = str(newname)
    #    return new

    @staticmethod
    def new_attr_instance(name):
        return instance(name)

    #def play(self, freq, **kwargs):
    #    ''' Plays a single sound '''
    #    message = ["freq", freq]
    #    for key, value in kwargs.items():
    #        message += [key, value]
    #    self.server.sendNote(self.name, message)
    #    return

    def preprocess_osc(self, osc_message):
        osc_message['amp'] *= self.balance

class DefaultPygenSynthDef(PygenSynthDefBaseClass):
    def __init__(self, *args, **kwargs):
        PygenSynthDefBaseClass.__init__(self, *args, **kwargs)
        # add vib depth?

    def add_base_class_behaviour(self):
        """ Defines the initial setup for every SynthDef """
        PygenSynthDefBaseClass.add_base_class_behaviour(self)
        self.base.append("freq = In.kr(bus, 1);")
        self.base.append("freq = [freq, freq+fmod];")
        return
