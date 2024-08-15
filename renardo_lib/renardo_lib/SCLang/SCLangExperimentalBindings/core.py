def format_args(args=[], kwargs={}, delim=': '):
    return ", ".join([str(a) for a in args] + ["%s%s%s" % (key, delim, value) for key, value in kwargs.items()])


class cls:
    def __init__(self, name, **kwargs):
        self.name = name
        self.ref = kwargs.get("ref", "")

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self.name)

    def __call__(self, *args, **kwargs):
        return instance("{}({}{})".format(self.name, self.ref, format_args(args, kwargs)))

    def ar(self, *args, **kwargs):
        return instance("{}.ar({}{})".format(self.name, self.ref, format_args(args, kwargs)))

    def kr(self, *args, **kwargs):
        return instance("{}.kr({}{})".format(self.name, self.ref, format_args(args, kwargs)))

    def ir(self, *args, **kwargs):
        return instance("{}.ir({}{})".format(self.name, self.ref, format_args(args, kwargs)))


class instance:
    defaults = {}
    shortarg = {}

    def __init__(self, string):
        self.value = str(string)

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)

    def __add__(self, other):
        return instance("(%s)" % (str(self) + " + " + str(other)))

    def __sub__(self, other):
        return instance("(%s)" % (str(self) + " - " + str(other)))

    def __mul__(self, other):
        return instance("(%s)" % (str(self) + " * " + str(other)))

    def __div__(self, other):
        return instance("(%s)" % (str(self) + " / " + str(other)))

    def __pow__(self, other):
        return instance("(%s)" % (str(self) + " ** " + str(other)))

    def __xor__(self, other):
        return instance("(%s)" % (str(self) + " ** " + str(other)))

    def __truediv__(self, other):
        return self.__div__(other)

    def __getitem__(self, other):
        return instance("(%s)" % (str(self) + "[" + str(other) + "]"))

    def __radd__(self, other):
        return instance("(%s)" % (str(other) + " + " + str(self)))

    def __rsub__(self, other):
        return instance("(%s)" % (str(other) + " - " + str(self)))

    def __rmul__(self, other):
        return instance("(%s)" % (str(other) + " * " + str(self)))

    def __rdiv__(self, other):
        return instance("(%s)" % (str(other) + " / " + str(self)))

    def __rpow__(self, other):
        return instance("(%s)" % (str(other) + " ** " + str(self)))

    def __rxor__(self, other):
        return instance("(%s)" % (str(other) + " ** " + str(self)))

    def __rtruediv__(self, other):
        return self.__rdiv__(other)

    def __mod__(self, other):
        return instance(str(self.value) % str(other)) if "%" in self.value else self

    def __coerce__(self, other):
        try:
            self = instance(str(self))
            other = instance(str(other))
            return (self, other)
        except:
            return

    def __getattr__(self, name, *args, **kwargs):
        return self.custom('.' + name, *args, **kwargs)

    def string(self):
        return str(self.value) + "{}"

    def custom(self, name):
        return self.__class__(self.string().format(name))

    def __call__(self, *args, **kwargs):
        for arg in set(list(self.defaults.keys()) + list(self.shortarg.keys())):
            if arg in self.shortarg:
                if self.shortarg[arg] in kwargs:
                    kwargs[arg] = kwargs.get(
                        self.shortarg[arg], self.default[arg])
                    del kwargs[self.shortarg[arg]]
                    continue

            if arg in self.defaults:
                kwargs[arg] = kwargs.get(arg, self.defaults[arg])

        value = self.string().format("({})".format(format_args(args, kwargs)))

        return self.__class__(value)
