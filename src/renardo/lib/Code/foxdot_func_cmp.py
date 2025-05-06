"""
Functions for comparing and processing Python functions
"""

def func_cmp(funcA, funcB):
    """
    Compare two functions to determine if they are identical
    
    Args:
        funcA: First function to compare
        funcB: Second function to compare
        
    Returns:
        bool: True if functions are identical (same bytecode, constants and variables)
    """
    codeA = funcA.__code__
    A_bytecode  = codeA.co_code
    A_constants = codeA.co_consts
    A_variables = codeA.co_names

    codeB = funcB.__code__
    B_bytecode  = codeB.co_code
    B_constants = codeB.co_consts
    B_variables = codeB.co_names
    
    return all([A_bytecode == B_bytecode,
                A_constants == B_constants,
                A_variables == B_variables])

def func_str(func):
    """
    Returns a function as a string representation for unique identification
    
    Args:
        func: Function to convert to string
        
    Returns:
        str: String representation of the function
    """
    code = func.__code__
    return ",".join([func.__name__, str(code.co_names), str(code.co_consts)])