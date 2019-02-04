import sys, os, time, logging

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(
    os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# Set up midi.
from rtmidi.midiutil import open_midiport

try:
    midiout, port = open_midiport(4, "output",
        client_name="RtMidi Sequencer")
except (IOError, ValueError) as exc:
    print("Could not open MIDI input: %s" % exc)
except (EOFError, KeyboardInterrupt):
    print("Other error")

# Set up pysician.
from pysician.components.sequence import Sequence
from pysician.components.progression import ChordProgression, DrumProgression
from pysician.sequencer import Sequencer
from pysician.components.arpeggiator import arpeggiate

# Arpeggio
sequence_1 = Sequence(channel=0x00, bars=4)
progression_1 = ChordProgression('Cm Ab Bb Gm', bars=4)
arpeggiated_1 = [arpeggiate(notes, 1, i, mode='up') for i, notes in enumerate(progression_1.to_notes())]
arpeggiated_1 = [note for chord_notes in arpeggiated_1 for note in chord_notes]
sequence_1.add_notes(arpeggiated_1)

# Pad
sequence_2 = Sequence(channel=0x01, bars=4)
sequence_2.add_notes(progression_1.quick_notes())

# Drums
sequence_3 = Sequence(channel=0x02, bars=1)
pattern = """
D#2 -------------*--
 D2 -*-*-*-*-*-*-*-*
C#2 ----*-------*---
 C2 *-------*-------
"""
progression_2 = DrumProgression(pattern, 1/16)
sequence_3.add_notes(progression_2.notes)

sequencer = Sequencer(midiout, bpm=100, ppqn=240)
id_1 = sequencer.set_sequence(sequence_1)
id_2 = sequencer.set_sequence(sequence_2)
id_3 = sequencer.set_sequence(sequence_3)
# print(sequence_1)
# print(sequence_2)

sequencer.start_sequencer(bars=None)
time.sleep(24)
sequencer.stop_sequencer()
