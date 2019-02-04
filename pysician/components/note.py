from ..constants.notes import midi_to_note


class Note:
    """
    A single note to be played within a sequence.

    :param value: The note value as a midi code (21-127).
    :param position: When the note should be played (within a bar).
    :param length: How long the note should be played (in fractions of a bar).
    :param velocity: How "loud" then note should be (1-127).
    """
    def __init__(self, value, position, length, velocity):
        self.value = value
        self.position = position
        self.length = length
        self.velocity = velocity

    def __str__(self):
        return 'N(' + midi_to_note[self.value] + ',' + str(round(self.position, 2)) \
            + '-' + str(round(self.position + self.length, 2)) + ')'
