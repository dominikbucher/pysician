from math import floor
import random

from .note import Note


def arpeggiate(note_values, bars, note_offset=0, 
               note_length=1/16, gate_length=3/64,
               mode='up', note_velocity=90):
    """Arpeggiates a collection of notes.
    
    :param note_values:
    :param bars:
    :param note_length:
    :param gate_length:
    :param mode:
    :param note_velocity:
    """

    if type(note_values[0]) is Note:
        sorted_notes = sorted(map(lambda n: n.value, note_values))
    else:
        sorted_notes = sorted(note_values)
    num_notes = floor(bars / note_length)
    notes = []

    if mode == 'up':
        for i in range(num_notes):
            notes.append(Note(sorted_notes[i % len(sorted_notes)], 
                              note_offset + i * note_length, gate_length, note_velocity - 40 + int((i % len(sorted_notes)) / len(sorted_notes) * 80)))
    elif mode == 'random':
        for i in range(num_notes):
            notes.append(Note(random.choice(sorted_notes), 
                              note_offset + i * note_length, gate_length, random.randint(70, 105)))

    return notes