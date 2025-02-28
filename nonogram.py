import tkinter as tk
from main import Matrix
from tkinter import messagebox
import psutil
import os
import tracemalloc
import time
import resource 

GRID_SIZE = 5
CELL_SIZE = 40

PUZZLE = [
    [" ", " ", "X", "X", "X"],
    [" ", " ", "X", " ", "X"],
    ["X", "X", " ", " ", " "],
    ["X", "X", " ", " ", " "],
    ["X", "X", "X", "X", " "]
]

# PUZZLE = [
# [' ', ' ', ' ', 'X', ' ', ' ', ' ', ' ', 'X'],
#  [' ', ' ', ' ', 'X', ' ', ' ', ' ', 'X', ' '],
#  ['X', 'X', ' ', ' ', 'X', 'X', ' ', ' ', ' '],
#  ['X', 'X', 'X', ' ', ' ', 'X', 'X', ' ', 'X'],
#  [' ', 'X', ' ', 'X', ' ', 'X', 'X', ' ', 'X'],
#  ['X', ' ', 'X', 'X', 'X', 'X', ' ', ' ', ' '],
#  [' ', 'X', 'X', 'X', ' ', 'X', ' ', ' ', 'X'],
#  [' ', ' ', ' ', 'X', 'X', 'X', 'X', ' ', 'X'],
#  [' ', ' ', 'X', ' ', ' ', 'X', ' ', ' ', 'X']
#  ]


# PUZZLE = [
#     ["X", "X", "X", " ", " "],
#     ["X", "X", " ", " ", " "],
#     ["X", " ", "X", "X", " "],
#     ["X", " ", " ", " ", "X"],
#     ["X", "X", "X", "X", " "]
# ]

class NonogramGame:
    def __init__(self, root, puzzle,grid_size, cell_size):
        self.root = root
        self.root.title("Nonogram Game")
        self.puzzle = puzzle
        self.grid_size = grid_size
        self.cell_size = cell_size

        self.info_label = tk.Label(root, text="Thời gian: 0.0s | Bộ nhớ: 0.0MB", font=("Arial", 12))
        self.info_label.pack(pady=5)
        
        self.row_hints, self.col_hints = self.get_puzzle_hints()
        self.max_row_hints = len(max(self.row_hints, key=len))
        self.max_col_hints = len(max(self.col_hints, key=len))

        self.matrix = Matrix(self.row_hints, self.col_hints )
        
        grid_width = (self.grid_size + self.max_row_hints) * self.cell_size
        grid_height = (self.grid_size + self.max_col_hints) * self.cell_size
        
        self.canvas = tk.Canvas(root, width=grid_width, height=grid_height, bg="white")
        self.canvas.pack(pady=10)
        
        self.draw_hints()
        self.board = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.cell_clicked)
        
        self.check_button = tk.Button(root, text="Kiểm tra", command=self.check_solution, font=("Arial", 12))
        self.check_button.pack(pady=5)
        
        self.solve_button = tk.Button(root, text="Giải", command=self.start_solving, font=("Arial", 12))
        self.solve_button.pack(pady=5)
        
        self.solve_step = 0
    
    def get_puzzle_hints(self):
        row_hints = [self.get_hint(row) for row in self.puzzle]
        col_hints = [self.get_hint([self.puzzle[row][col] for row in range(self.grid_size)]) for col in range(self.grid_size)]
        print(row_hints)
        print(col_hints)
        return row_hints, col_hints
    
    def get_hint(self, line):
        return [len(s) for s in "".join(line).split(" ") if s]
    
    def draw_hints(self):
        for i, hint in enumerate(self.row_hints):
            for k, num in enumerate(hint):
                x = (self.max_row_hints + len(hint) + k*15) + 30
                y = (i + self.max_col_hints) * self.cell_size + self.cell_size // 2
                self.canvas.create_text(x, y, text=str(num), font=("Arial", 12), anchor="e")
        
        for j, hint in enumerate(self.col_hints):
            for k, num in enumerate(hint):
                x = (j + self.max_row_hints) * self.cell_size + (self.cell_size//2)
                y = (self.max_col_hints - len(hint) + k *20)  + 50
                self.canvas.create_text(x, y, text=str(num), font=("Arial", 12), anchor="s")
    
    def draw_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x0 = (j + self.max_row_hints) * self.cell_size
                y0 = (i + self.max_col_hints) * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                self.board[i][j] = self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="black")
        
    def cell_clicked(self, event):
        col = (event.x // self.cell_size) - self.max_row_hints
        row = (event.y // self.cell_size) - self.max_col_hints
        
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            current_color = self.canvas.itemcget(self.board[row][col], "fill")
            new_color = "black" if current_color == "white" else "white"
            self.canvas.itemconfig(self.board[row][col], fill=new_color)
        
    def check_solution(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                color = self.canvas.itemcget(self.board[i][j], "fill")
                if (self.puzzle[i][j] == "X" and color != "black") or (self.puzzle[i][j] == " "and color != "white"):
                    messagebox.showinfo("Kết quả", "Bạn chưa giải đúng!")
                    return
        messagebox.showinfo("Kết quả", "Chúc mừng! Bạn đã giải đúng!")
    
    def start_solving(self):
        self.solve_step = 0
        time_start = time.perf_counter()
        self.solve()
        time_elapsed = (time.perf_counter() - time_start)
        total_memory = psutil.Process().memory_info().rss / (1024**2)
        self.info_label.config(text="Thời gian: %.2fs | Bộ nhớ: %.2fMB" % (time_elapsed, total_memory))


    def solve(self, row=0, col=0):
        if row == len(self.matrix.rows):  
            return self.matrix.is_fully_valid()

        if self.matrix.is_valid(row, full_check=True):  
            return self.solve(row + 1, 0)
        
        next_row, next_col = (row, col + 1) if col + 1 < len(self.matrix.cols) else (row + 1, 0)

        for char in ['X', ' ']:  
            self.matrix.solve_matrix[row][col] = char
            self.update_board(row,col,fill = "black" if char == "X" else "white")
            if (self.matrix.is_valid(row) and self.matrix.is_valid(col, is_row=False)) :
                if (col == len(self.matrix.cols)-1 and not self.matrix.is_valid(row, full_check=True)):
                    continue
                if self.solve(next_row, next_col):
                    return True
                
        self.matrix.solve_matrix[row][col] = ' '
        self.update_board(row,col,fill = "white")
        return False
    
    def update_board(self, row, col, fill):
        # print(row, " ", col," ", fill)
        x0 = (col + self.max_row_hints) * self.cell_size
        y0 = (row + self.max_col_hints) * self.cell_size
        x1, y1 = x0 + self.cell_size, y0 + self.cell_size
        self.board[row][col] = self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="black")
        self.root.update()
        # time.sleep(0.2)


if __name__ == "__main__":
    root = tk.Tk()
    game = NonogramGame(root, PUZZLE, GRID_SIZE, CELL_SIZE)
    root.mainloop()
