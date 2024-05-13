from ooodev.macro.macro_loader import MacroLoader
from range_action import create_array, clear_range

def fill(*args, **kwargs) -> None:
    with MacroLoader():
        create_array()

def clear(*args, **kwargs) -> None:
    with MacroLoader():
        clear_range()
