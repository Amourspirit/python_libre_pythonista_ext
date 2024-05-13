from pprint import pprint

# from random import sample
from typing import List, Optional
import random
from itertools import islice

base = 3
side = base * base
_EMPTY = 0
# grid = [[5,3,0,0,7,0,0,0,0],
#         [6,0,0,1,9,5,0,0,0],
#         [0,9,8,0,0,0,0,6,0],
#         [8,0,0,0,6,0,0,0,3],
#         [4,0,0,8,0,3,0,0,1],
#         [7,0,0,0,2,0,0,0,6],
#         [0,6,0,0,0,0,2,8,0],
#         [0,0,0,0,1,9,0,0,5],
#         [0,0,0,0,0,0,0,0,0]]

board = []
_solution = None


def generate_solution() -> List[List[int]]:
    global _solution
    # pattern for a baseline valid solution
    def pattern(r, c):
        return (base * (r % base) + r // base + c) % side

    def shuffle(s):
        return random.sample(s, len(s))

    rBase = range(base)
    rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, base * base + 1))

    # produce board using randomized baseline pattern
    _solution = [[nums[pattern(r, c)] for c in cols] for r in rows]
    return _solution


def generate_board(grid: Optional[list] = None) -> list:
    global _EMPTY
    if grid is None:
        _grid = generate_solution()
    else:
        _grid = []
        for row in grid:
            _grid.append([n for n in row])
    squares = side * side
    empties = squares * 3 // 4
    for p in random.sample(range(squares), empties):
        _grid[p // side][p % side] = 0

    numSize = len(str(side))
    s_board = []
    for line in _grid:
        new_ln = [n or _EMPTY for n in line]
        s_board.append(new_ln)
        # print("["+"  ".join(f"{n or '.':{numSize}}" for n in line)+"]")
    return s_board


def shortSudokuSolve(board: List[List[int]]):
    size = len(board)
    block = int(size**0.5)
    board = [n for row in board for n in row]
    span = {
        (n, p): {
            (g, n)
            for g in (n > 0)
            * [
                p // size,
                size + p % size,
                2 * size + p % size // block + p // size // block * block,
            ]
        }
        for p in range(size * size)
        for n in range(size + 1)
    }
    empties = [i for i, n in enumerate(board) if n == 0]
    used = set().union(*(span[n, p] for p, n in enumerate(board) if n))
    empty = 0
    while empty >= 0 and empty < len(empties):
        pos = empties[empty]
        used -= span[board[pos], pos]
        board[pos] = next((n for n in range(board[pos] + 1, size + 1) if not span[n, pos] & used), 0)
        used |= span[board[pos], pos]
        empty += 1 if board[pos] else -1
        if empty == len(empties):
            solution = [board[r : r + size] for r in range(0, size * size, size)]
            yield solution
            empty -= 1


def generate_single_solve_board() -> List[List[int]]:
    solution = generate_solution()
    s_board = generate_board(solution)
    while True:
        solved = [*islice(shortSudokuSolve(s_board), 2)]
        if len(solved) == 1:
            break
        diffPos = [(r, c) for r in range(9) for c in range(9) if solved[0][r][c] != solved[1][r][c]]
        r, c = random.choice(diffPos)
        s_board[r][c] = solution[r][c]
    return s_board


def get_current_solution() -> List[List[int]]:
    global _solution
    return _solution


def possible(row: int, column: int, number: int) -> bool:
    global board
    # Is the number appearing in the given row?
    for i in range(0, 9):
        if board[row][i] == number:
            return False

    # Is the number appearing in the given column?
    for i in range(0, 9):
        if board[i][column] == number:
            return False

    # Is the number appearing in the given square?
    x0 = (column // 3) * 3
    y0 = (row // 3) * 3
    for i in range(0, 3):
        for j in range(0, 3):
            if board[y0 + i][x0 + j] == number:
                return False

    return True


def solve():
    global board, _EMPTY
    for row in range(0, 9):
        for column in range(0, 9):
            if board[row][column] is _EMPTY:
                for number in range(1, 10):
                    if possible(row, column, number):
                        board[row][column] = number
                        solve()
                        board[row][column] = 0

                return

    pprint(board)
    input("More possible solutions")


if __name__ == "__main__":
    # board = generate_board()
    board = generate_single_solve_board()
    solve()
