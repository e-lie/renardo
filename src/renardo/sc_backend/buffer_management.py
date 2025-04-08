#import fnmatch
#import os
#import wave
#from contextlib import closing
#from itertools import chain
#from os.path import abspath, join, isabs, isfile, isdir, splitext
#
#from renardo.gatherer import sample_pack_library
## from renardo.lib.Code import WarningMsg
## from renardo.lib.Logging import Timing
#from renardo.sc_backend.ServerManager.default_server import Server

from typing import Dict, Optional
import wave
from contextlib import closing
from pathlib import Path
import heapq

from renardo.settings_manager import settings

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
    def from_file(cls, sample_file, number):
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
    def __init__(self, server, sample_library, paths=None):
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
        self._sample_library = sample_library
        if paths:
            for path in paths:
                self._sample_library._extra_paths.append(Path(path))

    def __getitem__(self, key):
        """Get buffer from symbol (e.g., buffer_manager['x'])"""
        if isinstance(key, tuple):
            return self.get_buffer_from_symbol(*key)
        return self.get_buffer_from_symbol(key)

    def get_buffer_from_symbol(self, symbol: str, spack: int = 0, index: int = 0) -> Buffer:
        """Get a buffer by its symbol representation."""
        if symbol.isspace() or symbol=='.':
            return nil

        # Find the sample using SamplePackLibrary
        found_sample = self._sample_library._find_sample(symbol, index)
        if found_sample is None:
            return nil

        return self._allocate(found_sample)

    def _allocate(self, sample_file, force=False) -> Buffer:
        """Allocate and load a sample file into a SuperCollider buffer."""
        path_str = str(sample_file.path)

        # Check if already loaded
        if path_str in self._path_to_buffer and not force:
            return self._path_to_buffer[path_str]

        # Allocate new buffer if not loaded or forced reload
        if path_str not in self._path_to_buffer:
            if not self._available_numbers:
                raise RuntimeError("No available buffer numbers")
            buffer_num = heapq.heappop(self._available_numbers)
            buffer = Buffer.from_file(sample_file, buffer_num)
            self._buffers[buffer_num] = buffer
            self._path_to_buffer[path_str] = buffer

        else:  # force reload existing buffer
            buffer = self._path_to_buffer[path_str]

        # Load the sample into SuperCollider
        self._server.bufferRead(path_str, buffer.bufnum)
        return buffer

    def free_buffer(self, buffer_num: int) -> bool:
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

    def reallocate_buffers(self):
        """Reset buffer manager, reloading all samples."""
        paths = list(self._path_to_buffer.keys())

        # Free all allocated buffers
        buffer_nums = list(self._buffers.keys())
        for num in buffer_nums:
            self.free_buffer(num)

        for path in paths:
            sample = self._sample_library._find_sample(path)
            if sample:
                self._allocate(sample)

    def get_buffer(self, buffer_num: int) -> Optional[Buffer]:
        """
        Get a buffer by its number.

        Args:
            buffer_num: The buffer number to retrieve

        Returns:
            Buffer if found, None if not allocated
        """
        return self._buffers.get(buffer_num)

    def load_buffer(self, filename: str, index: int = 0, force: bool = False) -> int:
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
        buffer = self._allocate(found_sample, force=force)
        return buffer.bufnum



