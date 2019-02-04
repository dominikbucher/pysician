# Pysician - Python for Musicians

![Version](https://img.shields.io/badge/version-v0.0.1-red.svg)

Pysician is a live sequencer written in Python.
Basically, it generates MIDI notes at given points in time.
If you know DAWs like Ableton Live, you'll know more or less how it works.
You queue up sequences, and Python takes care that they are played in order.
Pysician features some tools to quickly and automatically generate sequences, such as arpeggiators, automated chord progressions, drum rolls, etc.

The project makes heavy use of and is inspired by [python-rtmidi](https://github.com/SpotlightKid/python-rtmidi).

**Attention**: I experience quite some lags, depending on the devices I'm using.
At the current stage, I cannot really recommend pysician for live performances.

# Installation and Usage

Take a look at the examples! 
First, you set up a midi port, then you create some sequences and fill them with notes, and finally you set up the sequencers, assign the sequences to it, and fire it off!

```python
sequence_1 = Sequence(channel=0x00, bars=4)
progression_1 = ChordProgression('Cm Ab Bb Gm', bars=4)
sequence_1.add_notes(progression_1.to_notes())

sequencer = Sequencer(midiout, bpm=100, ppqn=240)
id_1 = sequencer.set_sequence(sequence_1)
sequencer.start_sequencer(bars=None)
```

# Development

Pull requests are welcome.
At the moment everything is very much in an exploratory phase.