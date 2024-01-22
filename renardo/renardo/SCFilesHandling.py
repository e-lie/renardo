import os

from pathlib import Path
from sys import platform

SC_USER_CONFIG_DIR = None

# default config path
# on windows AppData/Roaming/renardo
# on Linux ~/.config/renardo
# on MacOS /Users/<username>/Library/Application Support/renardo
if platform == "linux" or platform == "linux2" :
    home_path = Path.home()
    SC_USER_CONFIG_DIR = home_path / '.local' / 'share' / 'SuperCollider'
elif platform == "darwin":
    home_path = Path.home()
    SC_USER_CONFIG_DIR = home_path / 'Library' / 'Application Support' / 'SuperCollider'
elif platform == "win32":
    appdata_local_path = Path(os.getenv('LOCALAPPDATA'))
    SC_USER_CONFIG_DIR = appdata_local_path / 'SuperCollider'

SC_USER_EXTENSIONS_DIR = SC_USER_CONFIG_DIR / 'Extensions'

SCLANG_PROCESS = None

def is_renardo_scfiles_installed():
    return (
        (SC_USER_EXTENSIONS_DIR / 'Renardo.sc').exists()
        and (SC_USER_EXTENSIONS_DIR / 'StageLimiter.sc').exists()
        and (SC_USER_CONFIG_DIR / 'start_renardo.scd').exists()
    )

def write_sc_renardo_files_in_user_config():
    renardo_sc_class = '''
        Renardo
        {
            classvar server;
            classvar midiout;

            *start
            { | remote = false |

                server = Server.default;
                server.options.memSize = 8192 * 16; // increase this if you get "alloc failed" messages
                server.options.maxNodes = 1024 * 32; // increase this if you are getting drop outs and the message "too many nodes"
                server.options.numOutputBusChannels = 2; // set this to your hardware output channel size, if necessary
                server.options.numInputBusChannels = 2; // set this to your hardware output channel size, if necessary

                if (remote, {
                    server.options.bindAddress = "0.0.0.0"; // allow connections from any address
                });

                server.boot();

                OSCFunc(
                    {
                        arg msg, time, addr, port;
                        var fn;
                        // Get local filename
                        fn = msg[1].asString;
                        // Print a message to the user
                        ("Loading SynthDef from" + fn).postln;
                        // Add SynthDef to file
                        fn = File(fn, "r");
                        fn.readAllString.interpret;
                        fn.close;
                    },
                    'foxdot'
                );

                StageLimiterBis.activate(2);
                "Listening for messages from Renardo".postln;
            }

            *startRemote
            {
                this.start(true);
            }

            *midi
            {
                arg port=0;
                MIDIClient.init;
                midiout = MIDIOut(port);
                OSCFunc(
                    {
                        arg msg, time, addr, port;
                        var note, vel, sus, channel, nudge;
                        // listen for specific MIDI trigger messages from FoxDot
                        note    = msg[2];
                        vel     = msg[3];
                        sus     = msg[4];
                        channel = msg[5];
                        nudge   = msg[6];
                        SystemClock.schedAbs(time + nudge, {midiout.noteOn(channel, note, vel)});
                        SystemClock.schedAbs(time + nudge + sus, {midiout.noteOff(channel, note, vel)});
                    },
                    'foxdot_midi'
                );
                ("Sending Renardo MIDI messages to" + MIDIClient.destinations[port].name).postln;
            }
        }
   '''

    stagelimiter_sc_class = '''
        // Batuhan Bozkurt 2009
        StageLimiterBis
        {
            classvar lmSynth, lmFunc, activeSynth;
            
            *activate
            { |numChannels = 2|
                fork
                {
                    lmFunc = 
                    { 
                        { 
                            activeSynth = 
                                Synth(\\stageLimiter,
                                    target: RootNode(Server.default), 
                                    addAction: \\addToTail
                                );
                        }.defer(0.01) 
                    };
                    lmSynth = SynthDef(\\stageLimiter, 
                    {
                        var input = In.ar(0, numChannels);
                        input = Select.ar(CheckBadValues.ar(input, 0, 0), [input, DC.ar(0), DC.ar(0), input]);
                        ReplaceOut.ar(0, Limiter.ar(input)) ;
                    }).add;
                    Server.default.sync;
                    lmFunc.value;
                    CmdPeriod.add(lmFunc);
                    "StageLimiter active".postln;
                }
            }
            
            *deactivate
            {
                activeSynth.free;
                CmdPeriod.remove(lmFunc);
                "StageLimiter inactive...".postln;
            }
        }
    '''

    renardo_start_code = '''
        Renardo.start;
        Renardo.midi;
    '''

    with open(SC_USER_EXTENSIONS_DIR / 'StageLimiter.sc', mode="w") as file:
        file.write(stagelimiter_sc_class)

    with open(SC_USER_EXTENSIONS_DIR / 'Renardo.sc', mode="w") as file:
        file.write(renardo_sc_class)

    with open(SC_USER_CONFIG_DIR / 'start_renardo.scd', mode="w") as file:
        file.write(renardo_start_code)


