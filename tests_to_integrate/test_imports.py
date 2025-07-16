print("Starting import test...")

try:
    from renardo.runtime import *
    print("Successfully imported renardo.runtime")
except Exception as e:
    print(f"Error importing renardo.runtime: {e}")
    import traceback
    traceback.print_exc()