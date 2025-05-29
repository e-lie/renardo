import unittest
from renardo.lib.ring import Ring, R
from renardo.lib.Patterns.Main import Pattern, as_pattern

# Create a simple mock class to test our Ring integration with __setattr__
class MockPlayer:
    def __init__(self):
        self.__dict__["__init"] = False
        self.__dict__["__vars"] = ['__init', '__vars', '_rings', 'attr', 'alias']
        self.__dict__["attr"] = {}
        self.__dict__["alias"] = {}
        self.__dict__["_rings"] = {}
        self.__dict__["__init"] = True
    
    def test_for_circular_reference(self, item, name):
        pass
    
    def update_pattern_root(self, name):
        pass
    
    def __setattr__(self, name, value):
        # Simplified version of Player.__setattr__ for testing
        if self.__init:
            if name not in self.__vars:
                
                # Special handling for Ring objects
                from renardo.lib.ring import Ring
                
                # Handle Ring objects
                if isinstance(value, Ring):
                    # Get the actual value from the Ring by calling it
                    actual_value = value()
                    
                    # Store or update the Ring in our dictionary
                    self._rings[name] = value
                    
                    # Use the value from the Ring for the attribute
                    value = actual_value
                elif name in self._rings:
                    # Check if we're setting the same Ring again (using equality comparison)
                    if hasattr(value, "__eq__") and value == self._rings[name]:
                        # Get the next value in the cycle from our stored Ring
                        value = self._rings[name]()
                    else:
                        # If setting something other than the same Ring, remove from dict
                        del self._rings[name]

                # Get any alias
                name = self.alias.get(name, name)
                value = as_pattern(value)

                # Update the attribute dict
                self.attr[name] = value
                return

        self.__dict__[name] = value
        return

class TestPlayerRing(unittest.TestCase):
    
    def setUp(self):
        # Create a mock player
        self.player = MockPlayer()
    
    def test_ring_cycling(self):
        """Test that a Ring cycles through values when repeatedly set to the same attribute."""
        # Create a Ring
        r = R[1, 2, 3]
        
        # Set the ring to the player's degree attribute
        self.player.degree = r
        
        # First time should give us the first value in the ring
        self.assertEqual(self.player.attr["degree"], Pattern([1]))
        
        # Set the same Ring again
        self.player.degree = r
        
        # Should get the second value
        self.assertEqual(self.player.attr["degree"], Pattern([2]))
        
        # Set the same Ring again
        self.player.degree = r
        
        # Should get the third value
        self.assertEqual(self.player.attr["degree"], Pattern([3]))
        
        # Set the same Ring again to cycle back to beginning
        self.player.degree = r
        
        # Should cycle back to the first value
        self.assertEqual(self.player.attr["degree"], Pattern([1]))
    
    def test_different_rings(self):
        """Test that different Ring objects with same values are treated as distinct."""
        # Create two different Ring objects with the same values
        r1 = R[1, 2, 3]
        r2 = R[1, 2, 3]
        
        # Set the first ring
        self.player.degree = r1
        
        # First value from r1
        self.assertEqual(self.player.attr["degree"], Pattern([1]))
        
        # Set a different Ring object with the same values
        self.player.degree = r2
        
        # Should get the first value from r2, not continue from r1
        self.assertEqual(self.player.attr["degree"], Pattern([1]))
        
        # Now set r1 again
        self.player.degree = r1
        
        # Should get the second value from r1
        self.assertEqual(self.player.attr["degree"], Pattern([2]))
    
    def test_non_ring_value(self):
        """Test that setting a non-Ring value after a Ring removes the stored Ring."""
        # Create a Ring
        r = R[1, 2, 3]
        
        # Set the ring
        self.player.degree = r
        
        # First value
        self.assertEqual(self.player.attr["degree"], Pattern([1]))
        
        # Set a non-Ring value
        self.player.degree = 10
        
        # Should get that value
        self.assertEqual(self.player.attr["degree"], Pattern([10]))
        
        # Set the same Ring again
        self.player.degree = r
        
        # Should start from the beginning of the Ring since we cleared it
        self.assertEqual(self.player.attr["degree"], Pattern([1]))
    
    def test_multiple_attributes(self):
        """Test that different attributes can have different Rings."""
        # Create two different Rings
        r1 = R[1, 2, 3]
        r2 = R["a", "b", "c"]
        
        # Set different attributes
        self.player.degree = r1
        self.player.dur = r2
        
        # Check initial values
        self.assertEqual(self.player.attr["degree"], Pattern([1]))
        self.assertEqual(self.player.attr["dur"], Pattern(["a"]))
        
        # Update both
        self.player.degree = r1
        self.player.dur = r2
        
        # Check next values
        self.assertEqual(self.player.attr["degree"], Pattern([2]))
        self.assertEqual(self.player.attr["dur"], Pattern(["b"]))
        
        # Update degree only
        self.player.degree = r1
        
        # Check values
        self.assertEqual(self.player.attr["degree"], Pattern([3]))
        self.assertEqual(self.player.attr["dur"], Pattern(["b"]))  # Unchanged

if __name__ == "__main__":
    unittest.main()