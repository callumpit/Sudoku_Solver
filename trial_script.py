import numpy
import numpy as np
from datetime import datetime

class SudokuState:
    def __init__(self, board):
        self.board = board

    def empty_squares(self):
        squares = []
        for row in range(9):
            for col in range(9):
                if self.board[row, col] == 0:
                    squares.append((row, col))
        return squares

    @staticmethod
    def set_grid(row, col):
        # This function defines the grid to which the input square belongs to.
        top = (row // 3) * 3
        bottom = top + 3
        left = (col // 3) * 3
        right = left + 3
        return bottom, left, right, top

    def get_domain(self, row, col):
        # This function returns a variables arc consistent domain values.
        # Set possible values to default domain
        values = {x for x in range(1, 10)}
        constrained = set()
        # Set and check grid
        bottom, left, right, top = self.set_grid(row, col)
        for rows in self.board[top:bottom, left:right]: # CHECK THIS ISSUE DOESN'T OCCUR ANYWHERE ELSE!!!!!!!!!!!
            for val in rows:
                constrained.add(val)
        for val in self.board[row, :]:
            constrained.add(val)
        for val in self.board[:, col]:
            constrained.add(val)
        return list(values - constrained)

    def is_legitimate(self):
        for row in range(9):
            for col in range(9):
                # Check binary constraints for every non-zero variable on the board
                val = self.board[row, col]
                if val == 0:
                    continue

                # Check grid constraints
                bottom, left, right, top = self.set_grid(row, col)
                count = 0
                for rows in self.board[top:bottom, left:right]:
                    for value in rows:
                        if value == val:
                            count += 1
                if count > 1:
                    return False

                # check column constrains
                count = 0
                for value in self.board[row, :]:
                    if value == val:
                        count += 1
                if count > 1:
                    return False

                # check row constraints
                count = 0
                for value in self.board[:, col]:
                    if value == val:
                        count += 1
                if count > 1:
                    return False
        return True

    def check_solved(self):
        # Determine whether the current board state is terminal.
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    return False
        return True


    def propagate_constraints(self):
        complete = False
        while not complete:
            complete = True
            squares = self.empty_squares()
            for square in squares:
                allowed_values = self.get_domain(square[0], square[1])
                if len(allowed_values) == 1:
                    self.board[square] = allowed_values[0]
                    complete = False

    def apply_mrv(self, squares):
        domain_size = []
        for square in squares:
            domain = self.get_domain(*square)
            domain_size.append(len(domain))

        # Sort cells by increasing domain length
        return [square for _, square in sorted(zip(domain_size, squares))]  # Ignores non pairs

    # def apply_mrv(self, squares):
    #     mrv_sorted = []
    #     current_domain_list = []
    #     current_domain_size = 0
    #
    #     # For each square get its domain and check if it is bigger than the last domain size.
    #     for square in squares:
    #         domain_size = len(self.get_domain(*square))
    #         if domain_size == 0:
    #             continue
    #         # If the domain size has increased, sort the list of squares of the previous domain size by degree and add
    #         # the resulting list to the final sorted list. Then reset the current domain list and add the new square.
    #         if domain_size > current_domain_size:
    #             current_domain_size = domain_size
    #             mrv_sorted += current_domain_list
    #             current_domain_list = []
    #         current_domain_list.append(square)
    #
    #     # return squares sorted by increasing domain length
    #     return mrv_sorted

    def check_domains(self):
        # Function used for forward checking. Check all the domains of empty squares, if any domain is empty,
        # return False, otherwise return True.
        for square in self.empty_squares():
            if not self.get_domain(*square):
                return False
        return True

    def backtrack(self):
        # Initially check for solved board as base case of recursive algorithm
        if self.check_solved():
            return True

        # Define empty squares and sort by increasing domain size, applying the minimum remaining values (MRV)
        # heuristic.
        empty_squares = self.empty_squares()
        sorted_squares = self.apply_mrv(empty_squares)

        # For each square in the list, define its domain and begin
        for square in sorted_squares:
            domain = self.get_domain(*square)
            for value in domain:
            # values = self.sort_lsv(square)
            # for value in values:
                self.board[square] = value
                # if sudoku.check_domains(cell):
                saved_board = np.copy(self.board)
                self.propagate_constraints()
                if not self.check_domains():
                    self.board = saved_board
                    self.board[square] = 0
                    continue
                if self.check_solved():
                    return True
                else:
                    self.board = saved_board

                # Recursively call backtrack algorithm again
                if self.backtrack():
                    return True

                # If value is not a solution then reset variable to zero
                self.board[square] = 0
            return False

    def solve(self):
        # Initialise sudoku and try to solve via constraint propagation
        # If this does not solve the sudoku, try the backtracking algorithm
        if not self.is_legitimate():
            return np.array([[-1.]*9]*9)
        self.propagate_constraints()
        if self.check_solved():
            return self.board
        elif self.backtrack():
            return self.board
        else:
            return np.array([[-1.]*9]*9)

def sudoku_solver(board):
    sudoku = SudokuState(board)
    return sudoku.solve()


def tests():
    import time
    difficulties = ['very_easy', 'easy', 'medium', 'hard']

    for difficulty in difficulties:
        print(f"Testing {difficulty} sudokus")

        sudokus = np.load(f"/Users/callumpitceathly/Downloads/sudoku-2/data/{difficulty}_puzzle.npy")
        solutions = np.load(f"/Users/callumpitceathly/Downloads/sudoku-2/data/{difficulty}_solution.npy")

        count = 0
        for i in range(len(sudokus)):
            sudoku = sudokus[i].copy()
            print(f"This is {difficulty} sudoku number", i)
            print(sudoku)

            start_time = time.process_time()
            your_solution = sudoku_solver(sudoku)
            end_time = time.process_time()

            print(f"This is your solution for {difficulty} sudoku number", i)
            print(your_solution)

            print("Is your solution correct?")
            if np.array_equal(your_solution, solutions[i]):
                print("Yes! Correct solution.")
                count += 1
            else:
                print("No, the correct solution is:")
                print(solutions[i])

            print("This sudoku took", end_time - start_time, "seconds to solve.\n")

        print(f"{count}/{len(sudokus)} {difficulty} sudokus correct")
        if count < len(sudokus):
            break

if __name__ == "__main__":
    start_time = datetime.now()
    tests()
    end_time = datetime.now()
    print("")
    print("Full test duration {}".format(end_time-start_time))