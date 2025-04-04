from .player import Player, TimeVar
from renardo.sc_backend import WarningMsg


class Group:
    metro = None

    def __init__(self, *args):
        self.players = list(args)

    def add(self, other):
        self.players.append(other)

    def __len__(self):
        return len(self.players)

    def __str__(self):
        return str(self.players)

    def solo(self, arg=True):
        if self.metro is None:
            self.__class__.metro = Player.main_event_clock

        if arg:
            self.metro.solo.set(self.players[0])

            for player in self.players[1:]:
                self.metro.solo.add(player)

        else:
            self.metro.solo.reset()

        return self

    def only(self):
        if self.metro is None:
            self.__class__.metro = Player.main_event_clock

        for player in list(self.metro.playing):
            if player not in self.players:
                player.stop()

        return self

    def iterate(self, dur=4):
        if dur == 0 or dur is None:
            self.amplify = 1
        else:
            delay, on = 0, float(dur) / len(self.players)
            for player in self.players:
                player.amplify = TimeVar([0, 1, 0], [delay, on, dur - delay])
                delay += on
        return

    def __setattr__(self, name, value):
        try:
            for p in self.players:
                try:
                    setattr(p, name, value)
                except:
                    WarningMsg("'%s' object has no attribute '%s'" % (str(p), name))
        except KeyError:
            self.__dict__[name] = value
        return self

    def __getattr__(self, name):
        """Returns a Pattern object containing the desired attribute for each player in the group"""
        if name == "players":
            return self.__dict__["players"]
        attributes = GroupAttr()
        for player in self.players:
            if hasattr(player, name):
                attributes.append(getattr(player, name))
        return attributes


class GroupAttr(list):
    def __call__(self, *args, **kwargs):
        for p in self:
            if callable(p):
                p.__call__(*args, **kwargs)


