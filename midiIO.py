from os.path import exists
from io import BufferedReader, FileIO
from typing import override, Any
from enum import Enum

import struct
import string

# Midi file spec found here
# https://www.music.mcgill.ca/~ich/classes/mumt306/StandardMIDIfileformat.html

# Defined by the spec
DEFAULT_TEMPO = 500000 # Beats per microsecond
DEFAULT_RESOLUTION = 4/4 

MESSAGES = {
    0x80: ('Note_Off', ("Note", "Velocity")),
    0x90: ('Note_On', ("Note", "Velocity")),
    0xa0: ('Polyphonic_Pressure', ("Note", "Value")),
    0xb0: ('Control_Change', ("Controller", "Value")),
    0xc0: ('Program_Change', ("Program")),
    0xd0: ('Channel_Pressure', ("Pressure")),
    0xf0: ('Pitch_Wheel', ("Low", "Most")),
}

# Define the beat by note
class BEAT(Enum): 
    SINGLE = 1
    DOUBLE = 2
    QUAD = 4

class BeatGenerator:
    def __init__(self, resolution: float = 1, tempo: int = DEFAULT_TEMPO, emit_beat: BEAT = BEAT.SINGLE, ticks_per_second: float = 0, ticks_per_quarter: int = 0):
        self.resolution: float = resolution
        self.tempo: int = tempo
        self.emit_beat: BEAT = emit_beat
        self.ticks_per_second: float = ticks_per_second
        self.ticks_per_quarter: int = ticks_per_quarter
        self.ticks: int = 0

    @property
    def seconds_per_beat(self):
        return self.tempo * 1e-6 / self.resolution

    @property
    def ticks_per_beat(self) -> int:
        if self.ticks_per_quarter != 0:
            return int(self.ticks_per_quarter / self.resolution)
        else:
            return int(self.ticks_per_second * self.seconds_per_beat)

    @property
    def ticks_per_emit(self) -> int:
        return int(self.ticks_per_beat / self.emit_beat.value)


    @staticmethod
    def from_format_zero(ticks_per_quarter: int = 0, emit_beat: BEAT = BEAT.SINGLE):
        return BeatGenerator(ticks_per_quarter=ticks_per_quarter, emit_beat=emit_beat)

    @staticmethod
    def from_format_one(ticks_per_second: float = 0, emit_beat: BEAT = BEAT.SINGLE):
        return BeatGenerator(ticks_per_second=ticks_per_second, emit_beat=emit_beat)


class DebugWrapper(BufferedReader):
    @override
    def read(self, size: int | None = None):
        data = super().read(size) 

        for byte in data:
            char = chr(byte)
            if char.isspace() or char not in string.printable:
                char = '.'
            print(f"  {(self.tell()):06x}: {byte:02x}  {char}")
        return data


class MidiReader():
    def __init__(self, filepath: str, emit_beat: BEAT = BEAT.SINGLE, debug: bool = False):
        if exists(filepath):
            self._filepath: str = filepath
            self.format: int | None = None
            self.debug: bool = debug
            self.tracks: list[list[int]] = []

            _ = self._load()
        else:
            raise OSError(f"File not found {filepath}")

    def _load(self):
        if self.debug:
            _fd = DebugWrapper(FileIO(self._filepath))
        else:
            _fd = BufferedReader(FileIO(self._filepath))

        chunk, length = read_chunk_header(_fd)
        if chunk != b'MThd' or length != 6:
            raise OSError(f"{self._filepath} is not a midi file")

        _dbg("\nHeader:", self.debug)
        data = _fd.read(length)

        self.format, ntrks, division = struct.unpack('>hhh', data)
        _dbg(f"-> format={self.format}, tracks={ntrks}", self.debug)

        beat_gen = read_tick_format(division)
        _dbg(f"-> ticks_per_beat={beat_gen.ticks_per_beat}", self.debug)


        self.tracks = [read_track(_fd, beat_gen, self.debug) for _ in range(ntrks)]

        _fd.close()
        return self

    def __iter__(self):
        pass
        #temp = DEFAULT_TEMPO
        #for msg in track:
            #yield msg.copy(skip_checks=True)

    def _merge_tracks(self, tracks, skip_checks):
        messages = []
        for track in tracks:
            messages

def _dbg(text: str, debug: bool): 
    if debug: print (text)

# Given by the spec in C
def read_variable_int(buff: BufferedReader):
    delta = 0

    while True:
        byte = ord(buff.read(1))
        delta = (delta << 7) | (byte & 0x7f)
        if byte < 0x80:
            return delta

def read_chunk_header(buff: BufferedReader) -> tuple[bytes, int]:
    header = buff.read(8)
    if len(header) < 8:
        raise EOFError
    return struct.unpack(">4sL", header)


def read_tick_format(division: int):
    if division & 0x8000 == 0x8000:
        fps = int.from_bytes(int.to_bytes(division & 0x7f00, signed=False), signed=True) * -1
        resolution = division & 0x00ff
        ticks_per_second = resolution * fps
        return BeatGenerator.from_format_one(ticks_per_second=ticks_per_second)
    else:
        ticks_per_quarter = division & 0x7fff
        return BeatGenerator.from_format_zero(ticks_per_quarter=ticks_per_quarter)


def read_track(buff: BufferedReader, beat_generator: BeatGenerator, debug: bool = False):
    track: list[list[int]] = list()
    last_beat: list[int] = []
    held_keys: list[int] = []
    to_remove: list[int] = []
    track_ticks: int = 0

    name, size = read_chunk_header(buff)
    if name != b'MTrk':
        raise OSError(f"Malformed track header read")

    start = buff.tell()
    last_status = None

    while buff.tell() - start != size:
        if buff.tell() - start > size:
            print(buff.tell(), start, size)
            raise EOFError

        _dbg("\nMessage:", debug)

        peek = 0
        delta_tick = read_variable_int(buff)
        _dbg(f"-> delta_time={delta_tick}", debug)

        if delta_tick + track_ticks > beat_generator.ticks_per_beat:
            track.append(held_keys)
            last_beat = held_keys.copy()
            _dbg(f"-> beat={held_keys}", debug)

            track_ticks %= beat_generator.ticks_per_beat

        status = ord(buff.read(1))

        if status < 0x80:
            # Omitted Case
            if last_status is None:
                raise OSError(f"Malformed status byte read")
            peek = status
            status = last_status
        else:
            # Non-omitted Case
            if status != 0xff:
                last_status = status
        _dbg(f"-> status={status}", debug)
        
        if status == 0xff:
            read_meta_event(buff)
        elif status in [0xf7, 0xf0]:
            raise NotImplementedError("MIDI contains System Exclusive message in which parsing isn't implemented")
        else:
            held_keys, to_remove = read_message(buff, status, peek, held_keys, last_beat, to_remove)
    return track

def read_message(buff: BufferedReader, status: int, peek: int, keys: list[int], prev_keys: list[int], to_remove: list[int]):
    status &= 0xf0
    spec = MESSAGES[status]
    
    if peek != 0x00:
        size = len(spec[1]) - 1
        data = [peek] + [ord(buff.read(1)) for _ in range(size)]
    else:
        size = len(spec[1])
        data = [ord(buff.read(1)) for _ in range(size)]

    if status == 0x80 or status == 0x90:
        note, velocity = data 

        if status == 0x80:
            keys.append(note)
        else:
            if note in prev_keys and note in keys:
                keys.remove(note)
            else:
                to_remove.append(note)
    else:
        _ = buff.read(size)
    return (keys, to_remove)

def read_meta_event(buff: BufferedReader):
    # We dont care about parsing meta events right now
    _ = buff.read(1)
    size = read_variable_int(buff)
    _ = buff.read(size)
    print("META")
