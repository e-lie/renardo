FoxDot - Editor
=====================================

Original FoxDot editor extract from original project for use with separated FoxDot library or renardo fork.

#### Startup

1. Open SuperCollider and type in `FoxDot.start` and evaluate this line. SuperCollider is now listening for messages from renardo_lib. 
2. Start FoxDot by entering `FoxDot` at the command line. If that doesn't work, try `python -m FoxDot`.
3. If you have installed the SC3 Plugins, use the "Code" drop-down menu to select "Use SC3 Plugins". Restart FoxDot and you'll have access to classes found in the SC3 Plugins.
4. Keep up to date with the latest verion of FoxDot by running `pip install FoxDot --upgrade` every few weeks.
5. Check out the [YouTube tutorials](https://www.youtube.com/channel/UCRyrNX07lFcfRSymZEWwl6w) for some in-depth tutorial videos on getting to grips with FoxDot

#### Installing with SuperCollider 3.7 or earlier

If you are having trouble installing the FoxDot Quark in SuperCollider, it is usually because the version of SuperCollider you are installing doesn’t have the functionality for installing Quarks or it doesn’t work properly. If this is the case, you can download the contents of the following SuperCollider script: [foxdot.scd](http://foxdot.org/wp-content/uploads/foxdot.scd). Once downloaded, open the file in SuperCollider and press Ctrl+Return to run it. This will make SuperCollider start listening for messages from renardo_lib.

#### Frequently Asked Questions

You can find answers to many frequently asked questions on the [FAQ post on the FoxDot discussion forum](http://foxdot.org/forum/?view=thread&id=1).

## Basics

### Executing Code

A 'block' of code in FoxDot is made up of consecutive lines of code with no empty lines. Pressing `Ctrl+Return` (or `Cmd+Return` on a Mac) will execute the block of code that the cursor is currently in. Try `print(1 + 1)` to see what happens!

### Player Objects

Python supports many different programming paradigms, including procedural and functional, but FoxDot implements a traditional object orientated approach with a little bit of cheating to make it easier to live code. A player object is what FoxDot uses to make music by assigning it a synth (the 'instrument' it will play) and some instructions, such as note pitches. All one and two character variable names are reserved for player objects at startup so, by default, the variables `a`, `bd`, and `p1` are 'empty' player objects. If you use one of these variables to store something else but want to use it as a player object again, or you  want to use a variable with more than two characters, you just have to reserve it by creating a `Player` and assigning it like so:

``` python
p1 = Player("p1") # The string name is optional
```

To stop a Player, use the `stop` method e.g. `p1.stop()`. If you want to stop all players, you can use the command `Clock.clear()` or the keyboard short-cut `Ctrl+.`, which executes this command.

Assigning synths and instructions to a player object is done using the double-arrow operator `>>`. So if you wanted to assign a synth to `p1` called 'pads' (execute `print(SynthDefs)` to see all available synths) you would use the following code:

``` python
p1 >> pads([0,1,2,3])
```

The empty player object, `p1` is now assigned a the 'pads' synth and some playback instructions. `p1` will play the first four notes of the default scale using a SuperCollider `SynthDef` with the name `\pads`. By default, each note lasts for 1 beat at 120 bpm. These defaults can be changed by specifying keyword arguments:

```python
p1 >> pads([0,1,2,3], dur=[1/4,3/4], sus=1, vib=4, scale=Scale.minor)
```

The keyword arguments `dur`, `oct`, and `scale` apply to all player objects - any others, such as `vib` in the above example, refer to keyword arguments in the corresponding `SynthDef`. The first argument, `degree`, does not have to be stated explicitly. Notes can be grouped together so that they are played simultaneously using round brackets, `()`. The sequence `[(0,2,4),1,2,3]` will play the the the first harmonic triad of the default scale followed by the next three notes. 

### 'Sample Player' Objects

In FoxDot, sound files can be played through using a specific SynthDef called `play`. A player object that uses this SynthDef is referred to as a Sample Player object. Instead of specifying a list of numbers to generate notes, the Sample Player takes a string of characters (known as a "PlayString") as its first argument. To see a list of what samples are associated to what characters, use `print(Samples)`. To create a basic drum beat, you can execute the following line of code:

``` python
d1 >> play("x-o-")
```

To have samples play simultaneously, you can create a new 'Sample Player' object for some more complex patterns.

``` python
bd >> play("x( x)  ")
hh >> play("---[--]")
sn >> play("  o ")
```

Alternatively, you can do this in one line using `<>` arrows to separate patterns you want to play together like so:

```python
d1 >> play("<x( x)  ><---[--]><  o >")
```

Or you can use `PZip`, the `zip` method, or the `&` sign to create one pattern that does this. This can be useful if you want to perform some function on individual layers later on:

``` python
d1 >> play(P["x( x)  "].palindrome().zip("---[--]").zip(P["  o "].amen()))  

# The first item must be a P[] pattern, not a string. 

d1 >> play(P["x( x)  "].palindrome() & "---[--]" & P["  o "].amen())
```

Grouping characters in round brackets laces the pattern so that on each play through of the sequence of samples, the next character in the group's sample is played. The sequence `(xo)---` would be played back as if it were entered `x---o---`. Using square brackets will force the enclosed samples to played in the same time span as a single character e.g. `--[--]` will play two hi-hat hits at a half beat then two at a quarter beat. You can play a random sample from a selection by using curly braces in your Play String like so:

``` python
d1 >> play("x-o{-[--]o[-o]}")
```

There is now the functionality to specify the sample number for an individual sample when using the `play` SynthDef. This can be done from the play string itself by using the bar character in the form `|<char><sample>|`. These can also be patterns created using brackets:

```python
# Plays the kick drum with sample 2 but the rest with sample 0
p1 >> play("|x2|-o-")

# You can use square brackets to play multiple samples
p1 >> play("|x[12]| o ")

# Round brackets alternate which sample is used on each loop through the sequence
p1 >> play("|x(12)| o ")

# Curly braces will pick a sample at random
p1 >> play("|x{0123}| o ")
```

## Scheduling Player methods

You can perform actions like shuffle, mirror, and rotate on Player Objects just by calling the appropriate method.

```python
bd >> play("x o  xo ")

# Shuffle the contents of bd
bd.shuffle()
```

You can schedule these methods by calling the `every` method, which takes a list of durations (in beats), the name of the method as a string, and any other arguments. The following syntax mirrors the string of sample characters after 6 beats, then again 2 beats  later and also shuffles it every 8 beats. 

```python
bd >> play("x-o-[xx]-o(-[oo])").every([6,2], 'mirror').every(8, 'shuffle')
```