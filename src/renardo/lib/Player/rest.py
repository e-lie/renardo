
class rest(object):
    """Represents a rest when used with a Player's `dur` keyword"""

    def __init__(self, dur=1):
        self.dur = dur if not isinstance(dur, self.__class__) else dur.dur

    def __repr__(self):
        return "<rest: {}>".format(self.dur)

    def __add__(self, other):
        return rest(self.dur + other)

    def __radd__(self, other):
        return rest(other + self.dur)

    def __sub__(self, other):
        return rest(self.dur - other)

    def __rsub__(self, other):
        return rest(other - self.dur)

    def __mul__(self, other):
        return rest(self.dur * other)

    def __rmul__(self, other):
        return rest(other * self.dur)

    def __div__(self, other):
        return rest(self.dur / other)

    def __rdiv__(self, other):
        return rest(other / self.dur)

    def __truediv__(self, other):
        return rest(float(self.dur) / other)

    def __rtruediv__(self, other):
        return rest(other / float(self.dur))

    def __mod__(self, other):
        return rest(self.dur % other)

    def __rmod__(self, other):
        return rest(other % self.dur)

    def __eq__(self, other):
        return self.dur == other

    def __ne__(self, other):
        return self.dur != other

    def __lt__(self, other):
        return self.dur < other

    def __le__(self, other):
        return self.dur <= other

    def __gt__(self, other):
        return self.dur > other

    def __ge__(self, other):
        return self.dur >= other

    def __int__(self):
        return int(self.dur)

    def __float__(self):
        return float(self.dur)