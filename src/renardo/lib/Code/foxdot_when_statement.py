"""
When Statement Implementation

A 'when' statement is similar to an 'if' statement but continuously evaluates
the condition and executes the relevant code blocks whenever the condition
changes state.

Examples:

    when 5 < 10:
        print(True)
    else:
        print(False)

Currently there is no `elif` statement implemented yet and lines of code
cannot be spread over multiple lines.

To "stop" an individual `when` statement from monitoring its test, use the
`__when__` object with a `lambda` expression matching the test condition
and call the `remove` method:

Example:
    
    a, b = 5, 10
    
    when a > b:
        print("a is bigger")
    else:
        print("b is bigger")
    
    # This is how to 'stop' the statement above
    __when__(lambda: a > b).remove()
    
    # This removes *all* currently running when statements
    __when__.reset()
"""

from renardo.lib.Code.foxdot_func_cmp import *
from threading import Thread
from time import sleep

class _whenStatement:
    """
    Class for individual 'when' statements that continuously evaluate a condition
    """
    namespace = {}

    def __init__(self, func=lambda: True):
        """
        Initialize a when statement
        
        Args:
            func: Lambda function containing the condition to evaluate
        """
        self.expr = func
        self.reset()
        self.remove_me = False

    def __repr__(self):
        """String representation of the condition"""
        return func_str(self.expr)

    def __enter__(self):
        """Context manager entry"""
        when.editing = self
        return self

    def __exit__(self, *args):
        """Context manager exit"""
        when.editing = None
        return self

    @classmethod
    def set_namespace(cls, ns):
        """
        Define the namespace to execute the actions
        
        Args:
            ns: Dictionary namespace for execution
        """
        cls.namespace = ns

    def reset(self):
        """Reset the when and else actions to do nothing"""
        self.action = lambda: None
        self.notaction = lambda: None
        self.do_switch = False
        self.elsedo_switch = False

    def evaluate(self):
        """
        Evaluate the test expression and run appropriate response code
        if the condition has changed state
        """
        if self.expr():
            if not self.do_switch:
                self.action()
                self.toggle_live_functions(True)
                self.do_switch = True
                self.elsedo_switch = False
        else:
            if not self.elsedo_switch:
                self.notaction()
                self.toggle_live_functions(False)
                self.do_switch = False
                self.elsedo_switch = True

    def toggle_live_functions(self, switch):
        """
        Toggle live functions on/off if the action functions are @livefunctions
        
        Args:
            switch: Boolean indicating whether to enable or disable
        """    
        try:
            self.action.live = switch
        except:
            pass
        try:
            self.notaction.live = (not switch)
        except:
            pass
        return

    def when(self, func):
        """Set the condition function"""
        self.expr = func
        return self
                
    def then(self, func):
        """
        Set the function to execute when the condition is True
        
        Args:
            func: Function to execute
        """
        self.action = func
        return self
    
    def elsedo(self, func):
        """
        Set the function to execute when the condition is False
        
        Args:
            func: Function to execute
        """
        self.notaction = func
        return self
    
    def stop(self):
        """Reset the when statement"""
        self.reset()
        return self

    def remove(self):
        """Mark this when statement for removal"""
        self.reset()
        self.remove_me = True
        return self

class _whenLibrary:
    """
    Library to store and manage all 'when' statements
    Accessed through the `__when__` object
    """
    
    def __init__(self):
        """Initialize the when library"""
        self.library = {}
        self.editing = None
        
    def start_thread(self):
        """Start the monitoring thread for when statements"""
        self.thread = Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    @staticmethod
    def set_namespace(env):
        """Set the namespace for all when statements"""
        _whenStatement.set_namespace(env.namespace)

    def __len__(self):
        """Return the number of active when statements"""
        return len(self.library)

    def __repr__(self):
        """String representation of the library"""
        return repr(self.library)

    def run(self):
        """
        Continual loop evaluating all when statements
        """
        while len(self.library) > 0:
            for name, expression in self.library.items():
                if expression.remove_me == True:
                    del self.library[name]
                else:
                    expression.evaluate()
            sleep(0.01)
        return
        
    def __call__(self, name, **kwargs):
        """
        Access or create a when statement
        
        Args:
            name: Lambda function or identifier for the when statement
            
        Returns:
            _whenStatement: The requested or newly created when statement
        """   
        if name in self.library:
            return self.library[name]
        else:
            # Make a new statement
            self.library[name] = _whenStatement()

            # If that is the first statement, start the thread
            if len(self.library) == 1:
                self.start_thread()

            # Return the new statement
            return self.library[name]

    # Methods for context-based when statement editing
    def a(self, expr):
        """Set the condition for the currently edited when statement"""
        if self.editing is not None:
            self.editing.when(expr)            
        return None
        
    def b(self, expr):
        """Set the 'then' action for the currently edited when statement"""
        if self.editing is not None:
            self.editing.do(expr)
        return None
        
    def c(self, expr):
        """Set the 'else' action for the currently edited when statement"""
        if self.editing is not None:
            self.editing.elsedo(expr)
        return None

    def reset(self):
        """Clear all when statements"""
        self.library = {}
        return self

# Create the global when library
when = _whenLibrary()