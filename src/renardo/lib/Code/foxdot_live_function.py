"""
Live Function Module

Allows functions to be continuously updated in a live coding context
"""

# Dictionary to store all live functions
_live_functions_dict = {}

class _live_function:
    """
    Wrapper for functions that can be updated dynamically during execution
    """
    def __init__(self, func, dependency=None):
        """
        Initialize a live function
        
        Args:
            func: The function to wrap
            dependency: Optional dependent live function
        """
        self.func = func
        self.name = func.__name__
        self.live = False
        self.dependency = dependency
        
    def __call__(self, *args, **kwargs):
        """
        Execute the function and update live status
        """
        self.live = True
        # If this function has a dependency, set its live status to False
        if isinstance(self.dependency, self.__class__):
            self.dependency.live = False
        return self.func.__call__(*args, **kwargs)
        
    def update(self, func, dependency=None):
        """
        Update the function implementation
        
        Args:
            func: New function implementation
            dependency: Optional new dependency
        """
        self.func = func
        if dependency:
            self.dependency = dependency
        return

def livefunction(f, dependency=None):
    """
    Decorator to create a live function that can be updated on-the-fly
    
    Args:
        f: Function to be made "live"
        dependency: Optional function this one depends on
        
    Returns:
        _live_function: Wrapped function
    """
    # Live functions can "depend" on others for switching from live or not
    if dependency in _live_functions_dict:
        dependency = _live_functions_dict[dependency.__name__]
        
    # Add / update a dictionary of all live functions
    if f.__name__ not in _live_functions_dict:
        _live_functions_dict[f.__name__] = _live_function(f, dependency)
    else:
        _live_functions_dict[f.__name__].update(f, dependency)
        
    f = _live_functions_dict[f.__name__]
    
    # If the function is "live" call it
    if f.live: 
        f.__call__()    
        
    return f


if __name__ == "__main__":
    # Debug test code
    @livefunction
    def part1():
        return 10

    @livefunction
    def part2():
        return 20

    part1()

    print(part1.__class__)