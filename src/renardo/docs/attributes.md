# Player Attributes

In Renardo, player attributes allow you to control various aspects of how your sounds are produced and manipulated. This guide covers the most important attributes and how to use them.

## Core Attributes

These are the fundamental attributes used with most players:

### `dur` - Duration

Controls the duration of each note or sample:

```python
# Quarter notes (1 beat each)
p1 >> pluck([0, 1, 2, 3], dur=1)

# Eighth notes (0.5 beats each)
p1 >> pluck([0, 1, 2, 3], dur=0.5)

# Varying durations
p1 >> pluck([0, 1, 2, 3], dur=[0.5, 0.25, 0.25, 1])
```

### `amp` - Amplitude

Controls the volume of the sound:

```python
# Normal volume
p1 >> pluck([0, 1, 2, 3], amp=1)

# Quiet
p1 >> pluck([0, 1, 2, 3], amp=0.5)

# Dynamic volume pattern
p1 >> pluck([0, 1, 2, 3], amp=[1, 0.8, 0.6, 0.8])
```

### `pan` - Panning

Controls the stereo position (left to right):

```python
# Center
p1 >> pluck([0, 1, 2, 3], pan=0)

# Left channel
p1 >> pluck([0, 1, 2, 3], pan=-1)

# Right channel
p1 >> pluck([0, 1, 2, 3], pan=1)

# Moving across stereo field
p1 >> pluck([0, 1, 2, 3], pan=linvar([-1, 1], 8))
```

### `oct` - Octave

Sets the octave of the notes:

```python
# Default octave
p1 >> pluck([0, 1, 2, 3])

# One octave up
p1 >> pluck([0, 1, 2, 3], oct=5)

# One octave down
p1 >> pluck([0, 1, 2, 3], oct=3)

# Octave pattern
p1 >> pluck([0, 1, 2, 3], oct=[4, 5, 4, 5])
```

## Timing Attributes

These attributes affect the timing of notes:

### `delay` - Delay

Delays the notes by a specified amount:

```python
# Delay by half a beat
p1 >> pluck([0, 1, 2, 3], delay=0.5)

# Different delays for each note
p1 >> pluck([0, 1, 2, 3], delay=[0, 0.25, 0, 0.25])
```

### `sus` - Sustain

Controls how long notes are held (relative to duration):

```python
# Short, staccato notes
p1 >> pluck([0, 1, 2, 3], sus=0.1)

# Long, sustained notes
p1 >> pluck([0, 1, 2, 3], sus=2)

# Varying sustain pattern
p1 >> pluck([0, 1, 2, 3], sus=[0.1, 1, 0.5, 2])
```

## Sound Shaping Attributes

These attributes modify the timbre and character of the sound:

### `lpf` - Low Pass Filter

Filters out frequencies above the specified value:

```python
# Only allow lower frequencies
p1 >> pluck([0, 1, 2, 3], lpf=500)

# Changing filter cutoff
p1 >> pluck([0, 1, 2, 3], lpf=linvar([500, 5000], 8))
```

### `hpf` - High Pass Filter

Filters out frequencies below the specified value:

```python
# Only allow higher frequencies
p1 >> pluck([0, 1, 2, 3], hpf=1000)

# Changing filter cutoff
p1 >> pluck([0, 1, 2, 3], hpf=linvar([2000, 200], 16))
```

### `room` - Reverb Room Size

Controls the size of the virtual room for reverb:

```python
# Small room reverb
p1 >> pluck([0, 1, 2, 3], room=0.3)

# Large hall reverb
p1 >> pluck([0, 1, 2, 3], room=0.9)
```

### `chop` - Chop Effect

Divides each note into multiple segments:

```python
# Chop each note into 4 pieces
p1 >> pluck([0, 1, 2, 3], chop=4)

# Different chop values
p1 >> pluck([0, 1, 2, 3], chop=[4, 8, 2, 4])
```

## Pattern Modification Attributes

These attributes change how pattern values are interpreted:

### `scale` - Musical Scale

Sets the scale used to interpret numerical values:

```python
# Default scale (major)
p1 >> pluck([0, 1, 2, 3])

# Minor scale
p1 >> pluck([0, 1, 2, 3], scale=Scale.minor)

# Pentatonic scale
p1 >> pluck([0, 1, 2, 3], scale=Scale.penta)
```

### `root` - Root Note

Sets the root note of the scale:

```python
# Default root (C)
p1 >> pluck([0, 1, 2, 3])

# D as root
p1 >> pluck([0, 1, 2, 3], root=2)

# Changing root over time
p1 >> pluck([0, 1, 2, 3], root=var([0, 2, 4], 4))
```

## Working with Attribute Patterns

Attributes can use all the same pattern manipulation techniques as note values:

```python
# Pattern operations on attributes
p1 >> pluck([0, 1, 2, 3], dur=P[0.5, 0.25, 0.25].stretch(2))

# Using pattern variables
rhythm = P[0.5, 0.25, 0.25, 1]
amp_pattern = P[1, 0.8, 0.6, 0.8]
p1 >> pluck([0, 1, 2, 3], dur=rhythm, amp=amp_pattern)

# Using TimeVar objects
p1 >> pluck([0, 1, 2, 3], lpf=linvar([500, 5000], 8))
```

## Additional Resources

<!-- - [Complete Attribute Reference](./complete_reference.md) - All available attributes -->
- [Pattern Guide](../patterns/index.md) - More on pattern manipulation
- [TimeVar Guide](../timevars/index.md) - Using time-varying values with attributes