import pychord

from .note import Note
from .chord import chord_to_notes
from ..constants.notes import note_to_midi, midi_to_note


class ChordProgression():
    """A progression of chords.

    :param chords: The chords this progression is made from, e.g.,
        "C C F C" or "Cm Ab Bb Gm".
    :param bars: The number of bars over which the progression is spread.
    """
    def __init__(self, chords, bars):
        self.chord_progression = pychord.ChordProgression(chords.split())
        self.bars = bars

    def quick_notes(self):
        """Quickly transforms the chord progression into a simple collection of 
        notes to be played. 
        """
        progression_notes = self.to_notes()
        all_notes = []
        for chord_notes in progression_notes:
            for note in chord_notes:
                all_notes.append(note)
        return all_notes

    def to_notes(self, bass=True, bass_octave='2', chord_octave='4'):
        """Transforms the chord progression to a list of note collections. 
        For each chord, the collection consists of a bass note in octave 2 and
        chord notes in octave 4. For the chord notes, the nearest progression is chosen."""
        progression_notes = []
        note_lengths = self.bars / len(self.chord_progression)

        chord_notes = None
        for i, chord in enumerate(self.chord_progression):
            notes = []
            bass_note, chord_notes = chord_to_notes(chord, chord_notes, bass, bass_octave, chord_octave)
            if bass_note:
                notes.append(Note(bass_note, i*note_lengths, note_lengths, 100))
            for note in chord_notes:
                notes.append(Note(note, i*note_lengths, note_lengths, 100))
            progression_notes.append(notes)
        return progression_notes


class DrumProgression():
    """A progression of drums."""

    def __init__(self, pattern, step_length):
        self.notes = self.interpret_pattern(pattern, step_length)

    def interpret_pattern(self, pattern, step_length):
        notes = []
        for line in pattern.split('\n'):
            if len(line) == 0:
                continue
            midi_note = note_to_midi[line[:3].strip()]
            for i, char in enumerate(line[4:]):
                if char == '*':
                    notes.append(Note(midi_note, i*step_length, step_length, 100))
        return notes

    