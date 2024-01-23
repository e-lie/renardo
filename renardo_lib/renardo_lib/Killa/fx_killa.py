from ..Effects import *

### Based on TIDAL & SonicPi FX ####

fx = FxList.new("krush", "dirt_krush", {"krush":0, "kutoff":15000}, order=2)
fx.add_var("signal")
fx.add_var("freq")
fx.add("freq = Select.kr(kutoff > 0, [DC.kr(4000), kutoff])")
fx.add("signal = (osc.squared + (krush * osc)) / (osc.squared + (osc.abs * (krush-1.0)) + 1.0)")
fx.add("signal = RLPF.ar(signal, clip(freq, 20, 10000), 1)")
fx.add("osc = SelectX.ar(krush * 2.0, [osc, signal])")
fx.save()

fx = FxList.new("squiz", "squiz", {"squiz":0}, order=2)
fx.add("osc = Squiz.ar(osc, squiz)")
fx.save()

fx = FxList.new("triode", "triode", {"triode":0}, order=2)
fx.add_var("sc")
fx.add("sc = triode * 10 + 1e-3")
fx.add("osc = (osc * (osc > 0)) + (tanh(osc * sc) / sc * (osc < 0))")
fx.add("osc = LeakDC.ar(osc)*1.2")
fx.save()

fx = FxList.new("octer", "octer", {"octer":0, "octersub": 0, "octersubsub": 0}, order=1)
fx.add_var("oct1")
fx.add_var("oct2")
fx.add_var("oct3")
fx.add_var("sub")
fx.add("oct1 = 2.0 * LeakDC.ar(abs(osc))")
fx.add("sub = LPF.ar(osc, 440)")
fx.add("oct2 = ToggleFF.ar(sub)")
fx.add("oct3 = ToggleFF.ar(oct2)")
fx.add("osc = SelectX.ar(octer, [osc, octer*oct1, DC.ar(0)])")
fx.add("osc = osc + (octersub * oct2 * sub) + (octersubsub * oct3 * sub)")
fx.save()

fx = FxList.new("sample_atk", "sample_atk", {"sample_atk":0, "sample_sus":1}, order=2)
fx.add_var("env")
fx.add("env = EnvGen.ar(Env.new(levels: [0,1,0], times:[sample_atk, sample_sus], curve: 'lin'))")
fx.add("osc = osc*env")
fx.save()

fx = FxList.new("position", "trimPos", {"position": 0, "sus": 1}, order=2)
fx.add("osc = osc * EnvGen.ar(Env(levels: [0,0,1], curve: 'step', times: [sus * position, 0]))")
fx.save()

fx = FxList.new("comp", "comp", {"comp": 0, "comp_above": 1, "comp_below": 0.8}, order=2)
fx.add("osc = Compander.ar(osc, osc, thresh: comp, slopeAbove: comp_above, slopeBelow: comp_below, clampTime: 0.01, relaxTime: 0.01, mul: 1)")
fx.save()

Effect.server.setFx(FxList)