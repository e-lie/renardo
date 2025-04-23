import inspect
import sys

from types import FunctionType, MethodType

from renardo.lib.Player import MethodCall, Player

from renardo.lib.Patterns import as_pattern
from renardo.lib.Utils import modulo_index
from renardo.lib import Code


class SchedulingQueue(object):
    """Queue to store the event blocks to send to SuperCollider"""
    def __init__(self, clock):
        self.data = []
        self.clock = clock

    def __repr__(self):
        return "\n".join([str(item) for item in self.data]
                        ) if len(self.data) > 0 else "[]"

    def __iter__(self):
        for x in self.data:
            yield x

    def __len__(self):
        return len(self.data)

    def add(self, item, beat, args=(), kwargs={}, is_priority=False):
        """ Adds a callable object to the queue at a specified beat, args and kwargs for the
            callable object must be in a list and dict.
        """
        # item must be callable to be schedule, so check args and kwargs are appropriate for it
        try:
            function = inspect.getfullargspec(item)
        except TypeError:
            function = inspect.getfullargspec(item.__call__)
        # If the item can't take arbitrary keywords, check any kwargs are valid
        if function.varkw is None:
            for key in list(kwargs.keys()):
                if key not in function.args:
                    del kwargs[key]
        # If the new event is before the next scheduled event,
        # move it to the 'front' of the queue
        if self.before_next_event(beat):
            self.data.append(
                QueueBlock(self, item, beat, args, kwargs, is_priority)
            )
            block = self.data[-1]
        else:
            # If the event is after the next scheduled event, work
            # out its position in the queue
            # need to be careful in case self.data changes size
            for block in self.data:
                # If another event is happening at the same time, schedule together
                if beat == block.beat:
                    block.add(item, args, kwargs, is_priority)
                    break
                # If the event is later than the next event, schedule it here
                if beat > block.beat:
                    try:
                        i = self.data.index(block)
                    except ValueError:
                        i = 0
                    self.data.insert(
                        i,
                        QueueBlock(self, item, beat, args, kwargs, is_priority)
                    )
                    block = self.data[i]
                    break
        # Tell any players about what queue item they are in
        if isinstance(item, Player):
            item.set_queue_block(block)
        return

    def clear(self):
        while len(self.data):
            del self.data[-1]
        return

    def pop(self):
        return self.data.pop() if len(self.data) > 0 else list()

    def next(self):
        if len(self.data) > 0:
            try:
                return self.data[-1].beat
            except IndexError:
                pass
        return sys.maxsize

    def before_next_event(self, beat):
        try:
            return beat < self.data[-1].beat
        except IndexError:
            return True

    def after_next_event(self, beat):
        try:
            return beat >= self.data[-1].beat
        except IndexError:
            return False

    def get_server(self):
        """ Returns the `ServerManager` instanced used by this block's parent clock """
        return self.clock.server

    def get_clock(self):
        return self.clock



class QueueBlock(object):
    """Event block to send to SuperColiider -> stored in the Queue"""
    priority_levels = [
        lambda x: type(x) in
        (FunctionType, MethodType),  # Any functions are called first
        lambda x: isinstance(x, MethodCall),  # Then scheduled player methods
        lambda x: isinstance(x, Player),  # Then players themselves
        lambda x: True  # And anything else
    ]

    def __init__(
        self,
        clock,
        obj,
        t,
        args=(),
        kwargs={},
        is_priority=False
    ):  # Why am I forcing an obj?
        self.events = [[] for lvl in self.priority_levels]
        self.called_events = []
        self.called_objects = []
        self.items = {}
        self.osc_messages = []
        self.clock = clock
        self.server = self.clock.get_server()
        self.metro = self.clock.get_clock()
        self.beat = t
        self.time = 0
        self.add(obj, args, kwargs, is_priority)

    @classmethod
    def set_server(cls, server):
        cls.server = server  # osc server

    def start_server(self, serv):
        self.tempo_server = serv(self)
        return

    def __repr__(self):
        return "{}: {}".format(self.beat, self.players())

    def add(self, obj, args=(), kwargs={}, is_priority=False):
        """ Adds a callable object to the QueueBlock """
        q_obj = QueueObj(obj, args, kwargs)
        for i, in_level in enumerate(self.priority_levels):
            if in_level(obj):
                # Put at the front if labelled as priority
                if is_priority:
                    self.events[i].insert(0, q_obj)
                else:
                    self.events[i].append(q_obj)
                self.items[q_obj.obj
                          ] = q_obj  # store the wrapped object as an identifer
                break
        return

    def __call__(self):
        """ Calls self.osc_messages() """
        self.send_osc_messages()

    def append_osc_message(self, message):
        """ Adds an OSC bundle if the timetag is not in the past """
        if message.timetag > self.metro.get_time():
            self.osc_messages.append(message)
        return

    def send_osc_messages(self):
        """ Sends all compiled osc messages to the SuperCollider server """
        return list(map(self.server.sendOSC, self.osc_messages))

    def players(self):
        return [item for level in self.events[1:3] for item in level]

    def all_items(self):
        return [item for level in self.events for item in level]

    def __getitem__(self, key):  # could this use hashing with Player objects?
        return self.items[key]

    def __iter__(self):
        return (item for level in self.events for item in level)

    def __len__(self):
        return sum([len(level) for level in self.events])

    def __contains__(self, other):
        return other in self.items

    def objects(self):
        return [item.obj for level in self.events for item in level]



class QueueObj(object):
    """ Class representing each item in a `QueueBlock` instance """
    def __init__(self, obj, args=(), kwargs={}):
        self.obj = obj
        self.args = args
        self.kwargs = kwargs
        self.called = False  # flag to True when called by the block

    def __eq__(self, other):
        return other == self.obj

    def __ne__(self, other):
        return other != self.obj

    def __repr__(self):
        return repr(self.obj)

    def __call__(self):
        value = self.obj.__call__(*self.args, **self.kwargs)
        self.called = True
        return value



class History(object):
    """
    Stores osc messages send from the TempoClock so that if the
    Clock is reversed we can just send the osc messages already sent
    """
    def __init__(self):
        self.data = []
    def add(self, beat, osc_messages):
        self.data.append(osc_messages)



class Wrapper(Code.LiveObject):
    def __init__(self, metro, obj, dur, args=()):
        self.args = as_pattern(args)
        self.obj = obj
        self.step = dur
        self.metro = metro
        self.n = 0
        self.s = self.obj.__class__.__name__

    def __str__(self):
        return "<Scheduled Call '%s'>" % self.s

    def __repr__(self):
        return str(self)

    def __call__(self):
        """ Call the wrapped object and re-schedule """
        args = modulo_index(self.args, self.n)
        try:
            self.obj.__call__(*args)
        except:
            self.obj.__call__(args)
        Code.LiveObject.__call__(self)


class SoloPlayer:
    """ SoloPlayer objects """
    def __init__(self):
        self.data = []

    def __repr__(self):
        if len(self.data) == 0:
            return "None"
        if len(self.data) == 1:
            return repr(self.data[0])
        else:
            return repr(self.data)

    def add(self, player):
        if player not in self.data:
            self.data.append(player)

    def set(self, player):
        self.data = [player]

    def reset(self):
        self.data = []

    def active(self):
        """ Returns true if self.data is not empty """
        return len(self.data) > 0

    def __eq__(self, other):
        """ Returns true if other is in self.data or if self.data is empty """
        return (other in self.data) if self.data else True

    def __ne__(self, other):
        return (other not in self.data) if self.data else True


class ScheduleError(Exception):
    def __init__(self, item):
        self.type = str(type(item))[1:-1]

    def __str__(self):
        return "Could not schedule object of {}".format(self.type)