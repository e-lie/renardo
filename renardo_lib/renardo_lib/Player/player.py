import itertools
from .rest import rest

from renardo_sc_backend import SamplePlayer, LoopPlayer
from renardo_sc_backend import buffer_manager
from renardo_lib.SynthDefManagement.SCLangExperimentalPythonBindings.PygenSynthDef import (
    DefaultPygenSynthDef,
)
from renardo_lib.SynthDefManagement import SynthDefProxy
from renardo_lib.SynthDefManagement.SynthDict import SynthDefs
from renardo_lib.runtime.synthdefs_initialisation import effect_manager
from renardo_lib.Key import PlayerKey, NumberKey
from renardo_lib.Repeat import Repeatable
from renardo_lib.Patterns import (
    Pattern, PGroup, asStream, PRand, PGroupPrime, pattern_depth,
    GeneratorPattern, modi, group_modi, PwRand, choice
)
from renardo_lib.Root import Root
from renardo_lib.Scale import Scale, get_freq_and_midi
from renardo_lib.Bang import Bang
from renardo_lib.TimeVar import TimeVar, mapvar, linvar, inf, var
from renardo_lib.Code import WarningMsg
from renardo_lib.Utils import get_first_item, get_expanded_len

from renardo_reaper.ReaperIntegrationLib.ReaProject import get_reaper_object_and_param_name, set_reaper_param, get_reaper_param
from renardo_reaper.ReaperIntegrationLib.ReaTrack import ReaTrack


class Player(Repeatable):
    """
    FoxDot generates music by creating instances of `Player` and giving them instructions
    to follow. At startup FoxDot creates many instances of `Player` and assigns them to
    any valid two character variable. This is so that when you start playing you don't
    have to worry about typing `myPlayer = Player()` and `myPlayer_2 = Player()` every
    time you want to do something new. Of course there is nothing stopping you from
    doing that if yo so wish.

    Instances of `Player` are given instructions to generate music using the `>>` syntax,
    overriding the bitshift operator, and should be given an instance of `SynthDefProxy`.
    A `SynthDefProxy` is created when calling an instance of `SynthDef` - these are the
    "instruments" used by player objects and are written in SuperCollider code. You can
    see more information about these in the `SynthDefManagement` module. Below describes how to assign
    a `SynthDefProxy` of the `SynthDef` `pads` to a `Player` instance called `p1`: ::

        # Calling pads as if it were a function returns a
        # pads SynthDefProxy object which is assigned to p1
        p1 >> pads()

        # You could store several instances and assign them at different times
        proxy_1 = pads([0,1,2,3], dur=1/2)
        proxy_2 = pads([4,5,6,7], dur=1)

        p1 >> proxy_1 # Assign the first to p1
        p1 >> proxy_2 # This replaces the instructions being followed by p1
    """

    debug = 0
    __vars = []
    __init = False

    keywords = (
        "degree",
        "oct",
        "freq",
        "dur",
        "delay",
        "buf",
        "blur",
        "amplify",
        "scale",
        "bpm",
        "sample",
        "spack",
        "env",
    )

    envelope_keywords = ("atk", "decay", "rel", "legato", "curve", "gain")
    base_attributes = ("sus", "fmod", "pan", "rate", "amp", "midinote", "channel")
    required_keys = ("amp", "sus")

    internal_keywords = tuple(value for value in keywords if value != "degree")

    # Number of beats of delay for update >> operation or setattr
    update_delay = 0

    # Aliases
    alias = {"pitch": "degree", "char": "degree"}

    fx_attributes = effect_manager.all_kwargs()
    fx_keys = effect_manager.kwargs()

    # Load default sample bank
    samples = buffer_manager

    # Set in __init__.py
    metro = None

    default_scale = Scale.default

    default_root = Root.default()  # TODO//remove callable

    after_update_methods = ["stutter"]

    # Tkinter Window
    widget = None

    def __init__(self, name=None):
        # Inherit from repeatable i.e. x.every
        Repeatable.__init__(self)

        self.method_synonyms["->"] = "rshift"
        self.method_synonyms["<-"] = "lshift"

        # General setup

        self.synthdef = None
        self.id = name

        self.always_on = False

        #self.current_event_size   = 0
        #self.current_event_length = 0
        #self.current_event_depth  = 0

        # Stopping flag
        self.stopping = False
        self.stop_point = 0

        # Reference to other objects in the clock played at the same time
        self.queue_block = None
        self.bus = None

        # The string representation of the degree of the player
        self.playstring = ""
        self.midi_map = None

        # Information used in generating OSC messages
        self.buf_delay = []
        self.timestamp = 0
        # self.condition = lambda: True
        # self.sent_messages = []

        # Visual feedback information
        self.envelope = None
        self.line_number = None
        self.whitespace = None
        self.do_bang = False
        self.bang_kwargs = {}

        # Keeps track of which note to play etc
        self.event_index = 0
        self.event_n = 0
        self.notes_played = 0
        self.event = {}
        self.accessed_keys = []

        # Used for checking clock updates
        self.current_dur = None
        self.old_pattern_dur = None
        self.old_dur = None

        self.isplaying = False
        self.isAlive = True

        # These dicts contain the attribute and modifier values that are sent to SuperCollider     

        self.attr = {}

        # # These dict contains extra attributes of a SynthDef
        # self.extra_attr = {}

        # self.default_args = ('sus',
        #                      'fmod',
        #                      'pan',
        #                      'rate',
        #                      'amp',
        #                      'midinote',
        #                      'channel',
        #                      'freq',
        #                      'vib',
        #                      'bus',
        #                      'blur',
        #                      'beat_dur',
        #                      'atk',
        #                      'decay',
        #                      'rel',
        #                      'peak',
        #                      'level')

        self.modifier = Pattern()
        self.mod_data = 0
        self.filename = None

        # Keyword arguments that are used internally
        self.scale = None
        self.offset = 0
        self.following = None

        # List the internal variables we don't want to send to SuperCollider
        self.__vars = list(self.__dict__.keys())
        self.__init = True

        self.reset()

    # Class methods

    @classmethod
    def help(cls):
        return print(cls.__doc__)

    @classmethod
    def get_attributes(cls):
        """Returns a list of possible keyword arguments for FoxDot players"""
        return cls.keywords + cls.base_attributes

    @classmethod
    def get_fxs(cls):
        """Returns a list of possible keyword arguments for FoxDot effects"""
        return cls.fx_attributes

    @classmethod
    def Attributes(cls):
        """To be replaced by `Player.get_attributes()`"""
        return cls.get_attributes()

    @classmethod
    def set_clock(cls, tempo_clock):
        cls.metro = tempo_clock

    # Should this also be instance method?
    @classmethod
    def set_sample_bank(cls, sample_bank):
        cls.samples = sample_bank

    def __hash__(self):
        return hash(self.id)  # could be problematic if there are id clashes?

    def __repr__(self):
        if self.id is not None:
            return "<{} - {}>".format(self.id, self.synthdef)
        else:
            return "a '{}' Player Object".format(self.synthdef)

    def info(self):
        s = "Player Instance using '%s' \n\n" % self.synthdef
        s += "ATTRIBUTES\n"
        s += "----------\n\n"
        for attr, val in self.attr.items():
            s += "\t{}\t:{}\n".format(attr, val)
        return s

    def __getattribute__(self, name):
        # This checks for aliases, not the actual keys
        name = Player.alias.get(name, name)
        item = object.__getattribute__(self, name)
        if isinstance(item, PlayerKey):
            if name not in self.accessed_keys:
                self.accessed_keys.append(name)
        return item

    def __getitem__(self, name, sdb):
        if self.__init:
            if name not in self.__vars:
                return self.attr[name]
            pass
        return self.__dict__[name]

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return not self is other

    def __int__(self):
        return int(self.now('degree'))

    def __float__(self):
        return float(self.now('degree'))

    def __add__(self, data):
        """ Change the degree modifier stream """
        self.mod_data = data
        if self.synthdef == SamplePlayer:
            # self.attr['sample'] = self.modifier + self.mod_data
            self.sample = self.modifier + self.mod_data
        else:
            #self.attr['degree'] = self.modifier + self.mod_data
            self.degree = self.modifier + self.mod_data
        return self

    def __lshift__(self, data):
        self.dur = Pattern.mimov(self.dur, data)
        return self

    def __sub__(self, data):
        """ Change the degree modifier stream """
        self.mod_data = 0 - data
        if self.synthdef == SamplePlayer:
            self.attr['sample'] = self.modifier + self.mod_data
        else:
            self.attr['degree'] = self.modifier + self.mod_data
        return self

    def __mul__(self, data):
        return self

    def __div__(self, data):
        return self

    def __iter__(self):
        for _, value in self.event.items():
            yield value

    def __getattr__(self, name):
        try:
            # Get the parameter value from reaper if it exists
            if "reatrack" in self.attr.keys():
                reatrack = self.attr["reatrack"][0]
                if isinstance(reatrack, ReaTrack):
                    device, _ = get_reaper_object_and_param_name(reatrack, name, quiet=True)
                    if device is not None:
                        return get_reaper_param(reatrack, name)

            # This checks for aliases, not the actual keys
            name = self.alias.get(name, name)
            if name in self.attr and name not in self.__dict__:
                # Return a Player key
                self._update_player_key(name, self.now(name), 0)
            item = self.__dict__[name]

            # If returning a player key, keep track of which are being accessed
            if isinstance(item, PlayerKey) and name not in self.accessed_keys:
                self.accessed_keys.append(name)
            return item

        except KeyError:
            err = "Player Object has no attribute '{}'".format(name)
            raise AttributeError(err)
    # Player Object Manipulation

    def __rshift__(self, other):
        """
        Handles the allocation of SynthDef objects using >> syntax, other must be
        an instance of `SynthDefProxy`, which is usually created when calling a
        `SynthDef`
        """
        if isinstance(other, SynthDefProxy):
            # Call the update method
            self.update(other.name, other.degree, **other.kwargs)

            # self.update_pattern_root('sample' if self.synthdef == SamplePlayer else 'degree')
            for method, arguments in other.methods:
                args, kwargs = arguments
                getattr(self, method).__call__(*args, **kwargs)
            # Add the modifier (check if not 0 to stop adding 0 to values)
            if (not isinstance(other.mod, (int, float))) or (other.mod != 0):
                self + other.mod
            return self
        raise TypeError(
            "{} is an innapropriate argument type for PlayerObject".format(other)
        )

    def test_for_circular_reference(
        self, value, attr, last_player=None, last_attr=None
    ):
        """Used to raise an exception if a player's attribute refers to itself e.g. `p1 >> pads(dur=p1.dur)`"""
        # We are setting self.attr to value, check if value depends on self.attr

        if isinstance(value, PGroup):
            for item in value:
                self.test_for_circular_reference(item, attr, last_player, last_attr)

        elif isinstance(value, PlayerKey):
            # If the Player key relies on this player.attr, raise error
            if value.cmp(self, attr):
                ident_self = value.name()
                if last_player is not None:
                    ident_other = "{}.{}".format(last_player.id, last_attr)
                else:
                    ident_other = ident_self
                err = "Circular reference found: {} to itself via {}".format(
                    ident_self, ident_other
                )

                raise ValueError(err)

            elif last_player == value.player and last_attr == value.attr:
                return
            else:
                # Go through the player key's
                for item in value.get_player_attribute():
                    self.test_for_circular_reference(
                        item, attr, value.player, value.attr
                    )
        return

    def __setattr__(self, name, value):
        # Possibly replace with slots?
        if self.__init:
            # Force the data into a Pattern if the attribute is used with SuperCollider
            if name not in self.__vars:
                # Apply the parameter in reaper if it exists
                if "reatrack" in self.attr.keys():
                    reatrack = self.attr["reatrack"][0]
                    if isinstance(reatrack, ReaTrack):
                        device, _ = get_reaper_object_and_param_name(reatrack, name, quiet=True)
                        if device is not None:
                            set_reaper_param(reatrack, name, value)
                            return
                # Get any alias
                name = self.alias.get(name, name)
                value = asStream(value)
                for item in value:
                    self.test_for_circular_reference(item, name)

                # Update the attribute dict if no error
                self.attr[name] = value

                # Remove from the stored pattern dict / call those
                self.update_pattern_root(name)

                # keep track of what values we change with +-
                if (
                    (self.synthdef == SamplePlayer and name == "sample")
                    or (self.synthdef == SamplePlayer and name == "spack")
                    or (self.synthdef != SamplePlayer and name == "degree")
                ):
                    self.modifier = value

                # Update any playerkey
                if name in self.__dict__:
                    if isinstance(self.__dict__[name], PlayerKey):
                        self.__dict__[name].update_pattern()
                # self.update_player_key(name, 0, 0)
                return

        self.__dict__[name] = value
        return

    def __getattr__(self, name):
        try:
            # This checks for aliases, not the actual keys
            name = self.alias.get(name, name)
            if name in self.attr and name not in self.__dict__:
                # Return a Player key
                self.update_player_key(name, self.now(name), 0)

            item = self.__dict__[name]
            # If returning a player key, keep track of which are being accessed
            if isinstance(item, PlayerKey) and name not in self.accessed_keys:
                self.accessed_keys.append(name)
            return item

        except KeyError:
            err = "Player Object has no attribute '{}'".format(name)
            raise AttributeError(err)
        return

    def __getattribute__(self, name):
        # This checks for aliases, not the actual keys
        name = Player.alias.get(name, name)
        item = object.__getattribute__(self, name)
        if isinstance(item, PlayerKey):
            if name not in self.accessed_keys:
                self.accessed_keys.append(name)
        return item

    def __getitem__(self, name):
        if self.__init:
            if name not in self.__vars:
                return self.attr[name]
            pass
        return self.__dict__[name]

    def __eq__(self, other):
        "equal operator"
        return self is other

    def __ne__(self, other):
        "not equal"
        return not self is other

    # --- Startup methods
    def reset(self):
        """Sets all Player attributes to 0 unless their default is specified by an effect. Also
        can be called by using a tilde before the player variable. E.g. ~p1"""

        # Add all keywords to the dict, then set non-zero defaults

        reset = []

        for key in Player.Attributes():
            if key not in (
                "scale",
                "dur",
                "sus",
                "blur",
                "amp",
                "amplify",
                "degree",
                "oct",
                "bpm",
                "vol",
            ):
                setattr(self, key, 0)
            reset.append(key)

        # Set any non zero defaults for effects, e.g. verb=0.25

        for key in Player.fx_attributes:
            value = effect_manager.defaults[key]

            if key not in ("vol"): # fix volume bug
                setattr(self, key, value)

            reset.append(key)

        # Set SynthDef defaults
        if self.synthdef in SynthDefs:
            synth = SynthDefs[self.synthdef]
            for key in ("atk", "decay", "rel"):
                setattr(self, key, synth.defaults[key])
                reset.append(key)

        # Any other attribute that might have been used - set to 0

        for key in self.attr:
            if key not in reset:
                setattr(self, key, 0)

        # Set any non-zero values for FoxDot

        # Sustain & Legato
        self.sus = 0.5 if self.synthdef == SamplePlayer else 1
        self.blur = 1
        # Amplitude
        self.amp = 1
        self.amplify = 1
        # Duration of notes
        self.dur = 0.5 if self.synthdef == SamplePlayer else 1
        # Degree of scale / Characters of samples
        self.degree = " " if self.synthdef is SamplePlayer else 0
        # Octave of the note
        self.oct = 5
        # Tempo
        self.bpm = None
         # Output (Elie's multiphonic setup WIP)
        self.output = 2
        # Stop calling any repeating methods
        self.stop_calling_all()
        return self

    def __invert__(self):
        """Using the ~ syntax resets the player"""
        return self.reset()

    # --- Update methods
    def __call__(self, **kwargs):
        """Sends the next osc message event to SuperCollider and schedules this
        Player in the clock based on the current clock time and this player's
        current duration value."""

        # If stopping, kill the event
        if self.stopping and self.metro.now() >= self.stop_point:
            self.kill()
            return

        # If the duration has changed, work out where the internal markers should be
        # -- This could be in its own private function
        force_count = kwargs.get("count", False)
        dur_updated = self.dur_updated()

        if dur_updated or force_count is True:
            try:
                self.event_n, self.event_index = self.count(
                    self.event_index if not force_count else None
                )
            except TypeError as e:
                print(e)
                print("TypeError: Innappropriate argument type for 'dur'")

        # Get the current state
        self._get_event()

        # Play the note
        if not isinstance(self.event["dur"], rest):
            try:
                self._send_osc_messages_to_server(
                    verbose=(self.metro.solo == self and kwargs.get('verbose', True))
                )
            except Exception as err:
                print("Error in Player {}: {}".format(self.id, err))

        # If using custom bpm
        dur = self.event["dur"]

        if self.event["bpm"] is not None:
            try:
                tempo_shift = float(self.metro.bpm) / float(self.event["bpm"])
            except (AttributeError, TypeError, ZeroDivisionError):
                tempo_shift = 1
            dur *= tempo_shift

        # Schedule the next event (could move before get_event and use the index for get_event)
        self.event_index = self.event_index + dur
        self.metro.schedule(self, self.event_index, kwargs={})

        # Change internal marker
        self.event_n += 1
        self.notes_played += 1
        return

    def count(self, time=None, event_after=False):
        """Counts the number of events that will have taken place between 0 and `time`. If
        `time` is not specified the function uses self.metro.now(). Setting `event_after`
        to `True` will find the next event *after* `time`"""
        n = 0
        acc = 0
        dur = 0
        now = time if time is not None else self.metro.now()

        if self.current_dur is None:
            self.current_dur = self.rhythm()
        durations = list(map(get_first_item, self.current_dur))  # careful here
        total_dur = float(sum(durations))
        if total_dur == 0:
            WarningMsg("Player object has a total duration of 0. Set to 1")
            durations = [1]
            total_dur = 1
            self.dur = 1
        acc = now - (now % total_dur)

        try:
            n = int(len(durations) * (acc / total_dur))
        except TypeError as e:
            WarningMsg(e)
            self.stop()
            return 0, 0

        if acc != now:
            while True:
                dur = float(modi(durations, n))
                if acc + dur == now:
                    acc += dur
                    n += 1
                    break

                elif acc + dur > now:
                    if event_after:
                        acc += dur
                        n += 1
                    break
                else:
                    acc += dur
                    n += 1

        # Returns value for self.event_n and self.event_index
        return n, acc

    def dur_updated(self):
        """Returns True if the players duration has changed since the last call"""
        self.current_dur = self.rhythm()
        if self.current_dur != self.old_dur:
            self.old_dur = self.current_dur
            return True
        return False

    def rhythm(self):
        """Returns the players array of durations at this point in time"""
        return list(
            map(
                lambda x: x if isinstance(x, (int, float)) else self.unpack(x),
                self.attr["dur"],
            )
        )

    #############################################
    #######   Player Object Manipulation   ######
    #############################################

    def __rshift__(self, other):
        """ Handles the allocation of SynthDef objects using >> syntax, other must be
            an instance of `SynthDefProxy`, which is usually created when calling a
            `SynthDef`
        """
        if isinstance(other, SynthDefProxy):
            # Call the update method
            self.update(other.name, other.degree, **other.kwargs)
            # self.update_pattern_root('sample' if self.synthdef == SamplePlayer else 'degree')
            for method, arguments in other.methods:
                args, kwargs = arguments
                getattr(self, method).__call__(*args, **kwargs)
            # Add the modifier (check if not 0 to stop adding 0 to values)
            if (not isinstance(other.mod, (int, float))) or (other.mod != 0):
                self + other.mod
            return self
        raise TypeError(f"{other} is an innapropriate argument type for PlayerObject")
        return self

    def update(self, synthdef, degree, **kwargs):
        """Updates the attributes of the player. Called using the >> syntax."""
        # SynthDef name
        self.synthdef = synthdef
        # Make sure all values are reset to start
        if "filename" in kwargs:
            self.filename = kwargs["filename"]
            del kwargs["filename"]

        if "midi_map" in kwargs:
            self.midi_map = kwargs["midi_map"]
            del kwargs["midi_map"]

        if self.isplaying is False:
            self.reset()

        # If there is a designated solo player when updating, add this at next bar
        if self.metro.solo.active() and self.metro.solo != self:
            self.metro.schedule(
                lambda *args, **kwargs: self.metro.solo.add(self), self.metro.next_bar()
            )

        # Update the attribute values
        special_cases = ["scale", "root", "dur"]

        # Set the degree
        if synthdef == SamplePlayer:
            if type(degree) == str:
                self.playstring = degree
            else:
                self.playstring = None
            if degree is not None:
                setattr(self, "degree", degree if degree != "" else " ")
        elif degree is not None:
            self.playstring = str(degree)  # this doesn't work for var!
            setattr(self, "degree", degree)
        else:
            setattr(self, "degree", 0)

        # Set special case attributes
        self.scale = kwargs.get("scale", self.__class__.default_scale)
        self.root = kwargs.get("root", self.__class__.default_root)

        # If only duration is specified, set sustain to that value also
        if "dur" in kwargs:
            # If we use tuples / PGroups in setting duration, use it to modify delay using the PDur algorithm
            setattr(self, "dur", kwargs["dur"])
            if "sus" not in kwargs:
                self.sus = self.attr["dur"]

        # Set any other attributes
        for name, value in kwargs.items():
            if name not in special_cases:
                setattr(self, name, value)

        # Calculate new position if not already playing
        if self.isplaying is False:
            # Add to clock
            self.isplaying = True
            self.stopping = False

            # If we want to update now, set the start point to now
            after = True
            if self.metro.now_flag:
                start_point = self.metro.now()
                after = False
            elif kwargs.get("quantise", True) == False:
                start_point = self.metro.now()
            else:
                start_point = self.metro.next_bar()

            self.event_n = 0
            self.event_n, self.event_index = self.count(start_point, event_after=after)
            self.metro.schedule(self, self.event_index)

        return self

    def get_timestamp(self, beat=None):
        if beat is not None:
            timestamp = self.metro.osc_message_time() - self.metro.beat_dur(
                self.metro.now() - beat
            )
        else:
            timestamp = self.metro.osc_message_time()
        return timestamp

    def lshift(self, n=1):
        """Plays the event behind"""
        self.event_n -= n + 1
        return self

    def rshift(self, n=1):
        """Plays the event in front"""
        self.event_n += n
        return self

    def _number_of_layers(self, **kwargs):
        """ Returns the deepest nested item in the event """
        num = 1
        for attr, value in self.event.items():
            value = kwargs.get(attr, value)
            if isinstance(value, PGroup):
                l = pattern_depth(value)
            else:
                l = 1
            if l > num:
                num = l
        return num

    def largest_attribute(self, **kwargs):
        """Returns the length of the largest nested tuple in the current event dict"""

        size = 1
        values = []

        for attr, value in self.event.items():
            value = kwargs.get(attr, value)
            l = get_expanded_len(value)
            if l > size:
                size = l
        return size

    def _get_event_length(self, event=None, **kwargs):
        """ Returns the largest length value in the event dictionary """
        if event is None:
            event = self.event

        if kwargs:
            event = event.copy()
            event.update(kwargs)

        max_val = 0

        for attr, value in event.items():
            if isinstance(value, PGroup):
                l = len(value)

            else:
                l = 1

            if l > max_val:
                max_val = l

        return max_val

    def _number_attr(self, attr):
        """ Returns true if the attribute should be a number """
        return not (self.synthdef == SamplePlayer and attr in ("degree", "freq"))

    def _update_player_key(self, key, value, time):
        """  Forces object's dict uses PlayerKey instances
        """
        if (key not in self.__dict__) or (not isinstance(self.__dict__[key], PlayerKey)):

            self.__dict__[key] = PlayerKey(value, player=self, attr=key) 

        else:
            # Force values if not playing

            if self.isplaying is False:
                self.__dict__[key].set(value, time)

            else:
                self.__dict__[key].update(value, time)

        return

    def _update_all_player_keys(self, ignore=[], event=None, **kwargs):
        """ Updates the internal values of player keys that have been accessed e.g. p1.pitch. If there is a delay,
            then schedule a function to update the values in the future. """

        # Don't bother if no keys are being accessed

        if len(self.accessed_keys) == 0:
            return

        if event is None:
            event = self.event

        delay = event.get("delay", 0)

        if isinstance(delay, PGroup):
            event_size = self.get_event_length(event, **kwargs)

            delays = itertools.cycle(delay)

            for i in range(event_size):
                delay = next(delays)

                # recursively unpack

                new_event = {}

                for new_key, new_value in event.items():
                    if new_key in self.accessed_keys:
                        new_value = kwargs.get(new_key, new_value)

                        if isinstance(new_value, PGroup):
                            new_event[new_key] = new_value[i]

                        else:
                            new_event[new_key] = new_value

                if isinstance(delay, PGroup):
                    # Recursively unpack and send messages
                    for i in range(self._get_event_length(new_event)):
                        self._update_all_player_keys(event=new_event, ignore=ignore, **kwargs)
                else:
                    self._update_player_key_from_event(
                        new_event, time=self.event_index, ignore=ignore, delay=delay, **kwargs
                    )

        else:
            self._update_player_key_from_event(event, time=self.event_index, ignore=ignore, delay=delay, **kwargs)
        return

    def _update_player_key_from_event(self, event, time=None, delay=0, ignore=[], **kwargs):
        timestamp = self.event_index if time is None else time

        if delay == 0:
            for key in (x for x in self.accessed_keys if x not in ignore):
                self._update_player_key(key, kwargs.get(key, event.get(key, 0)), timestamp)
        else:
            func_args = (event, timestamp + delay, 0, ignore)
            self.metro.schedule(self._update_player_key_from_event, timestamp + delay, args=func_args, kwargs=kwargs)
        return

    def _update_player_key_relation(self, item: NumberKey):
        """ Called during 'now' to update any Players that a player key is related to before using that value """
        if item.parent is self:  # If this *is* the parent, just get the current value
            self._update_player_key(item.attr, self.now(item.attr), 0)

        # If the parent is in the same queue block, make sure its values are up-to-date

        elif self.queue_block is not None:
            # Try and find the item in the queue block

            try:
                queue_item = self.queue_block[item.player]

            except KeyError:
                queue_item = None

            # Update the parent with an up-to-date value

            if queue_item is not None and queue_item.called is False:
                item.player._update_player_key(item.attr, item.player.now(item.attr), 0)
        return item.now()

    # --- Methods for preparing and sending OSC messages to SuperCollider

    def unpack(self, item):
        """Converts a pgroup to floating point values and updates and time var or playerkey relations"""

        if isinstance(item, GeneratorPattern):
            # "pop" value from the generator

            item = item.getitem()  # could be renamed to "next"

        if isinstance(item, TimeVar):
            # Get current value if TimeVar

            item = item.now()

        if isinstance(item, NumberKey):
            # Update any relationships to the number key if necessary
            item = self._update_player_key_relation(item)

        if isinstance(item, PGroup):
            # Make sure any values in the PGroup have their "now" methods called

            item = item.convert_data(self.unpack)

        return item

    def get_key(self, key, i, **kwargs):
        return group_modi(kwargs.get(key, self.event[key]), i)

    # Private method

    def now(self, attr="degree", x=0, **kwargs):
        """Calculates the values for each attr to send to the server at the current clock time"""

        index = self.event_n + x

        try:
            if len(self.attr[attr]) > 0:
                attr_value = kwargs.get(attr, self.attr[attr][index])

            else:
                attr_value = 0  # maybe have a dict of defaults?

        # Debugging

        except KeyError as e:
            print(attr, self.attr[attr], index)
            raise (e)

        except ZeroDivisionError as e:
            print(self, attr, self.attr[attr], index)
            raise (e)

        # Force and timevar etc into floats

        if attr_value is not None and (not isinstance(attr_value, (int, float))):
            attr_value = self.unpack(attr_value)

        return attr_value

    def get_prime_funcs(self, event):
        """Finds and PGroupPrimes in event and returns the modulated event dictionary"""

        prime_keys = ("degree", "sample")

        # Go through priority keys

        for key in prime_keys:
            self.apply_prime_funcs(event, key)

        # Then do the rest (skipping prime)

        for key in event:
            if key not in prime_keys:
                self.apply_prime_funcs(event, key)

        return event

    @staticmethod
    def apply_prime_funcs(event, key):
        value = event[key]
        if isinstance(value, PGroup) and value.has_behaviour():
            func = value.get_behaviour()
            event = func(event, key)
        return event

    def _unduplicate_durs(self, event):
        """ Converts values stored in event["dur"] in a tuple/PGroup into delays """

        # If there are more than one dur then add to the delay

        if "dur" in event:
            try:
                if len(event["dur"]) > 1:
                    init_dur = event["dur"][0]

                    offset = PGroup(0 | event["dur"][1:])

                    event["delay"] = event["delay"] + offset

                    event["dur"] = float(init_dur)

                elif len(event["dur"]) == 1:
                    event["dur"] = float(event["dur"][0])

            except TypeError:
                pass

        if "sus" in event:
            try:
                # Also update blur / sus

                if len(event["sus"]) > 1:
                    min_sus = min(event["sus"]) if min(event["sus"]) else 1

                    offset = PGroup([(sus / min_sus) for sus in event["sus"]])

                    event["blur"] = event["blur"] * offset

                    event["sus"] = float(min_sus)

                elif len(event["sus"]) == 1:
                    event["sus"] = float(event["sus"][0])

            except TypeError:
                pass

        return event

    def _get_event(self):
        """ Returns a dictionary of attr -> now values """

        self.event = dict(map(lambda attr: (attr, self.now(attr)), self.attr.keys()))
        self.event = self._unduplicate_durs(self.event)
        self.event = self.get_prime_funcs(self.event)

        # Update internal player keys / schedule future updates
        self._update_all_player_keys()
        return self

    def _send_osc_messages_to_server(self, timestamp=None, verbose=True, **kwargs):
        """ Goes through the current event and compiles osc messages and sends them to server via the tempo clock """
        timestamp = timestamp if timestamp is not None else self.queue_block.time

        # self.do_bang = False
        for i in range(self._get_event_length(**kwargs)):
            self._send_osc_message(self.event, i, timestamp=timestamp, verbose=verbose, **kwargs)
        # if self.do_bang:

        #     self.bang()

        return

    def _send_osc_message(self, event, index, timestamp=None, verbose=True, **kwargs):
        """ Compiles and sends an individual OSC message created by recursively unpacking nested PGroups """

        packet = {}

        event = event.copy()
        event.update(kwargs)

        for key, value in event.items():
            # If we can index a value, trigger a new OSC message to send OSC messages for each

            # value = kwargs.get(key, value)

            if isinstance(value, PGroup):
                new_event = {}

                for new_key, new_value in event.items():
                    # new_value = kwargs.get(new_key, new_value)

                    if isinstance(new_value, PGroup):
                        new_event[new_key] = new_value[index]

                    else:
                        new_event[new_key] = new_value

                # Recursively unpack and send messages
                for i in range(self._get_event_length(new_event)):
                    self._send_osc_message(new_event, i, timestamp, verbose)
                return

            else:
                # If it is a number, use the numbers (check for kwargs override)

                packet[key] = value

        # Special case modulations

        if ("amp" in packet) and ("amplify" in packet):
            packet["amp"] = packet["amp"] * packet["amplify"]

        # Send compiled messages
        self._push_osc_to_server(packet, timestamp, verbose, **kwargs)
        return

    def _push_osc_to_server(self, packet, timestamp, verbose=True, **kwargs):
        """ Adds message head, calculating frequency then sends to server if verbose is True and 
            amp/bufnum values meet criteria """

        # Do any calculations e.g. frequency
        message = self._new_message_header(packet, **kwargs)

        # Only send if amp > 0 etc
        if verbose and (message["amp"] > 0) and (
            (self.synthdef != SamplePlayer and message["freq"] != None) or
            (self.synthdef == SamplePlayer and message["buf"] > 0)
        ):
            # Need to send delay and synthdef separately

            delay = self.metro.beat_dur(message.get("delay", 0))
            synthdef = self._get_synth_name(message.get("buf", 0))  # to send to play1 or play2
            compiled_msg = self.metro.server.get_bundle(synthdef, message, timestamp=timestamp + delay)

            # We can set a condition to only send messages

            self.queue_block.append_osc_message(compiled_msg)

            # self.do_bang = True

        return

    def _new_message_header(self, event, **kwargs):
        """ Returns the header of an osc message to be added to by osc_message() """

        # Let SC know the duration of 1 beat so effects can use it and adjust sustain too

        beat_dur = self.metro.beat_dur()

        message = {
            "beat_dur": beat_dur,
            "sus": kwargs.get("sus", event["sus"]) * beat_dur,
        }

        if self.synthdef == SamplePlayer:
            degree = kwargs.get("degree", event["degree"])
            sample = kwargs.get("sample", event["sample"])
            spack = kwargs.get("spack", event["spack"])
            rate = kwargs.get("rate", event["rate"])

            if rate < 0:
                sus = kwargs.get("sus", event["sus"])

                pos = self.metro.beat_dur(sus)

            else:
                pos = 0

            buf = self.samples.get_buffer_from_symbol(str(degree), spack, sample).bufnum

            message.update({"buf": buf, "pos": pos})

            # Update player key

            if "buf" in self.accessed_keys:
                self.buf = buf

        elif self.synthdef == LoopPlayer:
            pos = kwargs.get("degree", event["degree"])
            buf = kwargs.get("buf", event["buf"])

            # Get a user-specified tempo

            given_tempo = kwargs.get("tempo", self.event.get("tempo", self.metro.bpm))

            if given_tempo in (None, 0):
                tempo = 1

            else:
                tempo = self.metro.bpm / given_tempo

            # Set the position in "beats"

            pos = pos * tempo * self.metro.beat_dur(1)

            # If there is a negative rate, move the pos forward

            rate = kwargs.get("rate", event["rate"])

            if rate == 0:
                rate = 1

            # Adjust the rate to a given tempo

            rate = float(tempo * rate)

            if rate < 0:
                sus = kwargs.get("sus", event["sus"])

                pos += self.metro.beat_dur(sus)

            message.update({"pos": pos, "buf": buf, "rate": rate})

        else:
            degree = kwargs.get("degree", event["degree"])
            octave = kwargs.get("oct", event["oct"])
            root = kwargs.get("root", event["root"])
            spack = kwargs.get("spack", event["spack"])
            scale = kwargs.get("scale", self.scale)

            if degree == None:
                freq, midinote = None, None

            else:
                freq, midinote = get_freq_and_midi(degree, octave, root, scale, midi_map=self.midi_map)
            message.update({'freq': freq, 'midinote': midinote})
            # Updater player key

            if "freq" in self.accessed_keys:
                self.freq = freq

            if "midinote" in self.accessed_keys:
                self.midinote = midinote

        # Update the dict with other values from the event

        event.update(message)

        # Remove keys we dont need

        del event["bpm"]

        return event

    def set_queue_block(self, queue_block):
        """Gives this player object a reference to the other items that are
        scheduled at the same time"""
        self.queue_block = queue_block
        return

    def _get_synth_name(self, buf=0):
        """ Returns the real SynthDef name of the player. Useful only for "play" 
            as there is a play1 and play2 SynthDef for playing audio files with
            one or two channels respectively. """
        if self.synthdef == SamplePlayer:
            numChannels = self.samples.get_buffer(buf).channels
            if numChannels == 1:
                synthdef = "play1"
            else:
                synthdef = "play2"
        else:
            synthdef = str(self.synthdef)
        return synthdef

    def addfx(self, **kwargs):
        """Not implemented - add an effect to the SynthDef bus on SuperCollider
        after it has been triggered."""
        return self

    #: Methods for stop/starting players

    def kill(self):
        """Removes this object from the Clock and resets itself"""

        self.isplaying = False
        self.stopping = True

        self.reset()

        if self in self.metro.playing:
            self.metro.playing.remove(self)

        return

    def stop(self, N=0):
        """Removes the player from the Tempo clock and changes its internal
        playing state to False in N bars time
        - When N is 0 it stops immediately"""

        self.stopping = True
        self.stop_point = self.metro.now()

        if N > 0:
            self.stop_point = self.metro.next_bar() + (
                (N - 1) * self.metro.bar_length()
            )

        else:
            self.kill()

        return self

    def pause(self):
        self.isplaying = False

        return self

    def play(self):
        self.isplaying = True
        self.stopping = False
        self.isAlive = True

        self.__call__()
        return self

    #####################
    #####   Utils   #####
    #####################

    def num_key_references(self):
        """Returns the number of 'references' for the
        attr which references the most other players"""
        num = 0
        for attr in self.attr.values():
            if isinstance(attr, PlayerKey):
                if attr.num_ref > num:
                    num = attr.num_ref
        return num

    def _replace_degree(self, new_degree):
        # Update the GUI if possible
        # if self.widget:
        #    if self.synthdef == SamplePlayer:
        #        if self.playstring is not None:
        #            # Replace old_string with new string (only works with plain string patterns)
        #            new_string = new_degree.string()
        #            self.widget.addTask(target=self.widget.replace, args=(self.line_number, self.playstring, new_string))
        #            self.playstring = new_string
        #    else:
        #        # Replaces the degree pattern in the widget (experimental)
        #        # self.widget.addTask(target=self.widget.replace_re, args=(self.line_number,), kwargs={'new':str(new_degree)})
        #        self.playstring = str(new_degree)
        setattr(self, "degree", new_degree)
        return

    def multiply(self, n=2):
        self.attr["degree"] = self.attr["degree"] * n
        return self

    def degrade(self, amount=0.5):
        """Sets the amp modifier to a random array of 0s and 1s
        amount=0.5 weights the array to equal numbers"""
        if float(amount) <= 0:
            self.amplify = 1
        else:
            self.amplify = PwRand(
                [0, self.attr["amplify"]], [int(amount * 10), max(10 - int(amount), 0)]
            )
        return self

    def changeSynth(self, list_of_synthdefs):
        new_synth = choice(list_of_synthdefs)
        if isinstance(new_synth, DefaultPygenSynthDef):
            new_synth = str(new_synth.name)
        self.synthdef = new_synth
        return self

    """

        Modifier Methods
        ----------------

        Other modifiers for affecting the playback of Players

    """

    def offbeat(self, dur=1):
        """Off sets the next event occurence"""

        self.dur = abs(dur)
        self.delay = abs(dur) / 2

        return self

    def strum(self, dur=0.025):
        """Adds a delay to a Synth Envelope"""
        x = self.largest_attribute()
        if x > 1:
            self.delay = asStream([tuple(a * dur for a in range(x))])
        else:
            self.delay = asStream(dur)
        return self

    def __repr__(self):
        if self.id is not None:
            return "<{} - {}>".format(self.id, self.synthdef)
        else:
            return "a '{}' Player Object".format(self.synthdef)

    # def get_extra_attributes(self):
    #    """ Returns a dict of specific keyword arguments for a particular FoxDot player """
    #    filename = SYNTHDEF_DIR + f"/{self.id}.scd"
    #    file = open(filename, "r")
    #    contents = file.read()
    #    file.close()
    #    if "arg" in contents:
    #        arg_start = "arg"
    #        arg_end = "var"
    #    else:
    #        arg_start = "|"
    #        arg_end = "var"
    #    idx1 = contents.index(arg_start)
    #    idx2 = contents.index(arg_end)
    #    args = ""
    #    # getting elements in between
    #    for idx in range(idx1 + len(arg_start), idx2-3):
    #        args = args + contents[idx]
    #    args = "".join(args.split())
    #    xtra_args = args.split(",")
    #    temp_args = {}
    #    for arg in xtra_args:
    #        if "=" in arg:
    #            a, b = arg.split("=")
    #            temp_args[a] = b
    #            self.extra_attr[a] = b
    #    for k in self.default_args:
    #        if k in temp_args.keys():
    #            del self.extra_attr[k]
    #    return self.extra_attr

    # def info(self):
    #    s = "Player Instance using '%s' \n\n" % self.synthdef
    #    s += "ATTRIBUTES\n"
    #    s += "----------\n\n"
    #    for attr, val in self.attr.items():
    #        s += "\t{}\t:{}\n".format(attr, val)
    #    self.get_extra_attributes()
    #    for attr, val in self.extra_attr.items():
    #        s += "\t{}\t:{}\n".format(attr, val)
    #    return s

    def bang(self, **kwargs):
        """
        Triggered when sendNote is called. Responsible for any
        action to be triggered by a note being played. Default action
        is underline the player
        """
        if kwargs:
            self.bang_kwargs = kwargs

        elif self.bang_kwargs:
            bang = Bang(self, self.bang_kwargs)
        return self

