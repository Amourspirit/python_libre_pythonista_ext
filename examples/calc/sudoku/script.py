from lib import sudoku_calc


def generate_single_solve(*args, **kwargs) -> None:
    sudoku_calc.new_game()


def num1(*args, **kwargs) -> None:
    sudoku_calc.set_number(1)


def num2(*args, **kwargs) -> None:
    sudoku_calc.set_number(2)


def num3(*args, **kwargs) -> None:
    sudoku_calc.set_number(3)


def num4(*args, **kwargs) -> None:
    sudoku_calc.set_number(4)


def num5(*args, **kwargs) -> None:
    sudoku_calc.set_number(5)


def num6(*args, **kwargs) -> None:
    sudoku_calc.set_number(6)


def num7(*args, **kwargs) -> None:
    sudoku_calc.set_number(7)


def num8(*args, **kwargs) -> None:
    sudoku_calc.set_number(8)


def num9(*args, **kwargs) -> None:
    sudoku_calc.set_number(9)


def clear_sel(*args, **kwargs) -> None:
    sudoku_calc.clear_cell()


def reset_board(*args, **kwargs) -> None:
    sudoku_calc.reset_board()


def hint(*args, **kwargs) -> None:
    sudoku_calc.hint()


def hide_toolbars(*args, **kwargs) -> None:
    sudoku_calc.hide_toolbars()


def display_fullscreen(*args, **kwargs) -> None:
    sudoku_calc.display_fullscreen()
