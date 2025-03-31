# Pattern function

from renardo.lib.runtime import (
    Player, Group, player_method,
    linvar,
    var,
)

def create_group(group_name, *args):
    """
    create_group("keys", "key1", "key2", "key3")
    create_group("pads") # -> create pad1 to pad5
    """
    if not args and group_name[-1] == 's':
        args = [group_name[:-1]+str(i) for i in range(1,6)]
    for player_name in args:
        globals()[player_name] = Player()
    globals()[group_name] = Group(*[globals()[player_name] for player_name in args])

@player_method
def pause(self, longueur=4, total=8, decalage=0, smooth=0):
    if smooth == 0:
        self.amplify = var([1,0,1], [decalage, longueur, total-decalage-longueur])
    else:
        self.amplify = linvar([1,0,0,0,1,1], [decalage, smooth*longueur, longueur-smooth*longueur, smooth*longueur, total-decalage-longueur-smooth*longueur])
    return self


# def rnd(pattern, random_amount=0.05, compensation=True):
#     tweak_serie = PWhite(-random_amount, random_amount)[: len(pattern)]
#     result = [pattern[i] + tweak_serie[i] for i in range(len(pattern))]
#     if compensation:
#         result += [pattern[i] - tweak_serie[i] for i in range(len(pattern))]
#     print(result)
#     return result


# def rnd1(pattern):
#     average_value = sum(pattern) / len(pattern)
#     return rnd(pattern, random_amount=0.1 * average_value)


# def rnd2(pattern):
#     average_value = sum(pattern) / len(pattern)
#     return rnd(pattern, random_amount=0.2 * average_value)


# def rnd5(pattern):
#     average_value = sum(pattern) / len(pattern)
#     return rnd(pattern, random_amount=0.05 * average_value)


# def microshift(pattern, shifts):
#     for key, value in shifts.items():
#         if key in range(len(pattern) - 1):
#             pattern[key] += value
#             pattern[key + 1] -= value
#     print(pattern)
#     return pattern


# def zipat(*args):
#     notes = [item for i, item in enumerate(args) if i % 2 == 0]
#     dur = [item for i, item in enumerate(args) if i % 2 == 1]
#     return {"degree": notes, "dur": dur}


# ZP = zipat


def run_now(f):
    f()
    return f

# This is not really a decorator, more a currying mechanism using the decorator syntax
# Cf: https://www.geeksforgeeks.org/currying-function-in-python/ and https://www.saltycrane.com/blog/2010/03/simple-python-decorator-examples/


def later_clockless(clock):
    def later_clocked(future_dur):
        def later_decorator(f):
            clock.future(future_dur, f)
            return f
        return later_decorator
    return later_clocked
