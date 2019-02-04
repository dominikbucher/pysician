class MidiEvent(object):
    """An event that should be sent to midi out at a given
    time (tick).
    """

    __slots__ = ('tick', 'message')

    def __init__(self, tick, message):
        self.tick = tick
        self.message = message

    def __repr__(self):
        return "@ %05i %r" % (self.tick, self.message)

    def __eq__(self, other):
        return (self.tick == other.tick and
                self.message == other.message)

    def __lt__(self, other):
        return self.tick < other.tick

    def __le__(self, other):
        return self.tick <= other.tick

    def __gt__(self, other):
        return self.tick > other.tick

    def __ge__(self, other):
        return self.tick >= other.tick