from renardo.lib.runtime import Pvar

import enum
from fastnumbers import isfloat, isint

class OctChange(enum.Enum):
    up = 0
    down = -1
    oct1 = 1
    oct2 = 2
    oct3 = 3
    oct4 = 4
    oct5 = 5
    oct6 = 6
    oct7 = 7
    oct8 = 8
    oct9 = 9
    def __repr__(self):
        if self.value == 0:
            return f"octup"
        elif self.value == 0:
            return f"octdown"
        else:
            return f"oct{self.value}"

down = OctChange.down
up = OctChange.up
oct1 = OctChange.oct1
oct2 = OctChange.oct2
oct3 = OctChange.oct3
oct4 = OctChange.oct4
oct5 = OctChange.oct5
oct6 = OctChange.oct6
oct7 = OctChange.oct7
oct8 = OctChange.oct8
oct9 = OctChange.oct9

def from_ziffer(ziffer):
    ziffer = ziffer.replace('T','10').replace('E','11')
    ziffer = ziffer.replace('\n', ' ').replace('  ', ' ').replace('  ',' ')
    ziffer = ziffer.replace('_','_ ').replace('^','^ ')
    bars = ziffer.split('|')
    res = []
    for bar in bars:
        elements = bar.split(' ')
        base_oct = 5
        current_oct = 5
        current_dur = .25
        new_bar = []
        for e in elements:
            if e == '_' and current_oct > 1:
                current_oct -= 1
            elif e == '^' and current_oct < 9:
                current_oct += 1
            elif isint(e):
                if current_oct != base_oct:
                    new_bar.append(OctChange(current_oct))
                    base_oct = current_oct
                new_bar.append(int(e))
            elif isfloat(e):
                if current_oct != base_oct:
                    new_bar.append(OctChange(current_oct))
                    base_oct = current_oct
                new_bar.append(float(e)*4)
        res += new_bar
    print(res)
    return res

class ZPattern():
    def __init__(self, *args):
        self.current_oct = 5
        self.current_dur = 1
        self.degree = []
        self.dur = []
        self.oct = []
        for arg in args:
            if isinstance(arg, float):
                self.current_dur = arg
            elif isinstance(arg, OctChange):
                if arg.value == -1:
                    self.current_oct -= 1
                elif arg.value == 0:
                    self.current_oct += 1
                else:
                    self.current_oct = arg.value
            elif isinstance(arg, int):
                self.degree.append(arg)
                self.dur.append(self.current_dur)
                self.oct.append(self.current_oct)
    def res(self):
        return {"degree": self.degree, "dur": self.dur, "oct": self.oct}


def ZP(*args):
    if len(args) == 1 and isinstance(args[0], str):
        args = from_ziffer(args[0])
    return ZPattern(*args).res()

############### Legacy 

def Pvar_unzip_degree_dur(duration_pattern_list):
    """
    Function to transform a list alternating degree and dur value into
    """
    if len(duration_pattern_list) == 1:
        return duration_pattern_list[0][0]
    patterns = [item[0] for item in duration_pattern_list]
    durations = [item[1] for item in duration_pattern_list]
    return Pvar(patterns, durations)

Pvz = Pvar_unzip_degree_dur

def Pvar_zip_degree_dur_root(root_pattern_list):
    if len(root_pattern_list) == 1:
        return {
            "degree": root_pattern_list[0][0],
            "root": root_pattern_list[0][1]
        }
    patterns = [item[0] for item in root_pattern_list]
    roots = [item[1] for item in root_pattern_list]
    durations = [item[2] for item in root_pattern_list]
    return {"degree": Pvar(patterns, durations), "root": Pvar(roots, durations)}

Pvzr = Pvar_zip_degree_dur_root

def zipat(*args):
    notes = [item for i, item in enumerate(args) if i % 2 == 0]
    dur = [item for i, item in enumerate(args) if i % 2 == 1]
    return {"degree": notes, "dur": dur}

ZP = zipat