import numpy
import numpy as np
from datetime import datetime


class SudokuState:
    def __init__(self, board):
        # Initialise class with input board.
        self.board = np.array(board)

    def sort_lsv(self, square):
        # This function applies the least-constraining values heuristic to order the domain values by the number of
        # choices for neighbouring variable values in the constraint graph.
        values = self.get_domain(*square)
        row, col = square
        choices_list = []
        grid_squares = []
        bottom, left, right, top = self.set_grid(row, col)

        for value in values:
            total_choices = 0
            self.board[square] = value
            for rows in range(top, bottom):
                for cols in range(left, right):
                    grid_squares.append((rows, cols))
            # Check grid values
            for squares in grid_squares:
                if self.board[squares] == 0:
                    total_choices += len(self.get_domain(*squares))
            # Check column
            for rows in range(9):
                if (rows, col) not in grid_squares:
                    if self.board[rows, col] == 0:
                        total_choices += len(self.get_domain(rows, col))
            # Check row
            for cols in range(9):
                if (row, cols) not in grid_squares:
                    if self.board[row, cols] == 0:
                        total_choices += len(self.get_domain(row, cols))
            self.board[square] = 0
            choices_list.append(total_choices)
        return [val for choices, val in sorted(zip(choices_list, values))]

    def empty_squares(self):
        # This function returns a list of all unassigned squares on the board
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
        # This function returns the arc consistent domain values of a variable in accordance with its binary
        # constraints. Set possible values to default domain
        values = {x for x in range(1, 10)}
        constrained = set()
        # Set and check grid
        bottom, left, right, top = self.set_grid(row, col)
        for rows in self.board[top:bottom, left:right]:
            for val in rows:
                constrained.add(val)
        # Check column
        for val in self.board[row, :]:
            constrained.add(val)
        # Check row
        for val in self.board[:, col]:
            constrained.add(val)
        return list(values - constrained)

    def is_valid_board(self):
        # Check if the current state of the board is valid according to the rules of Sudoku, if it is valid return
        # True if not return False.
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
        # Determine whether the current board state is terminal by checking if any variable is still assigned 0.
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    return False
        return True

    def propagate_constraints(self):
        # This function applies constraint propagation to assign variables inferred by the already assigned variables.
        complete = False
        # Loop until no single valued domains remain.
        while not complete:
            complete = True
            # Determine empty squares
            squares = self.empty_squares()
            # For each square, calculate its domain and if its singled values assign it.
            for square in squares:
                allowed_values = self.get_domain(*square)
                if len(allowed_values) == 1:
                    self.board[square] = allowed_values[0]
                    complete = False

    def get_mrv(self, squares):
        # Function for getting the most restricted variable (MRV) from a list of squares, used for selecting a
        # variable in line with the MRV heuristic.

        # Set MRV square, degree and domain size to the first square in the list.
        mrv_domain_size = len(self.get_domain(*squares[0]))
        mrv_degree = self.get_degree(squares[0])
        mrv = squares[0]
        # Loop through each square in the list
        for square in squares:
            # get the squares domain and determine its size
            square_domain = self.get_domain(*square)
            domain_size = len(square_domain)
            # If the domain size is zero return it straight away to trigger a failure as the state must be invalid.
            if domain_size == 0:
                return square
            # If domain size of square is smaller than the current MRV assign it as the new MRV.
            elif domain_size < mrv_domain_size:
                mrv_domain_size = len(self.get_domain(*square))
                mrv_degree = self.get_degree(square)
                mrv = square
            # Apply degree heuristic in the case of a tie in domain size.
            elif domain_size == mrv_domain_size:
                square_degree = self.get_degree(square)
                if square_degree > mrv_degree:
                    mrv_degree = square_degree
                    mrv = square
        return mrv

    def get_degree(self, square):
        # Returns the square from the input list involved in the largest number of constraints on other unassigned
        # variables
        row, col = square
        degree = 0

        # Define 3x3 grid to which the square belongs
        grid_squares = []
        bottom, left, right, top = self.set_grid(row, col)
        for rows in range(top, bottom):
            for cols in range(left, right):
                grid_squares.append((rows, cols))
        # Check grid values
        for square in grid_squares:
            if self.board[square] == 0:
                degree += 1
        # Check column
        for rows in range(9):
            if (rows, col) not in grid_squares:
                if self.board[rows, col] == 0:
                    degree += 1
        # Check row
        for cols in range(9):
            if (row, cols) not in grid_squares:
                if self.board[row, cols] == 0:
                    degree += 1
        return degree

    def backtrack(self):
        # Initially check for solved board as base case of recursive algorithm
        if self.check_solved():
            return True

        # Define empty squares and sort by increasing domain size, applying the minimum remaining values (MRV)
        # heuristic (get_mrv function uses degree heuristic for tie breaking).
        empty_squares = self.empty_squares()
        select_square = self.get_mrv(empty_squares)
        domain = self.get_domain(*select_square)
        # If any domain is empty the state isn't valid so return failure.
        if not domain:
            return False

        # For each value, apply it to the board and call constraint propagation algorithm
        for value in domain:
            self.board[select_square] = value
            saved_board = np.copy(self.board)  # Make a copy of the board in case of failure
            self.propagate_constraints()

            # Recursively call backtrack method.
            if self.backtrack():
                return True

            # If value is not a solution then reset variable and the constraint propagation values to zero.
            self.board = saved_board
            self.board[select_square] = 0
        return False

    def solve(self):
        # Solving algorithm:
        # Checks if the board is valid
        if not self.is_valid_board():
            return np.array([[-1] * 9] * 9)

        # Initially tries to solve with constraint propagation
        self.propagate_constraints()
        if self.check_solved():
            return self.board

        # If board is not solved call backtracking search algorithm
        elif self.backtrack():
            return self.board

        # If backtracking search returns failure, the board is unsolvable.
        else:
            return np.array([[-1] * 9] * 9)


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
    print("Full test duration {}".format(end_time - start_time))
