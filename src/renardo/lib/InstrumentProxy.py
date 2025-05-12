class InstrumentProxy:
    def __init__(self, name, degree, kwargs):
        self.name = name
        self.degree = degree
        self.mod = 0
        self.kwargs = kwargs

        # the list of transform methods applied
        # eg blip([0,2]).often("reverse")
        self.methods = []
        self.vars = vars(self)

    def __str__(self):
        return "<SynthDef Proxy '{}'>".format(self.name)

    def __add__(self, other):
        self.mod = other
        return self

    def __coerce__(self, other):
        return None

    def __getattr__(self, name):
        if name not in self.vars:
            def func(*args, **kwargs):
                self.methods.append((name, (args, kwargs)))
                return self
            return func
        else:
            return getattr(self, name)