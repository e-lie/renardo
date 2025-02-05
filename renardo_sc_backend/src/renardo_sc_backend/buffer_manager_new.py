from typing import Dict, Optional
import heapq
from pathlib import Path

from renardo_gatherer import SampleFile, SamplePackLibrary, LOOP_SUBDIR, get_samples_dir_path
from renardo_sc_backend.ServerManager.default_server import Server

class Buffer:
    """Represents a SuperCollider buffer with its associated sample file."""

    def __init__(self, buffer_num: int, sample_file: Optional[SampleFile], channels=1):
        self.buffer_num = buffer_num
        self.sample_file = sample_file
        self.name = sample_file.name
        self.channels = channels

    def __str__(self) -> str:
        return f"Buffer({self.buffer_num}: {self.name})"

    def __repr__(self) -> str:
        return self.__str__()

    def __int__(self):
        return self.buffer_num

nil = Buffer(buffer_num=0, sample_file=None)


class BufferManager:
    """Manages a collection of SuperCollider buffers with automatic numbering."""

    def __init__(self, supercollider_server, sample_pack_library):

        self._supercollider_server = supercollider_server
        self._sample_pack_library = sample_pack_library
        self.max_buffers = supercollider_server.max_buffers
        self._buffers: Dict[int, Buffer] = {}  # Maps buffer numbers to Buffer objects
        self._available_numbers = []  # Priority queue of available buffer numbers

        # Initialize available numbers (skip 0 as it's reserved for nil/empty buffer)
        for i in range(1, self.max_buffers):
            heapq.heappush(self._available_numbers, i)

    def allocate(self, sample_file: SampleFile) -> Optional[Buffer]:
        """
        Allocate a new buffer with the next available number.

        Args:
            path: Path to the sample file

        Returns:
            Buffer object if allocation successful, None if no numbers available
        """
        if not self._available_numbers:
            return None

        # Get the smallest available buffer number
        buffer_num = heapq.heappop(self._available_numbers)

        # Create and store the new buffer
        buffer = Buffer(buffer_num, sample_file)
        self._buffers[buffer_num] = buffer

        return buffer

    def free(self, buffer_num: int) -> bool:
        """
        Free a buffer number making it available for reuse.

        Args:
            buffer_num: The buffer number to free

        Returns:
            True if buffer was freed, False if buffer wasn't allocated
        """
        if buffer_num == 0:
            return False  # Can't free buffer 0

        if buffer_num not in self._buffers:
            return False

        # Remove the buffer and make its number available
        del self._buffers[buffer_num]
        heapq.heappush(self._available_numbers, buffer_num)

        return True

    def get(self, buffer_num: int) -> Optional[Buffer]:
        """Get the Buffer object for a given buffer number."""
        return self._buffers.get(buffer_num)

    def get_by_name(self, name: str) -> Optional[Buffer]:
        """Find a buffer by its sample name."""
        for buffer in self._buffers.values():
            if buffer.name == name:
                return buffer
        return None

    def is_allocated(self, buffer_num: int) -> bool:
        """Check if a buffer number is currently allocated."""
        return buffer_num in self._buffers

    def next_available(self) -> Optional[int]:
        """Get the next buffer number that would be allocated."""
        if not self._available_numbers:
            return None
        return self._available_numbers[0]  # Peek without popping

    @property
    def allocated_count(self) -> int:
        """Get the number of currently allocated buffers."""
        return len(self._buffers)

    @property
    def available_count(self) -> int:
        """Get the number of available buffer numbers."""
        return len(self._available_numbers)

    def list_buffers(self) -> Dict[int, str]:
        """Get a dictionary of allocated buffer numbers and their sample names."""
        return {num: buf.name for num, buf in self._buffers.items()}

    def free_all(self):
        """Free all allocated buffers."""
        # Reset buffers dictionary
        self._buffers.clear()

        # Reset available numbers
        self._available_numbers = []
        for i in range(1, self.max_buffers):
            heapq.heappush(self._available_numbers, i)

    def __len__(self) -> int:
        return len(self._buffers)

    def __str__(self) -> str:
        return f"BufferManager({len(self)}/{self.max_buffers} buffers allocated)"




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


sample_pack_library = SamplePackLibrary(root_directory=get_samples_dir_path())

buffer_manager =  BufferManager(supercollider_server=Server, sample_pack_library=sample_pack_library)
















# Example usage
if __name__ == "__main__":
    # Create a buffer manager with 8 slots for demonstration
    manager = BufferManager(max_buffers=8)

    # Allocate some buffers
    samples = [
        Path("kick.wav"),
        Path("snare.wav"),
        Path("hihat.wav")
    ]

    print("Allocating buffers:")
    allocated = []
    for sample in samples:
        buffer = manager.allocate(sample)
        if buffer:
            allocated.append(buffer)
            print(f"  {buffer}")

    print(f"\nAllocated: {manager.allocated_count}")
    print(f"Available: {manager.available_count}")
    print(f"Next available number: {manager.next_available()}")

    # Free a buffer
    if allocated:
        buffer = allocated.pop()
        print(f"\nFreeing {buffer}")
        manager.free(buffer.buffer_num)

    print(f"\nAllocated buffers:")
    for num, name in manager.list_buffers().items():
        print(f"  {num}: {name}")