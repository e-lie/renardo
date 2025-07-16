import unittest
from renardo.lib.ring import Ring, R

class TestRing(unittest.TestCase):
    
    def test_ring_creation(self):
        # Test direct creation
        r1 = Ring([1, 2, 3, 4])
        self.assertEqual(len(r1), 4)
        self.assertEqual(r1.data, [1, 2, 3, 4])
        
        # Test creation with R syntax
        r2 = R[1, 2, 3, 4]
        self.assertEqual(len(r2), 4)
        self.assertEqual(r2.data, [1, 2, 3, 4])
        
        # Test creation with slice
        r3 = R[0:4]
        self.assertEqual(len(r3), 4)
        self.assertEqual(r3.data, [0, 1, 2, 3])
        
    def test_ring_call(self):
        # Test the cycling behavior
        r = R[10, 20, 30]
        
        # First cycle
        self.assertEqual(r(), 10)
        self.assertEqual(r(), 20)
        self.assertEqual(r(), 30)
        
        # It should wrap around
        self.assertEqual(r(), 10)
        self.assertEqual(r(), 20)
        
    def test_ring_getitem(self):
        r = R["a", "b", "c", "d"]
        
        # Normal indexing
        self.assertEqual(r[0], "a")
        self.assertEqual(r[1], "b")
        self.assertEqual(r[2], "c")
        self.assertEqual(r[3], "d")
        
        # Test cycling with getitem
        self.assertEqual(r[4], "a")
        self.assertEqual(r[5], "b")
        self.assertEqual(r[6], "c")
        self.assertEqual(r[7], "d")
        
        # Test negative indices
        self.assertEqual(r[-1], "d")
        self.assertEqual(r[-2], "c")
        
    def test_ring_reset(self):
        r = R[1, 2, 3]
        
        # Advance the ring
        r()  # 1
        r()  # 2
        
        # Reset the ring
        r.reset()
        
        # Should start from beginning again
        self.assertEqual(r(), 1)
        
    def test_empty_ring(self):
        r = Ring([])
        self.assertEqual(r(), None)
        self.assertEqual(r[0], None)
        self.assertEqual(len(r), 0)

if __name__ == "__main__":
    unittest.main()