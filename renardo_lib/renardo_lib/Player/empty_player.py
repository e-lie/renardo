from .player import Player


class EmptyPlayer(object):
    """
    Placeholder for Player objects created at run-time to reduce load time.
    """

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<{} - Unassigned>".format(self.name)

    def __rshift__(self, *args, **kwargs):
        """Converts an EmptyPlayer to a Player."""
        self.__class__ = Player
        self.__init__(self.name)
        self.__rshift__(*args, **kwargs)
        return self

    def __invert__(self):
        """Using the ~ syntax resets the player"""
        return self.reset()

    def __getattribute__(self, name):
        """Tries to return the correct attr; if not init the Player and try again"""
        try:
            # Try to return the attribute
            return object.__getattribute__(self, name)
        except AttributeError:
            # If the attribute doesn't exist, initialize the Player and try again
            self.__class__ = Player
            self.__init__(self.name)
            try:
                # Try to return the attribute again
                return self.__getattribute__(name)
            except AttributeError:
                # If the attribute still doesn't exist, use getattr to make sure we return player key
                return self.__getattr__(name)