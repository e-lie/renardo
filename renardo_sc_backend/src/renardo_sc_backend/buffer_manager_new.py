from typing import Dict, Optional
from renardo_gatherer import SampleFile, SamplePackLibrary, LOOP_SUBDIR
import heapq

class Buffer:
    """Represents a SuperCollider buffer with its associated sample file."""

    def __init__(self, buffer_num: int, sample_file: SampleFile):
        self.buffer_num = buffer_num
        self.sample_file = sample_file
        self.name = sample_file.name

    def __str__(self) -> str:
        return f"Buffer({self.buffer_num}: {self.name})"

    def __repr__(self) -> str:
        return self.__str__()


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

    def clear(self):
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