import threading
import time
import uuid

from collections import deque
from heapq import heappush, heappop

from rtmidi.midiconstants import CONTROL_CHANGE, ALL_SOUND_OFF, ALL_NOTES_OFF
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF

from .midi_event import MidiEvent
from .constants.notes import midi_to_note


class Sequencer(threading.Thread):
    """A sequencer takes sequence and outputs them on various midi channels, for
    now on a single midi out device. It has a certain number of beats per minute
    as well as a "pulses per quarter note" parameter that defines its resolution.

    :param midiout: The midi out device on which to send notes.
    :param bpm: The beats per minute played on this sequencer.
    :param ppqn: The number of "pulses per quarter note", i.e., the number of 
        ticks per beat (e.g., if ppqn=480, one beat or quarter note will have
        480 ticks or pulses, while a bar (4 beats) has 1920 pulses).
    """

    def __init__(self, midiout, bpm=120.0, ppqn=480):
        super(Sequencer, self).__init__()
        self.midiout = midiout

        # Setting up threading things.
        self.queue = deque()
        self._stopped = threading.Event()
        self._finished = threading.Event()

        # Counts elapsed ticks when sequence is running
        self._tickcnt = None

        # Max number of input queue events to get in one loop
        self._batchsize = 100

        # Setting up running sequences and sequencer constants.
        self.sequences = {}
        self.ppqn = ppqn
        self.bpm = bpm

        self.logfile = open('examples/log/log.txt', 'w')

    @property
    def bpm(self):
        """Return current beats-per-minute value."""
        return self._bpm

    @bpm.setter
    def bpm(self, value):
        self._bpm = value
        self._tick = 60. / value / self.ppqn

    def set_sequence(self, sequence, sequence_id=None):
        """Adds a sequence to the sequences playing within this sequencer."""
        if sequence_id is None:
            sequence_id = str(uuid.uuid4())
        self.sequences[sequence_id] = sequence
        return sequence_id
    
    def restart_sequences(self, tick):
        """This method is called whenever a bar passes. If a sequence needs to
        be restarted, this can be done here. 
        """
        for _, sequence in self.sequences.items():
            if tick % (4 * sequence.bars * self.ppqn) == 0:
                for note in sequence.notes:
                    self.add_event((NOTE_ON | sequence.channel, note.value, note.velocity), 
                        tick=tick + 4 * self.ppqn * note.position)
                    self.add_event((NOTE_OFF | sequence.channel, note.value, 0), 
                        tick=tick + 4 * self.ppqn * note.position + 4 * self.ppqn * note.length - 1)

    def print_notes(self):
        """Prints all the notes currently lined up in the sequences."""
        return ' '.join([str(s) for s in self.sequences.values()])

    def add_event(self, event, tick=None, delta=0):
        """Enqueue event for sending to MIDI output."""
        if tick is None:
            tick = self._tickcnt or 0

        if not isinstance(event, MidiEvent):
            event = MidiEvent(tick, event)

        if not event.tick:
            event.tick = tick

        event.tick += delta
        self.queue.append(event)

    def get_event(self):
        """Poll the input queue for events without blocking."""
        try:
            return self.queue.popleft()
        except IndexError:
            return None

    def handle_event(self, event):
        """Handle the event by sending it to MIDI out."""
        # print("Sending MIDI out:", event.message, "(" + str(midi_to_note[event.message[1]]) + ")")
        self.midiout.send_message(event.message)

    def run(self):
        """Start the thread's main loop.
        The thread will watch for events on the input queue and either send
        them immediately to the MIDI output or queue them for later output, if
        their timestamp has not been reached yet.
        """
        # busy loop to wait for time when next batch of events needs to
        # be written to output.
        pending = []
        self._tickcnt = 0
        if self._bars:
            ticks_to_play = 4 * self._bars * self.ppqn

        try:
            while not self._stopped.is_set():
                curtime = time.time()
                due = []

                # Check if we passed a bar, and need to restart some sequences.
                if self._tickcnt % (4 * self.ppqn) == 0:
                    self.restart_sequences(self._tickcnt)

                # Pop events off the pending queue if they are due for this tick.
                while True:
                    if not pending or pending[0].tick > self._tickcnt:
                        break

                    evt = heappop(pending)
                    heappush(due, evt)

                # Pop up to self._batchsize events off the input queue.
                for _ in range(self._batchsize):
                    evt = self.get_event()
                    if not evt:
                        break

                    # Check whether event should be sent out immediately
                    # or needs to be scheduled.
                    if evt.tick <= self._tickcnt:
                        heappush(due, evt)
                    else:
                        heappush(pending, evt)

                # If this batch contains any due events, send them 
                # to the MIDI output.
                if due:
                    for _ in range(len(due)):
                        self.handle_event(heappop(due))

                # Check if we can stop playing due to reaching the max bars to play.
                if self._bars and self._tickcnt > ticks_to_play:
                    self._stopped.set()

                # Loop speed adjustment.
                elapsed = time.time() - curtime
                if elapsed < self._tick:
                    time.sleep(self._tick - elapsed)
                self.logfile.write(str(curtime) + '\n')

                self._tickcnt += 1

        except KeyboardInterrupt:
            # log.debug("KeyboardInterrupt / INT signal received.")
            pass

        self.midiout.send_message((ALL_SOUND_OFF,))
        # Turn all notes of all sequences off (as some devices don't care
        # about the ALL_SOUND_OFF or NOTE_OFF messages).
        for _, sequence in self.sequences.items():
            for i in range(128):
                self.midiout.send_message((NOTE_OFF | sequence.channel, i, 0))
            self.midiout.send_message((CONTROL_CHANGE | sequence.channel, ALL_SOUND_OFF, 0))
            self.midiout.send_message((CONTROL_CHANGE | sequence.channel, ALL_NOTES_OFF, 0))

        self._finished.set()

    def start_sequencer(self, bars=None):
        """Starts the sequencer.
        
        :param bars: Set the number of bars for which this sequencer should play.
        """
        self._bars = bars
        self.start()

    def stop_sequencer(self, timeout=5):
        """Set thread stop event, causing it to exit its mainloop."""
        self._stopped.set()

        if self.is_alive():
            self._finished.wait(timeout)

        self.join()