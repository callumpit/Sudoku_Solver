# Sudoku Solver
## Description of Algorithm
For my solution I have used a CSP Backtracking Search algorithm for solving sudoku puzzles. I decided to represent the state of the sudoku board as an object with all methods for minipulating the state and solving the board contained in its respective class. This includes methods for returning a list of the empty squares of the board, returning the domain of a specified square variable (reduced by its binary constraints), checking if the current state of the board is legitimate, checking if the current state of the board is solved, checking for empty domains of board variables, applying heuristics and applying constraint propagation. The class is initialised by the input board which is saved as an instance variable which all minipulation methods are performed on.

My sudoku_solver function takes a board state as a 9x9 numpy array and creates an instance of my SudokuState class, and then calls the Sudokustate.solve method. This algorithm first checks the input board to see if it is a valid initial state, i.e. does the initial state of the board break any of the rules of Sudoku. If it isn't valid the requested numpy array of 9x9 -1s is returned. If the initial state is valid, the method attempts to solve the board intially by constraint propagation by calling the SudokuState.proagate_constraints method. This method loops through all unassigned squares checking each ones
domain, restricted by its binary constraints. If its domain is single valued, the square is assigned to it. The loop is repeated untill there are no more squares with single valued domains.

The board is then checked if it is solved and returned if it is. If the board remains unsolved, the recursive SudokuState.backtrack method is called. The base case of this method checks if the board is solved and returns True if it is. If not the algorithm enters its main body. The method first gets a list of the empty squares on the board and sorts them in order of increasing domain length, applying the minimum remianing values heuristic. This means that any
variables whose domain is empty will be checked first and trigger a failure which prunes the search tree. Hence the empty squares are looped through. For
each square its domain is first determined according to its binary constraints. If the domain is empty, the function returns False triggering a failure.
Otherwise each value in its domain is looped through. For each value in the domain, the value of the current square is set to that value, and a copy of the
current state of the board is made case of failure further down the tree. 

The algorithm then calls the constraint propagation method to enforce all values implicit by the assignment of the current square to its current value. Subsequently, the algorithm calls the SudokuState.check_domains method which enacts forward checking on the domains of all unassigned variables. If any of them are empty, the assigned value of the current square cannot be correct and hence the check_domains method returns False and the board is reset (using
the copied board), the squares value set back to zero and the value loop tries the next value in the domain. This further prunes the search tree by detecting future failures early. If the forward checking process returns true and all resulting domains are non-zero, the algorithm then recursively calls
the backtrack method. If this call results in failure, the board is reset and the current squares value is reset to zero. If the algorithm tries all values in the domain of the square it returns False as the current state of the board is
unsolvable.

If the initial call of the backtracking algorithm results in failure it means that there is no possible solution for the board as every possible value of the first square cheked has resulted in failure, meaning that that square has no valid value. In this case the solve method returns the requested numpy array of 9x9 -1s.


