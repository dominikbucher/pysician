from ..constants.notes import note_to_midi


def chord_to_notes(chord, prev_chord_notes=None, 
                   bass=True, bass_octave='2',
                   chord_octave='4'):
    """Takes a chord, and returns note for it, taking into account a variety
    of parameters as well as the previously played notes.

    :param chord: The chord to be transformed into notes.
    :param prev_chord_notes: If there was a previous chord (that is 
        important for this one), which notes were played.
    :param bass: If a bass note should be played.
    :param bass_octave: In which octave the bass plays.
    :param chord_octave: In which octave the chord mostly should play.
    """

    if not prev_chord_notes:
        top_notes = [note_to_midi[c + chord_octave] for c in chord.components()]
    else:
        top_notes = []
        for c in chord.components():
            candidates = [note_to_midi[c + str(oct)] for oct in range(1, 9)]
            top_notes.append(min(candidates, 
                key=lambda c: abs(min(prev_chord_notes, 
                key=lambda t: abs(c - t)) - c)))
        
    if bass:
        bass_note = note_to_midi[chord.root + bass_octave]
        return bass_note, top_notes
    else:
        return None, top_notes
