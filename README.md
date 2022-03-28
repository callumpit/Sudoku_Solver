# Sudoku Solver
For my solution I have used a CSP Backtracking Search algorithm for solving sudoku puzzles. I decided to represent the state of the sudoku board as an object with all methods for minipulating the state and solving the board contained in its respective class. This includes methods for returning a list of the empty squares of the board, returning the domain of a specified square variable, checking if the current state of the board is legitimate, checking if the current state of the board is solved, checking for empty domains of board variables, applying heuristics and applying constraint propagation. The class is initialised by the input board which is saved as an instance variable which all minipulation methods are performed on.

My sudoku_solver function takes a board state as a 9x9 numpy array and creates an instance of my SudokuState class, and then calls the Sudokustate.solve method. This algorithm first checks the input board to see if it is a valid initial state, i.e. does the initial state of the board break any of the rules of Sudoku. If it isn't valid the requested numpy array of 9x9 -1s is returned. If the initial state is valid, the method attempts to solve the board intially by constraint propagation by calling the Sudoku.proagate_constraints method. This method works as follows:
* Loop untill no free squares have a single domain value:
*   get list of empty quares 
*     for each empty square:
*       check its domain according to all of its binary constraints, if it is single valued, set to this value.

