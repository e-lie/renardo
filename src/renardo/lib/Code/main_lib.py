import sys
import re
import os.path
import time
from traceback import format_exc as error_stack
from types import CodeType, FunctionType

try:
    from types import TypeType
except ImportError:
    # Python 3 compatibility
    TypeType = type
    
from renardo.lib.Utils import modulo_index
from renardo.settings_manager import settings

"""
Live Object
===========

Base for any self-scheduling objects
"""

# Player RegEx - used to match player definitions in code
re_player = re.compile(r"(\s*?)(\w+)\s*?>>\s*?\w+")

# Macro RegEx - used to match scheduling macro definitions
re_macro = re.compile(r"^\s*#\s*\{(.+?)\}(?:\s+.*)?$")

class LiveObject(object):
    """ Base class for any self-scheduling objects """
    foxdot_object = True
    isAlive = True
    
    metro = None  # Reference to the metronome/clock
    step  = None  # Time between executions
    n     = 0     # Number of times executed
    
    def kill(self):
        """ Stop this object from scheduling itself """
        self.isAlive = False
        return self

    def __call__(self):
        """ Schedule this object to execute again """
        self.metro.schedule(self, self.metro.now() + float(modulo_index(self.step, self.n)))
        self.n += 1
        return self

"""
FoxCode
=======
Handles the execution of FoxDot code
"""

class CodeString:
    """ Wrapper for string that can be executed line by line """
    def __init__(self, raw):
        self.raw = raw
        self.iter = -1
        self.lines = [s + "\n" for s in self.raw.split("\n")] + ['']
    def readline(self):
        """ Return next line, used in compilation """
        self.iter += 1
        return self.lines[self.iter]
    def __str__(self):
        return self.raw

if sys.version_info[0] > 2:
    def clean(string):
        """ Cleans string by replacing unicode lambda symbol """
        string = string.replace("\u03BB", "lambda")
        return string
else:
    def clean(string):
        """ Removes non-ascii characters from a string for Python 2 """
        string = string.replace(u"\u03BB", "lambda")
        return string.encode("ascii", "replace")

class _StartupFile:
    """ Manages loading of startup file code """
    def __init__(self, path=None):
        self.path = None
        if path is not None:
            self.set_path(path)
    
    def set_path(self, path):
        """ Set the path to the startup file """
        if path is None:
            self.path = None
        else:
            self.path = os.path.realpath(path)
        return self

    def load(self):
        """ Load and return the content of the startup file """
        if self.path is not None:
            try:
                file = open(self.path)
                code = file.read()
                file.close()
                return code
            except (IOError, OSError):
                WarningMsg(f"'{self.path}' startup file not found.")
        return ""

# Initialize startup file - will be replaced by runtime.startup_files module
FOXDOT_STARTUP = _StartupFile()
        
class FoxDotCode:
    """ Handles execution of FoxDot code with namespace management """
    namespace={}  # Global namespace for executed code
    player_line_numbers={}  # Tracks line numbers of player definitions
    macro_counter = 0  # Counter for generating unique macro function names

    @staticmethod
    def _compile(string):
        """ Compiles a string of code to bytecode """
        return compile(str(CodeString(string)), "FoxDot", "exec")

    @classmethod
    def use_sample_directory(cls, directory):
        """ Forces FoxDot to look in `directory` instead of the default 
            directory when using audio samples. """
        return cls.namespace['symbolToDir'].set_root(directory)

    @classmethod
    def use_startup_file(cls, path):
        """ Set the path to a custom startup file """
        return cls.namespace['FOXDOT_STARTUP'].set_path(path)

    @classmethod
    def no_startup(cls):
        """ Disable the startup file """
        return cls.namespace["FOXDOT_STARTUP"].set_path(None)

    def load_startup_file(self): 
        """ Load and execute the startup file """
        code = self.namespace["FOXDOT_STARTUP"].load()
        return self.__call__(code, verbose=False)
    
    def transform_macros(self, code):
        """ Transform scheduling macros directly into Clock.schedule calls in the code
        
        IMPROVED IMPLEMENTATION:
        This function transforms macro syntax into discrete functions and Clock.schedule calls.
        
        Benefits of this approach:
        1. Single-phase execution: All code executes in one pass rather than separate phases
        2. Consistent namespace: Variables are properly shared between regular code and macros
        3. Better error handling: Issues are caught during compilation rather than at schedule time
        4. More intuitive: Transformation clearly shows the generated code equivalent
        5. Better debugging: Transformed code is more transparent and easier to understand
        
        The transformation converts:
        ```
        # {beat_expression}
        code_block
        code_block
        ```
        
        Into:
        ```
        # Auto-generated function for macro at beat_expression
        def _macro_func_N():
            code_block
            code_block
            
        # Schedule the function
        Clock.schedule(_macro_func_N, beat_expression)
        ```
        """
        lines = code.split('\n')
        transformed_lines = []
        current_macro = None
        current_block = []
        macro_counter = 0
        
        i = 0
        while i < len(lines):
            line = lines[i]
            macro_match = re_macro.match(line)
            
            if macro_match:
                # Start a new macro block
                current_macro = macro_match.group(1).strip()
                current_block = []
                i += 1
                
                # Collect all lines in the macro block until empty line or new macro
                while i < len(lines):
                    # Stop if we hit a new macro block
                    if re_macro.match(lines[i]):
                        break
                    # Stop if we hit an empty line
                    if lines[i].strip() == '':
                        i += 1  # Skip the empty line
                        break
                    # Otherwise add this line to the current block
                    current_block.append(lines[i])
                    i += 1
                
                # Generate function and Clock.schedule code if the block is not empty
                if current_block:
                    macro_counter += 1
                    func_name = f"_macro_func_{macro_counter}"
                    
                    # Create indented block for function body
                    indented_block = '\n    '.join(current_block)
                    if not indented_block.strip():
                        indented_block = "    pass"
                    else:
                        indented_block = '    ' + indented_block
                    
                    # Generate the function definition and Clock.schedule call
                    transformed_code = f"""def {func_name}():
{indented_block}

Clock.schedule({func_name}, beat={current_macro})

"""
                    transformed_lines.append(transformed_code)
                
                current_macro = None
                current_block = []
            else:
                # Regular code line, keep as is
                transformed_lines.append(line)
                i += 1
        
        return '\n'.join(transformed_lines)
                 
    def __call__(self, code, verbose=True, verbose_error=None):
        """ Takes a string of FoxDot code and executes as Python """

        # Check if clock is waiting for sync
        if self.namespace['_Clock'].waiting_for_sync:
            time.sleep(0.25)
            return self.__call__(code, verbose, verbose_error)

        if verbose_error is None:
            verbose_error = verbose

        if not code:
            return

        response = ""
        processed_code = code

        catching_exceptions_in_performance_code = settings.get("core.PERFORMANCE_EXCEPTIONS_CATCHING")

        if catching_exceptions_in_performance_code == True: 
            try:
                if type(code) != CodeType:
                    code = clean(code)
                    
                    # Transform macros directly into equivalent Clock.schedule calls
                    # This is an improved approach that replaces the old parse_macros/schedule_macros two-phase execution
                    # with a single-phase execution where macros are transformed into regular code
                    processed_code = self.transform_macros(code)
                    
                    response = stdout(processed_code)
                    if verbose is True:
                        print(response)

                # Execute the transformed code in a single step
                exec(self._compile(processed_code), self.namespace)

            # catch any exception in the executed code 
            except Exception as e:
                response = error_stack()
                if verbose_error is True:
                    print(response)

        else: # no exception catching 
            if type(code) != CodeType:
                code = clean(code)
                
                # Transform macros directly into equivalent Clock.schedule calls
                # This is an improved approach that replaces the old parse_macros/schedule_macros two-phase execution
                # with a single-phase execution where macros are transformed into regular code
                processed_code = self.transform_macros(code)
                
                response = stdout(processed_code)
                if verbose is True:
                    print(response)

            # Execute the transformed code in a single step
            exec(self._compile(processed_code), self.namespace)

        return response

    def update_line_numbers(self, text_widget, start="1.0", end="end", remove=0):
        """ Updates the line numbers of player objects in the editor """
        lines = text_widget.get(start, end).split("\n")[remove:]
        update = []
        offset = int(start.split(".")[0])

        for i, line in enumerate(lines):
            # Check line for a player and assign it a line number
            match = re_player.match(line)
            line_changed = False

            if match is not None:                
                whitespace = len(match.group(1))
                player     = match.group(2)
                line       = i + offset

                if player in self.player_line_numbers:
                    if (line, whitespace) != self.player_line_numbers[player]:
                        line_changed = True

                if line_changed or player not in self.player_line_numbers:
                    self.player_line_numbers[player] = (line, whitespace)
                    update.append("{}.id = '{}'".format(player, player))
                    update.append("{}.line_number = {}".format(player, line))
                    update.append("{}.whitespace  = {}".format(player, whitespace))

        # Execute updates if necessary
        if len(update) > 0:
            self.__call__("\n".join(update), verbose=False)
                
        return

# Main execution instance
execute = FoxDotCode()

def get_now(obj):
    """ Returns the value of objects if they are time-varying """
    return getattr(obj, 'now', lambda: obj).__call__()

def get_input():
    """ Similar to `input` but can handle multi-line input. Terminates on a final "\n" """
    line = " "; text = []
    
    while len(line) > 0:
        line = input("")
        text.append(line)

    return "\n".join(text)

def handle_stdin():
    """ When FoxDot is run with the --pipe flag, this function
        is called to continuously read from stdin """
    load_startup_file()

    while True:
        try:
            text = get_input()
            execute(text, verbose=False, verbose_error=True)
        except(EOFError, KeyboardInterrupt):
            sys.exit("Quitting")

def stdout(code):
    """ Format code for command line output """
    console_text = code.strip().split("\n")
    return ">>> {}".format("\n... ".join(console_text))

def debug_stdout(*args):
    """ Forces prints to server-side for debugging """
    sys.__stdout__.write(" ".join([str(s) for s in args]) + "\n")

def load_startup_file():
    """ Load and execute the startup file """
    return execute.load_startup_file()

def WarningMsg(*text):
    """ Print a warning message """
    print("Warning: {}".format(" ".join(str(s) for s in text)))

def write_to_file(fn, text):
    """ Write text to a file with proper encoding """
    try:
        with open(fn, "w") as f:
            f.write(clean(text))
    except IOError:
        print("Unable to write to {}".format(fn))
    return

# These functions return information about an imported module

def classes(module):
    """ Returns a list of class names defined in module """
    return [name for name, data in vars(module).items() if type(data) == TypeType]

def instances(module, cls):
    """ Returns a list of instances of cls from module """
    return [name for name, data in vars(module).items() if isinstance(data, cls)]

def functions(module):
    """ Returns a list of function names defined in module """
    return [name for name, data in vars(module).items() if type(data) == FunctionType]