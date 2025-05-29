"""
Contains the class `Ring` which is a collection that cycles through its elements when called.
"""

from renardo.lib.Patterns.Main import convert_nested_data

class Ring:
    """
    A Ring is a collection that cycles through its elements when called.
    Similar to Pattern, but specifically designed for cycling through elements
    of any kind in order.
    
    Example:
        >>> r = Ring([0, 1, 2, 3])
        >>> r()
        0
        >>> r()
        1
        >>> r()
        2
        >>> r()
        3
        >>> r()
        0
    """
    
    def __init__(self, data):
        """
        Initialize a Ring with the given data.
        
        Args:
            data: List or other iterable to initialize the Ring with.
        """
        self.data = data
        # Convert nested data (similar to Pattern)
        # self.data = list(map(convert_nested_data, self.data))
        
        # Index for tracking position in the ring
        self.index = 0
    
    def __repr__(self):
        return f"Ring{self.data}"
        
    def __str__(self):
        return f"Ring{self.data}"
    
    def __len__(self):
        return len(self.data)
    
    def __call__(self):
        """
        Returns the next element in the Ring and advances the index.
        
        Returns:
            The next element in the Ring.
        """
        if not self.data:
            return None
            
        value = self.data[self.index]
        self.index = (self.index + 1) % len(self.data)
        return value
    
    def __getitem__(self, key):
        """
        Get an item at a specific index.
        
        Args:
            key: Index to retrieve.
            
        Returns:
            The item at the specified index.
        """
        if len(self.data) == 0:
            return None
            
        return self.data[key % len(self.data)]
    
    def reset(self):
        """
        Reset the ring to start from the beginning.
        """
        self.index = 0
        return self
    
    def __eq__(self, other):
        """
        Check if two Rings contain the same elements in the same order.
        
        Args:
            other: Another Ring or list-like object to compare with.
            
        Returns:
            bool: True if the elements are the same in the same order, False otherwise.
        """
        if isinstance(other, Ring):
            return self.data == other.data
        elif hasattr(other, '__len__') and hasattr(other, '__getitem__'):
            if len(self.data) != len(other):
                return False
            return all(self.data[i] == other[i] for i in range(len(self.data)))
        return False

    @classmethod
    def fromList(cls, data):
        """
        Create a Ring from a list.
        
        Args:
            data: List to convert to a Ring.
            
        Returns:
            A new Ring object.
        """
        return cls(data)

# Define __getitem__ for list-style syntax with square brackets
class RingIndexer:
    """
    Utility class to enable R[a, b, c] syntax for creating Rings.
    """
    def __getitem__(self, args):
        if isinstance(args, slice):
            start = args.start if args.start is not None else 0
            stop = args.stop
            step = args.step if args.step is not None else 1
            return Ring(list(range(start, stop, step)))
        
        if not isinstance(args, tuple):
            args = [args]
            
        return Ring(args)

# Create an instance for use as the R shorthand
R = RingIndexer()