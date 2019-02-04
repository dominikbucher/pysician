class Sequence():
    """A sequence to be played within a sequencer. A sequence 
    ultimately consists of individual notes to be played at a certain
    position within the sequence.
    """
    def __init__(self, channel, bars):
        self.channel = channel
        self.bars = bars
        self.notes = []

    def add_notes(self, notes):
        """Adds notes to this sequence."""
        self.notes = self.notes + notes

    def __str__(self):
        return 'S(' + ' '.join([str(n) for n in self.notes]) + ')'