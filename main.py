import tkinter as tk
# from main import Matrix
from tkinter import messagebox
import psutil
import os
import tracemalloc
import time
import gc
import resource 

class Matrix:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.solve_matrix = [[' ' for _ in range(len(cols))] for _ in range(len(rows))]

    def print_matrix(self):
        print("   " + " ".join([",".join(map(str, r)) for r in self.cols])  )
        print("   "+ "+" + "--" * len(self.cols) + "+")

        for row_rule, row in zip(self.rows, self.solve_matrix):
            print(f"{','.join(map(str, row_rule))}".ljust(3) + "|" + " ".join(row) + " |" ) 
        print("   +" + "--" * len(self.cols) + "+")
        # time.sleep(0.2)

    def get_col(self, index):
        return "".join(self.solve_matrix[row][index] for row in range(len(self.rows)))
    
    def check_partial(self,index, rule, check_list ):
        if len(check_list) > len(rule): return False
        for i in range(len(rule)):
            if i > len(check_list)-1 or rule[i] == check_list[i]: return True
            if rule[i] < check_list[i]: return False
        return True

    def is_valid(self, index, is_row=True, full_check = False):
        rule = self.rows[index] if is_row else self.cols[index]
        data = "".join(self.solve_matrix[index]) if is_row else self.get_col(index)
        blocks = [len(b) for b in data.replace("-", " ").split(" ") if b]
        if full_check: return rule==blocks
        if rule==blocks: return True
        return self.check_partial(index, rule, blocks)

    def is_fully_valid(self):
        return all(self.is_valid(i, full_check = True) for i in range(len(self.rows))) and \
               all(self.is_valid(i, is_row=False, full_check = True) for i in range(len(self.cols)))

PUZZLE = [
    [" ", " ", "X", "X", "X"],
    [" ", " ", "X", " ", "X"],
    ["X", "X", " ", " ", " "],
    ["X", "X", " ", " ", " "],
    ["X", "X", "X", "X", " "]
]
class NonogramGame:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.grid_size = len(puzzle)
        self.row_hints, self.col_hints = self.get_puzzle_hints()
        self.matrix = Matrix(self.row_hints, self.col_hints)
        self.board = [[" " for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def get_puzzle_hints(self):
        row_hints = [self.get_hint(row) for row in self.puzzle]
        col_hints = [self.get_hint([self.puzzle[row][col] for row in range(self.grid_size)]) for col in range(self.grid_size)]
        return row_hints, col_hints

    def get_hint(self, line):
        return [len(s) for s in "".join(line).split(" ") if s]


    def check_solution(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (self.puzzle[i][j] == "X" and self.board[i][j] != "X") or \
                   (self.puzzle[i][j] == " " and self.board[i][j] != " "):
                    print("Bạn chưa giải đúng!")
                    return False
        print("Chúc mừng! Bạn đã giải đúng!")
        return True

    def start_solving(self):
        self.solve_step = 0
        time_start = time.perf_counter()
        self.solve()
        time_elapsed = (time.perf_counter() - time_start)
        total_memory = psutil.Process().memory_info().rss / (1024**2)
        # print((time_elapsed , total_memory))
        return (time_elapsed , total_memory)

    def solve(self, row=0, col=0):
        if row == self.grid_size:
            return self.matrix.is_fully_valid()
        if self.matrix.is_valid(row, full_check=True):
            return self.solve(row + 1, 0)
        
        next_row, next_col = (row, col + 1) if col + 1 < self.grid_size else (row + 1, 0)

        for char in ['X', ' ']:
            self.matrix.solve_matrix[row][col] = char
            self.board[row][col] = char
            # self.matrix.print_matrix()
            # time.sleep(0.1)
            if self.matrix.is_valid(row) and self.matrix.is_valid(col, is_row=False):
                if col == self.grid_size - 1 and not self.matrix.is_valid(row, full_check=True):
                    continue
                if self.solve(next_row, next_col):
                    return True
        
        self.matrix.solve_matrix[row][col] = ' '
        return False

if __name__ == "__main__":
    game = NonogramGame(PUZZLE)
    game.start_solving()
