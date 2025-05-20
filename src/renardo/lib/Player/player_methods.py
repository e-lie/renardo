from __future__ import division, absolute_import, print_function

from copy import copy
from random import choice

from .player import Player
from renardo.lib.Patterns import PwRand, PRand, PGroup, PGroupPrime, as_pattern
from renardo.lib.TimeVar import mapvar, var, linvar, inf
from renardo.sc_backend import LoopPlayer
from renardo.lib.Bang import Bang


def player_method(f):
    """ Decorator for assigning functions as Player methods.
    >>> @player_method
    ... def test(self):
    ...    print(self.degree)

    >>> p1.test()
    """
    setattr(Player, f.__name__, f)
    return getattr(Player, f.__name__)


PlayerMethod = player_method # Temporary alias

@player_method
def pause(self: Player):
    self.isplaying = False

    return self

@player_method
def play(self: Player):
    self.isplaying = True
    self.stopping = False
    #self.isAlive = True

    self.__call__()

    return self

@player_method
def stop(self: Player, N=0):
    """Removes the player from the Tempo clock and changes its internal
    playing state to False in N bars time
    - When N is 0 it stops immediately"""
    self.stopping = True
    self.stop_point = self.main_event_clock.now()
    if N > 0:
        self.stop_point = self.main_event_clock.next_bar() + (
            (N - 1) * self.main_event_clock.bar_length()
        )
    else:
        self.kill()
    return self

@player_method
def kill(self: Player):
    """Removes this object from the Clock and resets itself"""
    self.isplaying = False
    self.stopping = True
    self.reset()
    if self in self.main_event_clock.playing:
        self.main_event_clock.playing.remove(self)
    return

@player_method
def reload(self: Player):
    """ If this is a 'play' or 'loop' SynthDef, reload the filename used"""
    if self.instrument_name == LoopPlayer:
        self.buffer_manager.load_buffer(self.filename, force=True)
    return self

@player_method
def only(self: Player):
    """ Stops all players except this one """
    for player in list(self.main_event_clock.playing):
        if player is not self:
            player.stop()
    return self

@player_method
def solo(self: Player, action=1):
    """ Silences all players except this player. Undo the solo
        by using `Player.solo(0)` """
    action = int(action)
    if action == 0:
        self.main_event_clock.solo.reset()
    elif action == 1:
        self.main_event_clock.solo.set(self)
    elif action == 2:
        pass
    return self


###########################

@player_method
def often(self: Player, *args, **kwargs):
    """Calls a method every 1/2 to 4 beats using `every`"""
    return self.every(PRand(1, 8) / 2, *args, **kwargs)

@player_method
def sometimes(self: Player, *args, **kwargs):
    """Calls a method every 4 to 16 beats using `every`"""
    return self.every(PRand(8, 32) / 2, *args, **kwargs)

@player_method
def rarely(self: Player, *args, **kwargs):
    """Calls a method every 16 to 32 beats using `every`"""
    return self.every(PRand(32, 64) / 2, *args, **kwargs)


###########################

@player_method
def stutter(self: Player, amount=None, _beat_=None, **kwargs):
    """Plays the current note n-1 times. You can specify keywords."""

    timestamp = self.get_timestamp(_beat_)

    # Get the current values (this might be called between events)

    n = int(kwargs.get("n", amount if amount is not None else 2))
    ahead = int(kwargs.get("ahead", 0))

    for key in ("ahead", "n"):
        if key in kwargs:
            del kwargs[key]

    # Only send if n > 1 and the player is playing

    if self.main_event_clock.solo == self and n > 1:
        new_event = {}
        attributes = self.attr.copy()
        attr_keys = set(list(self.attr.keys()) + list(kwargs.keys()))
        for key in attr_keys:
            if key in kwargs:
                item = kwargs[key]
                if isinstance(item, PGroupPrime):
                    new_event[key] = self.unpack(item)
                elif isinstance(item, PGroup):
                    new_event[key] = self.unpack(PGroup([item]))
                else:
                    new_event[key] = self.unpack(PGroup(item))
            elif len(attributes[key]) > 0:
                new_event[key] = self.attr_current_value(key, ahead)
        new_event = self.unduplicate_durs(new_event)
        dur = float(kwargs.get("dur", new_event["dur"])) / n
        new_event["dur"] = dur
        # Get PGroup delays
        new_event["delay"] = PGroup(
            [dur * (i + 1) for i in range(max(n, self.get_event_length(new_event)))]
        )
        new_event = self.get_prime_funcs(new_event)
        self.send(timestamp=timestamp, **new_event)

    return self

@player_method
def jump(self: Player, ahead=1, _beat_=None, **kwargs):
    """ Plays an event ahead of time. """
    timestamp = self.get_timestamp(_beat_)
    if self.main_event_clock.solo == self:
        new_event = {}
        attributes = copy(self.attr)
        for key in attributes:
            if key in kwargs:
                new_event[key] = self.unpack(PGroup(kwargs[key]))
            elif len(attributes[key]) > 0:
                new_event[key] = self.attr_current_value(key, ahead)
        new_event = self.unduplicate_durs(new_event)
        new_event = self.get_prime_funcs(new_event)
        self.send(timestamp=timestamp, **new_event)
    return self

@player_method
def degrade(self: Player, amount=0.5):
    """ Sets the amp modifier to a random array of 0s and 1s
        amount=0.5 weights the array to equal numbers """
    if float(amount) <= 0:
        self.amplify = 1
    else:
        self.amplify = PwRand([0, self.attr["amplify"]], [int(amount * 10), max(10 - int(amount), 0)])
    return self

@player_method
def lshift(self: Player, n=1):
    """Plays the event behind"""
    self.event_n -= n + 1
    return self

@player_method
def rshift(self: Player, n=1):
    """Plays the event in front"""
    self.event_n += n
    return self


@player_method
def spread(self: Player, on=0.125):
    """ Sets pan to (-1, 1) and pshift to (0, 0.125)"""
    if on != 0:
        self.pan = (-1, 1)
        self.pshift = (0, on)
    else:
        self.pan = 0
        self.pshift = 0
    return self

@player_method
def unison(self: Player, unison=2, detune=0.125):
    """ Like spread(), but can specify number of voices(unison)
    Sets pan to (-1,-0.5,..,0.5,1) and pshift to (-0.125,-0.0625,...,0.0625,0.125)
    If unison is odd, an unchanged voice is added in the center
    Eg : p1.unison(4, 0.5) => pshift=(-0.5,-0.25,0.25,0.5), pan=(-1.0,-0.5,0.5,1.0)
         p1.unison(5, 0.8) => pshift=(-0.8,-0.4,0,0.4,0.8), pan=(-1.0,-0.5,0,0.5,1.0)
    """
    if unison != 0:
        pan = []
        pshift = []
        uni = int(unison if unison % 2 == 0 else unison - 1)
        for i in range(1, int(uni / 2) + 1):
            pan.append(2 * i / uni)
            pan.insert(0, -2 * i / uni)
        for i in range(1, int(uni / 2) + 1):
            pshift.append(detune * (i / (uni / 2)))
            pshift.insert(0, detune * -(i / (uni / 2)))
        if unison % 2 != 0 and unison > 1:
            pan.insert(int(len(pan) / 2), 0)
            pshift.insert(int(len(pan) / 2), 0)
        self.pan = tuple(pan)
        self.pshift = tuple(pshift)
    else:
        self.pan = 0
        self.pshift = 0
    return self

@player_method
def seconds(self: Player):
    """ Sets the player bpm to 60 so duration will be measured in seconds """
    self.bpm = 60
    return self

@player_method
def slider(self: Player, start=0, on=1):
    """ Creates a glissando effect between notes """
    if on:
        if start:
            self.slide = [1, 0]
            self.slidefrom = [0, 1]
        else:
            self.slide = [0, 1]
            self.slidefrom = [1, 0]
        self.slidedelay = 0.75
    else:
        self.slide = 0
        self.slidefrom = 0
        self.slidedelay = 0
    return self

@player_method
def penta(self: Player, switch=1):
    """ Shorthand for setting the scale to the pentatonic mode of the default scale """
    if switch:
        self.scale = self.__class__.default_scale.pentatonic
    else:
        self.scale = self.__class__.default_scale
    return self

@player_method
def alt_dur(self: Player, dur):
    """ Used to set a duration that changes linearly over time. You should use a `linvar` but
        any value can be used. This sets the `dur` to 1 and uses the `bpm` attribute to
        seemingly alter the durations """

    self.dur = 1
    self.bpm = self.main_event_clock.bpm * (1 / (dur))
    return self

@player_method
def reverse(self: Player):
    """ Reverses every attribute stream """
    for attr in self.attr:
        try:
            self.attr[attr] = self.attr[attr].pivot(self.event_n)
        except AttributeError:
            pass
    return self

@player_method
def shuffle(self: Player):
    """ Shuffles the degree of a player. """
    # If using a play string for the degree
    #if self.synthdef == SamplePlayer and self.playstring is not None:
    #    # Shuffle the contents of playgroups among the whole string
    #    new_play_string = PlayString(self.playstring).shuffle()
    #    new_degree = Pattern(new_play_string).shuffle()
    #else:
    #new_degree = self.attr['degree'].shuffle()
    new_degree = self.previous_patterns["degree"].root.shuffle()
    self._replace_degree(new_degree)
    return self

@player_method
def rotate(self: Player, n=1):
    """ Rotates the values in the degree by 'n' """
    #self._replace_degree(self.attr['degree'].rotate(n))
    new_degree = self.previous_patterns["degree"].root.rotate(n)
    self._replace_degree(new_degree)
    return self

@player_method
def attrmap(self: Player, key1, key2, mapping):
    """ Sets the attribute for self.key2 to self.key1
        altered with a mapping dictionary.
    """
    self.attr[key2] = self.attr[key1].map(mapping)
    return self

@player_method
def smap(self: Player, kwargs):
    """ Like map but maps the degree to the sample attribute
    """
    self.attrmap("degree", "sample", kwargs)
    return self

@player_method
def map(self: Player, other, mapping, otherattr="degree"):
    """ p1 >> pads().map(b1, {0: {oct=[4,5], dur=PDur(3,8), 2: oct})     """
    # Convert dict to {"oct": {4}}
    # key is the value of player key, attr is
    for key, minimap in mapping.items():
        for attr, value in minimap.items():
            setattr(self, attr, mapvar(getattr(other, attr), value))
    return self


@player_method
def offbeat(self: Player, dur=1):
    """ Off sets the next event occurence """
    self.dur = abs(dur)
    self.delay = abs(dur) / 2

    return self

@player_method
def strum(self: Player, dur=0.025):
    """ Adds a delay to a Synth Envelope """
    x = self.largest_attribute()
    if x > 1:
        self.delay = as_pattern([tuple(a * dur for a in range(x))])
    else:
        self.delay = as_pattern(dur)
    return self

@player_method
def multiply(self: Player, n=2):
    self.attr['degree'] = self.attr['degree'] * n
    return self

@player_method
def changeSynth(self: Player, list_of_synthdefs):
    new_synth = choice(list_of_synthdefs)
    # TODO write a better check for the synthdef type/name
    # if isinstance(new_synth, SynthDef):
    #    new_synth = str(new_synth.name)
    self.instrument_name = new_synth
    return self

#####################################################
#####   Methods for collaborative performance   #####
#####################################################

@player_method
def accompany(self: Player, other, values=[0, 2, 4], debug=False):
    """ Similar to "follow" but when the value has changed """
    if isinstance(other, self.__class__):
        self.degree = other.degree.accompany()
    return self

@player_method
def follow(self: Player, other=False):
    """ Takes a Player object and then follows the notes """
    if isinstance(other, self.__class__):
        self.degree = other.degree
    return self

@player_method
def versus(self: Player, other_key, rule=lambda x, y: x > y, attr=None):
    """ Sets the 'amplify' key for both players to be dependent on the comparison of keys """
    # Get reference to the second player object
    other = other_key.player
    # Get the attribute from the key to versus
    this_key = getattr(self, other_key.attr if attr is None else attr)
    # Set amplifications based on the rule
    self.amplify = this_key.transform(lambda value: rule(value, other_key.now()))
    other.amplify = this_key.transform(lambda value: not rule(value, other_key.now()))
    return self


@player_method
def versus_old(self: Player, other: Player, key=lambda x: x.freq, f=max):
    """Takes another Player object and a function that takes
    two player arguments and returns one, default is the higher
    pitched
    """
    if other is not None:
        # make sure it's using another player
        assert other.__class__ == self.__class__

        def func(x, y):
            return f(x, y, key=key)

        self.condition = lambda: func(self, other) == self
        other.condition = lambda: func(self, other) == other
        self._versus = other
    else:
        self.condition = lambda: True
        self._versus.condition = lambda: True
        self._versus = None
    return self

# def versus(self, other, func = lambda a, b: a > b):

#     self.amp  = self.pitch > other.pitch
#     other.amp = other.pitch > self.pitch

#     return self





@player_method
def bang(self: Player, **kwargs):
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




@player_method
def fade(self: Player, dur=8, fvol=1, ivol=None, autostop=True):
    if ivol is None:
        ivol = float(self.amplify)
    self.amplify = linvar([ivol, fvol], [dur, inf], start=self.main_event_clock.mod(4))
    def static_final_value():
        if fvol == 0 and autostop:
            self.stop()
        else:
            self.amplify = fvol
    self.main_event_clock.schedule(static_final_value, self.main_event_clock.next_bar() + dur + 1)
    return self

@player_method
def fadein(self: Player, dur=8, fvol=1, ivol=0, autostop=True):
    self.fade(dur=dur, fvol=fvol, ivol=ivol, autostop=autostop)
    return self

@player_method
def fadeout(self: Player, dur=4, fvol=0, ivol=1, autostop=True):
    self.fade(dur=dur, fvol=fvol, ivol=ivol, autostop=autostop)
    return self

@player_method
def solofade(self: Player, dur=16, fvol=0, ivol=None, autostop=False):
    for player in list(self.main_event_clock.playing):
        if player is not self: # and not player.always_on:
            player.fade(dur, ivol, fvol, autostop)
    return self

@player_method
def solofadeout(self: Player, dur=16, fvol=0, ivol=None, autostop=False):
    self.solofade(dur, ivol, fvol, autostop=autostop)
    return self

@player_method
def solofadein(self: Player, dur=16, fvol=1, ivol=None, autostop=False):
    self.solofade(dur, ivol, fvol, autostop=autostop)
    return self

@player_method
def eclipse(self: Player, dur=4, total=16, leftshift=0, smooth=0):
    """periodic pause of the player: pause 4 beats every 16"""
    if smooth == 0:
        self.amplify = var([1, 0, 1], [leftshift, dur, total - leftshift - dur])
    else:
        self.amplify = linvar([1, 0, 0, 0, 1, 1],
                                [leftshift, smooth * dur, dur - smooth * dur, smooth * dur,
                                total - leftshift - dur - smooth * dur])
    return self


# @player_method
# def addfx(self: Player, **kwargs):
#     """Not implemented - add an effect to the SynthDef bus on SuperCollider
#     after it has been triggered."""
#     return self


# Bulk modification of player params with dict
@player_method
def setp(self, param_dict):
    for key, value in param_dict.items():
        setattr(self, key, value)

@player_method
def getp(self, filter = None):
    result = None
    if "reatrack" in self.attr.keys():
        reatrack = self.attr["reatrack"][0]
        if isinstance(reatrack, ReaTrack):
            #result = reatrack.config
            if filter is not None:
                result = {key: value for key, value in reatrack.get_all_params().items() if filter in key}
            else:
                result = reatrack.get_all_params()
    return result

@player_method
def showp(self, filter = None):
    pprint(self.getp(filter))