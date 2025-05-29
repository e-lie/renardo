# Pattern Reference

Patterns are at the heart of Renardo's music creation system. This guide explains how to use and manipulate patterns effectively.

## What are Patterns?

In Renardo, patterns are sequences of values that can be manipulated algorithmically. They are used to create rhythms, melodies, and control various aspects of your music.

## Basic Pattern Types

Renardo offers several types of patterns:

### P - Standard Pattern

The basic pattern type, created using the `P` class:

```python
# Create a pattern of pitches
p1 >> pluck(P[0, 1, 2, 3])

# Create a pattern of durations
p1 >> pluck([0, 1, 2, 3], dur=P[1, 0.5, 0.25, 0.25])
```

### PGroup - Embedded Pattern

PGroups are used to play multiple values simultaneously:

```python
# Play chords (multiple notes at once)
p1 >> pluck([(0, 2, 4), (1, 3, 5)])

# Equivalent using P and PGroup syntax
p1 >> pluck(P[P(0, 2, 4), P(1, 3, 5)])
```

### PStep - Alternating Pattern

PStep patterns alternate between values at different rates:

```python
# Alternate between two values every cycle
p1 >> pluck(PStep(4, 0, 2))

# Create more complex alternating patterns
p1 >> pluck(PStep(3, [0, 1, 2], [3, 4, 5]))
```

## Pattern Methods

Patterns have numerous methods for algorithmic manipulation:

### Repetition and Expansion

```python
# Repeat the pattern twice
p1 >> pluck(P[0, 1, 2, 3].repeat(2))

# Stretch the pattern by repeating each value
p1 >> pluck(P[0, 1, 2, 3].stretch(2))
```

### Mathematical Operations

```python
# Add a value to all elements
p1 >> pluck(P[0, 1, 2, 3] + 2)  # Results in [2, 3, 4, 5]

# Multiply all elements
p1 >> pluck(P[0, 1, 2, 3] * 2)  # Results in [0, 2, 4, 6]
```

### Shuffling and Rearranging

```python
# Reverse the pattern
p1 >> pluck(P[0, 1, 2, 3].reverse())

# Shuffle the pattern randomly
p1 >> pluck(P[0, 1, 2, 3].shuffle())
```

## Pattern Generation

Renardo includes functions to generate patterns algorithmically:

```python
# Generate range of values
p1 >> pluck(PRand(0, 7))  # Random values between 0-7

# Generate random pattern from a list
p1 >> pluck(PChoice([0, 2, 4, 7]))
```

## Advanced Pattern Techniques

### Pattern Groups

Combine patterns to create complex sequences:

```python
# Alternate between two patterns
pattern = P[0, 1, 2, 3] | P[4, 5, 6, 7]

# Combine patterns sequentially
pattern = P[0, 1, 2, 3] + P[4, 5, 6, 7]
```

### Pattern Variables

Create and reuse patterns as variables:

```python
# Define a pattern variable
rhythm = P[0.25, 0.5, 0.25]

# Use in multiple players
p1 >> pluck([0, 1, 2, 3], dur=rhythm)
p2 >> bass([0, 4], dur=rhythm*2)
```

## Further Resources

- [Playing Samples](../samples/index.md) - How to use patterns with samples
- [TimeVar Objects](../timevars/index.md) - Time-varying values in patterns
- [Pattern Examples](./examples.md) - More complex pattern examples