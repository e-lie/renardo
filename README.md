# Renardo

> Music livecoding environment

![Renardo screenshot](https://renardo.org/images/screenshot1.png)

- Livecoding with Python, SuperCollider, Reaper
- FoxDot fork with a lot of new features

[Installation](https://renardo.org/#/installation)

## Renardo is a new maintained version (a fork) of FoxDot.

FoxDot is a classic/amazing software used in the algorave community, created by Ryan Kirkbride nearly 10 years ago !

...but it has not been maintained for the last 3 years.

The community is still very alive ! (check especially FoxDot channel on Telegram)

There has been multiple very cool community forks but hard to find, install and understand without looking in the code.

Even before, FoxDot was already hard to install for non developers due the multiple moving parts it is composed of.

So the intent of the project is:

- Renardo as a fork of FoxDot will support all/most vanilla FoxDot features.
- The new name "Renardo" comes to make the new fork identifiable and thus findable online especially to serve as support for workshops and musical teaching.
- Renardo should be easier to install (and will continue to get easier).
- There is a lot of potential for FoxDot/Renardo and we would like to make it even more amazing.

This software would not exist without a lot of hard and smart work from Ryan Kirbride and all the community contributors. They should be thanked a lot for that piece !!

## Presentation of new features and architecture

### New documentation and tutorials (Work in progress)

### Cleaning and refactoring

- Progressive and deep code refactoring in progress seeking Python new features and good practices.
- Renardo is FoxDot made modular, splitting the codebase into several pieces / PyPI packages : `renardo-lib`, `renardo` (launcher + configuration TUI), `renardo-gatherer` (install/share sample packs and Synthdefs) |`FoxDotEditor` (Tkinter Editor from FoxDot), `renardo-reaper`

### New utility functions to compose musical pieces

- Fade (...to, ...in or ...out) functions
- Smart periodic pause functions (`eclipse`)
- New rythm generators
- New methods of Pattern interpolation
- New utility decorators to write down/produce pieces/tracks with code (as opposed to livecoding)

### Features to come...

#### Easy install

- Renardo bundle, using Pyinstaller will make the environment easily installable by simply downloading an archive including Python and Renardo.

#### External TUI to see FoxDot state while playing

- Independant of the editor in use (FoxDot editor, Pulsar, VIM, VSCod(ium) etc)
- Interactive displaying of currently active players and their parameters
- Clock display with multiple configurable modulo based progressbars
- Error/debug display

#### REAPER DAW / Vital(ium) Synth integration

- Reaper projects templates for use with Renardo
- Instantiation of classic (VST,AU,LV2) plugins via code
- Automatic mapping of all plugin's parameters for native control from renardo.

#### Ableton Link clock synchronisation...

- ...As de facto standard for music software synchronisation and synchronisation with other livecoding environments.