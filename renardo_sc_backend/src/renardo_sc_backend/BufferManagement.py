#import fnmatch
#import os
#import wave
#from contextlib import closing
#from itertools import chain
#from os.path import abspath, join, isabs, isfile, isdir, splitext
#
#from renardo_gatherer import default_loop_path, sample_pack_library
## from renardo_lib.Code import WarningMsg
## from renardo_lib.Logging import Timing
#from renardo_sc_backend.ServerManager.default_server import Server

from typing import Dict, Optional
import wave
from contextlib import closing
from pathlib import Path
import heapq

from renardo_gatherer import sample_pack_library
from renardo_sc_backend.ServerManager.default_server import Server

alpha    = "abcdefghijklmnopqrstuvwxyz"


class Buffer:
    def __init__(self, sample_file, buffer_num: int, channels: int = 1):
        self.sample_file = sample_file
        self.bufnum = int(buffer_num)  # Keep bufnum for backward compatibility
        self.buffer_num = int(buffer_num)  # New style naming
        self.channels = channels
        self.fn = str(sample_file.path) if sample_file else ""  # Keep fn for backward compatibility

    def __repr__(self):
        return f"<Buffer num {self.bufnum}>"

    def __int__(self):
        return self.bufnum

    @classmethod
    def fromFile(cls, sample_file, number):
        """Create Buffer from a sample file, detecting number of channels."""
        try:
            with closing(wave.open(str(sample_file.path))) as snd:
                numChannels = snd.getnchannels()
        except (wave.Error, AttributeError):
            numChannels = 1
        return cls(sample_file, number, numChannels)


# Create empty buffer (buffer 0)
nil = Buffer(None, 0)


class BufferManager:
    def __init__(self, server=Server, paths=None):
        self._server = server
        self._max_buffers = server.max_buffers

        # Initialize available buffer numbers (skip 0 for nil buffer)
        self._available_numbers = []
        for i in range(1, self._max_buffers):
            heapq.heappush(self._available_numbers, i)

        # Storage for buffers
        self._buffers: Dict[int, Buffer] = {}  # number -> Buffer
        self._path_to_buffer: Dict[str, Buffer] = {}  # path -> Buffer

        # Set up sample pack library paths
        self._sample_library = sample_pack_library
        if paths:
            for path in paths:
                self._sample_library._extra_paths.append(Path(path))

    def __getitem__(self, key):
        """Get buffer from symbol (e.g., buffer_manager['x'])"""
        if isinstance(key, tuple):
            return self.getBufferFromSymbol(*key)
        return self.getBufferFromSymbol(key)

    def getBufferFromSymbol(self, symbol: str, spack: int = 0, index: int = 0) -> Buffer:
        """Get a buffer by its symbol representation."""
        if symbol.isspace():
            return nil

        # Find the sample using SamplePackLibrary
        found_sample = self._sample_library._find_sample(symbol, index)
        if found_sample is None:
            return nil

        return self._allocateAndLoad(found_sample)

    def _allocateAndLoad(self, sample_file, force=False) -> Buffer:
        """Allocate and load a sample file into a buffer."""
        path_str = str(sample_file.path)

        # Check if already loaded
        if path_str in self._path_to_buffer and not force:
            return self._path_to_buffer[path_str]

        # Allocate new buffer if not loaded or forced reload
        if path_str not in self._path_to_buffer:
            if not self._available_numbers:
                raise RuntimeError("No available buffer numbers")
            buffer_num = heapq.heappop(self._available_numbers)
            buffer = Buffer.fromFile(sample_file, buffer_num)
            self._buffers[buffer_num] = buffer
            self._path_to_buffer[path_str] = buffer

        else:  # force reload existing buffer
            buffer = self._path_to_buffer[path_str]

        # Load the sample into SuperCollider
        self._server.bufferRead(path_str, buffer.bufnum)
        return buffer

    def free(self, buffer_num: int) -> bool:
        """Free a buffer by its number."""
        if buffer_num == 0 or buffer_num not in self._buffers:
            return False

        buffer = self._buffers[buffer_num]
        path_str = str(buffer.sample_file.path) if buffer.sample_file else ""

        # Remove from mappings
        del self._buffers[buffer_num]
        if path_str in self._path_to_buffer:
            del self._path_to_buffer[path_str]

        # Free on server
        self._server.bufferFree(buffer_num)

        # Make number available again
        heapq.heappush(self._available_numbers, buffer_num)
        return True

    def freeAll(self):
        """Free all allocated buffers."""
        buffer_nums = list(self._buffers.keys())
        for num in buffer_nums:
            self.free(num)

    def reset(self):
        """Reset buffer manager, reloading all samples."""
        paths = list(self._path_to_buffer.keys())
        self.freeAll()
        for path in paths:
            sample = self._sample_library._find_sample(path)
            if sample:
                self._allocateAndLoad(sample)

    def getBuffer(self, buffer_num: int) -> Optional[Buffer]:
        """
        Get a buffer by its number.

        Args:
            buffer_num: The buffer number to retrieve

        Returns:
            Buffer if found, None if not allocated
        """
        return self._buffers.get(buffer_num)

    def loadBuffer(self, filename: str, index: int = 0, force: bool = False) -> int:
        """
        Load a sample file into a buffer by filename or pattern.

        Args:
            filename: Path or pattern to find the sample
            index: Which sample to use if multiple matches (default: 0)
            force: Force reload if already loaded (default: False)

        Returns:
            Buffer number if successful, 0 if sample not found
        """
        # Find the sample using SamplePackLibrary
        found_sample = self._sample_library._find_sample(filename, index)
        if found_sample is None:
            return 0

        # Allocate and load the buffer
        buffer = self._allocateAndLoad(found_sample, force=force)
        return buffer.bufnum



DESCRIPTIONS = { 'a' : "Gameboy hihat",      'A' : "Gameboy kick drum",
                 'b' : "Noisy beep",         'B' : "Short saw",
                 'c' : "Voice/string",       'C' : "Choral",
                 'd' : "Woodblock",          'D' : "Dirty snare",
                 'e' : "Electronic Cowbell", 'E' : "Ringing percussion",
                 'f' : "Pops",               'F' : "Trumpet stabs",
                 'g' : "Ominous",            'G' : "Ambient stabs",
                 'h' : "Finger snaps",       'H' : "Clap",
                 'i' : "Jungle snare",       'I' : "Rock snare",
                 'j' : "Whines",             'J' : "Ambient stabs",
                 'k' : "Wood shaker",        'K' : "Percussive hits",
                 'l' : "Robot noise",        'L' : "Noisy percussive hits",
                 'm' : "808 toms",           'M' : "Acoustic toms",
                 'n' : "Noise",              'N' : "Gameboy SFX",
                 'o' : "Snare drum",         'O' : "Heavy snare",
                 'p' : "Tabla",              'P' : "Tabla long",
                 'q' : "Ambient stabs",      'Q' : "Electronic stabs",
                 'r' : "Metal",              'R' : "Metallic",
                 's' : "Shaker",             'S' : "Tamborine",
                 't' : "Rimshot",            'T' : "Cowbell",
                 'u' : "Soft snare",         'U' : "Misc. Fx",
                 'v' : "Soft kick",          'V' : "Hard kick",
                 'w' : "Dub hits",           'W' : "Distorted",
                 'x' : "Bass drum",          'X' : "Heavy kick",
                 'y' : "Percussive hits",    'Y' : "High buzz",
                 'z' : "Scratch",            "Z" : "Loud stabs",
                 '-' : "Hi hat closed",      "|" : "Hangdrum",
                 '=' : "Hi hat open",        "/" : "Reverse sounds",
                 '*' : "Clap",               "\\" : "Lazer",
                 '~' : "Ride cymbal",        "%" : "Noise bursts",
                 '^' : "'Donk'",             "$" : "Beatbox",
                 '#' : "Crash",              "!" : "Yeah!",
                 '+' : "Clicks",             "&" : "Chime",
                 '@' : "Gameboy noise",      ":" : "Hi-hats",
                 '1' : "Vocals (One)",
                 '2' : 'Vocals (Two)',
                 '3' : 'Vocals (Three)',
                 '4' : 'Vocals (Four)'}

# Samples and DefaultSamples just display default samples list (compat with FoxDot print(Samples))
DefaultSamples = Samples = "\n".join(["%r: %s" % (k, v) for k, v in sorted(DESCRIPTIONS.items())])

buffer_manager =  BufferManager()
