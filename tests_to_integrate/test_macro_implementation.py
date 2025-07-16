import sys
import unittest
import os

# Add src directory to path so we can import renardo modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from renardo.lib.Code.main_lib import FoxDotCode


class TestMacroImplementation(unittest.TestCase):
    def setUp(self):
        # Create a fresh instance of FoxDotCode for each test
        self.fox_code = FoxDotCode()
        
        # Mock the Clock namespace
        self.fox_code.namespace = {
            '_Clock': type('_ClockMock', (), {'waiting_for_sync': False}),
            'Clock': type('ClockMock', (), {
                'schedule': self.mock_schedule,
                'now': lambda: 0
            }),
        }
        
        # Track scheduled calls for verification
        self.scheduled_calls = []
    
    def mock_schedule(self, func, time):
        """Mock for Clock.schedule that records calls"""
        self.scheduled_calls.append((func, time))
        return None
    
    def test_basic_macro_transformation(self):
        """Test that a basic macro is correctly transformed"""
        code = """# {Clock.now()+8}
print("This should be scheduled for 8 beats later")
"""
        transformed = self.fox_code.transform_macros(code)
        
        # Check that transformation contains function definition and Clock.schedule with beat= parameter
        self.assertIn("def _macro_func_", transformed)
        self.assertIn("Clock.schedule(_macro_func_", transformed)
        self.assertIn("beat=Clock.now()+8", transformed)
        self.assertIn("print(\"This should be scheduled for 8 beats later\")", transformed)
    
    def test_multiline_macro_transformation(self):
        """Test that a multiline macro is correctly transformed"""
        code = """# {pit3-32}
b1.fadein(32)  # rising melody for 32 beats before break
print("More code in the same macro")
"""
        transformed = self.fox_code.transform_macros(code)
        
        # Check that all lines are included in the function body
        self.assertIn("b1.fadein(32)", transformed)
        self.assertIn("print(\"More code in the same macro\")", transformed)
        self.assertIn("pit3-32", transformed)
        self.assertIn("def _macro_func_", transformed)
    
    def test_multiple_macros_transformation(self):
        """Test that multiple macros are correctly transformed"""
        code = """# {pit3-32}
b1.fadein(32)

# {pit3}
d2.amplify = 0
"""
        transformed = self.fox_code.transform_macros(code)
        
        # Check that both macros are transformed
        self.assertIn("pit3-32", transformed)
        self.assertIn("b1.fadein(32)", transformed)
        self.assertIn("pit3", transformed)
        self.assertIn("d2.amplify = 0", transformed)
        
        # Ensure we have two separate Clock.schedule calls and function definitions
        schedule_count = transformed.count("Clock.schedule(")
        function_count = transformed.count("def _macro_func_")
        self.assertEqual(schedule_count, 2)
        self.assertEqual(function_count, 2)
    
    def test_consecutive_macros_without_empty_line(self):
        """Test that consecutive macros without empty lines are correctly transformed"""
        code = """# {pit3-32}
b1.fadein(32)
# {pit3}
d2.amplify = 0
# {pit3+32}
b1.stop()
"""
        transformed = self.fox_code.transform_macros(code)
        
        # Check that all three macros are correctly transformed
        self.assertIn("pit3-32", transformed)
        self.assertIn("b1.fadein(32)", transformed)
        self.assertIn("pit3", transformed)
        self.assertIn("d2.amplify = 0", transformed)
        self.assertIn("pit3+32", transformed)
        self.assertIn("b1.stop()", transformed)
        
        # Ensure we have three separate Clock.schedule calls and function definitions
        schedule_count = transformed.count("Clock.schedule(")
        function_count = transformed.count("def _macro_func_")
        self.assertEqual(schedule_count, 3)
        self.assertEqual(function_count, 3)
    
    def test_example_drum_formatting(self):
        """Test the exact output format for the drums example"""
        code = """# {somebreak} cut drums for 16 beats
d2.amplify=0 # break (cutting the drum)
k2.amplify=0
# {somebreak+16} # Put back the drums 16 beats later
d2.amplify=1
k2.amplify=1"""
        
        transformed = self.fox_code.transform_macros(code)
        
        # Check for correct function definitions with proper indentation
        self.assertIn("def _macro_func_1():", transformed)
        self.assertIn("    d2.amplify=0 # break (cutting the drum)", transformed)
        self.assertIn("    k2.amplify=0", transformed)
        self.assertIn("Clock.schedule(_macro_func_1, beat=somebreak)", transformed)
        
        self.assertIn("def _macro_func_2():", transformed)
        self.assertIn("    d2.amplify=1", transformed)
        self.assertIn("    k2.amplify=1", transformed)
        self.assertIn("Clock.schedule(_macro_func_2, beat=somebreak+16)", transformed)


if __name__ == '__main__':
    unittest.main()