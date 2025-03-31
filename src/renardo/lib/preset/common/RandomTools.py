# Pattern function
from renardo.lib.runtime import player_method, PWhite

# Param shortcut functions to use with dict unpack : **lpf(linvar([0,.3],8))
@player_method
def humz(self, velocity=20, humanize=5, swing=0):
    """ Humanize the velocity, delay and add swing in % (less to more)"""
    humanize += 0.1
    if velocity!=0:
        self.delay=[0,PWhite((-1*humanize/100)*self.dur, (humanize/100)*self.dur) + (self.dur*swing/100)]
        self.amplify=[1,PWhite((100-velocity)/100,1)]
    else:
        self.delay=0
        self.amplify=1
    return self

def rnd(pattern, random_amount=0.05, compensation=True):
    tweak_serie = PWhite(-random_amount, random_amount)[: len(pattern)]
    result = [pattern[i] + tweak_serie[i] for i in range(len(pattern))]
    if compensation:
        result += [pattern[i] - tweak_serie[i] for i in range(len(pattern))]
    print(result)
    return result

def rnd1(pattern):
    average_value = sum(pattern) / len(pattern)
    return rnd(pattern, random_amount=0.1 * average_value)

def rnd2(pattern):
    average_value = sum(pattern) / len(pattern)
    return rnd(pattern, random_amount=0.2 * average_value)

def rnd5(pattern):
    average_value = sum(pattern) / len(pattern)
    return rnd(pattern, random_amount=0.05 * average_value)