SynthDef.new(\tb303, {
	|bus=0, freq=440, atk=0.1,fmod=0, pan=0, sus=1, dec=1.0, gate=0, amp=1, wave=0, ctf=100, res=0.2, top=1000|
	var  filEnv, volEnv, waves, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	volEnv =  EnvGen .ar( Env .new([10e-10, 1, 1, 10e-10], [0.01, sus, dec],  'exp' ));
	filEnv =  EnvGen .ar( Env .new([10e-10, 1, 10e-10], [0.01, dec],  'exp' ));

	waves = [ Saw .ar(freq, volEnv),  Pulse .ar(freq, 0.5, volEnv)];
	osc = RLPF .ar(  Select .ar(wave, waves), ctf + (filEnv * top), res).dup * amp;

	osc = Mix(osc) * 0.5;
	osc = HPF.ar(osc, 20);
	osc = LPF.ar(osc, 14000);
	osc = Splay.ar(osc * amp, pan);
	osc = Mix(osc);
	osc = osc * amp * 0.12;
	osc = Splay.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
