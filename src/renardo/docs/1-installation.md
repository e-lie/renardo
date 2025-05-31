
# Renardo 1.0 installation

# What's New in 1.0

- New embedded livecoding editor with integrated tutorial, doc and examples : to replace FoxDot (tk based) editor as default editor. But you can which you can still access and use classic editor (see other editor section)
- Web UI for preferences and customizable look and feel.
- New dynamic scheduling concepts (undefined PointInTime classes) to prepare
- Simple macro to make scheduling painless
- Support for several audio backends : SuperCollider (classic FoxDot) + Reaper (dynamic plugin provisioning and every parameters control)
- Musical assets management : picking sample packs, sclang code for instruments and effects, reaper instruments chains, all from a community server : milestone on the road to free reproducible music. 

## Install overview

 > Renardo is a modular software with multiple possible use cases and way of generating music with code. Here we will follow theses standard steps:

- Install renardo as a python library or a binary (embeddeding it own python)
- Launch renardo
- Install and launch SuperCollider Audio Backend
- Initialize and test by executing some code
- Install and launch Reaper Audio Backend (facultative)
- Test by executing some more tutorial examples

> Lets start with the simple installation.

# Install Renardo

 ## Use Renardo binary (easier if you don't use Python already)

 Download from here (depending on your System) https://collections.renardo.org/binaries/
 
 ...and execute the binary program  : `./renardo` or double click `renardo.exe`

 On MacOs and Linux you have to give execution right to the binary before executing it: `chmod u+x renardo`

 On MacOs and maybe Windows you will need to go to security preferences to allow program manually for execution.
 
## Install Renardo as Python Package (to integrate it with a python environment)

- Install `renardo==1.0.0a4` package from PyPI using pip or your prefered python package manager.
- Execute `python3 -m renardo`, `py -m renardo` or similar depending on your python setup.

## Install Development version (to contribute or hack it)

 - Install `uv` : https://docs.astral.sh/uv/
 - Clone the following repository : `git clone https://github.com/e-lie/renardo.git -b v1.0dev`
 - install / build the web ui / editor : `cd webclient && npm install && npm run build`
 - run `uv run renardo` which will install python dependencies and start renardo with web ui (default) 

# Launch renardo

Launching renardo will open automatically a local http endpoint : `https://127.0.0.1:12345`

We will initialize the install but first we need to install SuperCollider

# Install SuperCollider (Default Audio Backend)

- Windows : Install SuperCollider with the official installer (https://supercollider.github.io/downloads) 
- MacOS : Install SuperCollider with the official installer (https://supercollider.github.io/downloads) 
- Linux : Install SuperCollider with your prefered package manager (`sudo apt install supercollider`, `sudo pacman -S supercollider`, etc...)

### Launch SuperCollider and make it work !

- _Facultative Linux step_ : you need JACK server started (https://archive.flossmanuals.net/ardour/ch015_starting-jack-on-ubuntu.html) or `pipewire` with the `pipewire-jack` module installed.
- Open SuperCollider IDE (`scide` on linux).
- Type code `s.boot` or `Server.default.boot` and hit Ctrl+Return. Look for errors in the post window
- Type code `{ SinOsc.ar() }.play;` and execute like before. You should ear a simple sound hurra !

If it works you can quit SuperCollider for now.

If it didn't you may need to select the proper sound device by following this doc: https://doc.sccode.org/Reference/AudioDeviceSelection.html

On recent M1/M2 Mac computers you may need to manually switch sound device to use headphones (because Apple engineers like to break things/standards)

# Initialize Renardo and test

Launch renardo and go to initialize page to follow init instructions: you will download minimal samples, sclang instruments and effect, reaper instruments, for the features to work.

Go to Audio Backend page to launch SuperCollider backend.

Go to the Code Editor and test typing for example : `b1 >> blip()` then CTRL+Enter to test the sound.

# Install Reaper Backend

- Download and install reaper (`https://reaper.fm`)
- Launch renardo, go to Audio Backends > REAPER. Click "Initialize REAPER integration":

- First it will open reaper. Ensure you validate everything (choosing an output device, click activate reaper or using the demo, etc). Then click continue.
- Second it configures reaper connection (reapy) and ask you to close : close THEN click continue.
- Third it will conclude the init process. Keep reaper open.

# Test REAPER backend

Close and relaunch renardo while keeping REAPER open. Go to tutorial tab, (right pane) section 16 (reaper integration).

Follow the instruction there.