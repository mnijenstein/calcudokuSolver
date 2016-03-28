#####################
# Calcudoku Solver
#
# 2014-12-30
#
# M. Nijenstein
#####################

from numpy import *
import operator
import weakref
import itertools
import logging as log

### options ###
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--input-file", dest="INPUT_FILE", 
                  help="solve INPUT_FILE", metavar="INPUT_FILE")
parser.add_option("-v", "--verbose", dest="VERBOSE",
                  help="print verbose output with level VERBOSE and higher\n QUIET, CRIT, ERR, WARN, INFO, DEBUG", metavar="VERBOSE")

(options, args) = parser.parse_args()

### verbose config ###
verbose = options.VERBOSE
if verbose == "CRIT":
    log_level = log.CRITICAL
elif verbose == "ERR":
    log_level = log.ERR
elif verbose == "WARN":
    log_level = log.WARN
elif verbose == "INFO":
    log_level = log.INFO
elif verbose == "DEBUG":
    log_level = log.DEBUG
else:
    log_level = log.NOTSET

if not (verbose == "QUIET"):
    log.basicConfig(format="%(levelname)s: %(message)s", level=log_level)
    log.info("Calcudoku Solver")
    log.info("-" * 20)
    
### input file ###
input_file = options.INPUT_FILE

class CalcudokuChecker(object):
    def __init__(self, size, arr=None):
        # Initialize variables
        self.size = size
        self.grid = zeros((size,size))
        self.groups = []
        if arr is not None:
            self.grid = arr

    def set_grid(self, grid):
        # Set grid to given grid
        self.grid = grid

    def print_grid(self):
        # Print the current grid
        print self.grid

    def add_group(self, group):
        # Add a Group with cells, operator and result
        self.groups.append(group);

    def get_value(self, x, y):
        # Return the value from grid cell (x, y)
        return self.grid(x, y)

    def check_solution(self, grid=None):
        # Prints if the grid is a valid solution.
        # If a grid is given, that grid is checked. Otherwise, the current grid will be checked.

        if self.grid_is_solution(grid):
            log.info("Solution is VALID")
        else:
            log.info("Solution is INVALID")

    def grid_is_solution(self, grid=None):
        # Returns whether the grid is a valid solution to the calcudoku.
        # If a grid is given, that grid is checked. Otherwise, the current grid will be checked.

        if grid is not None:
            self.grid = grid

        if 0 in self.grid:
            return False
            
        # Check groups. Stop if one fails.
        for i in range(len(self.groups)):
            if not self.evaluate_group(i):
                log.debug("Group %d fails" % i)
                log.debug(self.print_group(i))
                return False

        # Check rows and colums. Stop if one fails.
        return (self.check_rows() and self.check_columns())
            
    def check_rows(self):
        # Check if all rows in the grid have unique values

        # Construct reference series to check against
        validRow = arange(1, self.size+1)

        for i in range(self.size):
            # Sort row and check against reference
            row = array(self.grid[i,:])
            row.sort()
            result = row - validRow

            if not all(result == 0):
                # Stops as soon as a wrong row is found.
                log.debug("Row %d fails" % i)
                log.debug(array(self.grid[i,:]))
                return False
        return True

    def check_columns(self):
        # Check if all columns in the grid have unique values

        # Construct reference series to check against
        validColumn = arange(1, self.size+1).transpose()

        for i in range(self.size):
            # Sort column and check against reference
            column = array(self.grid[:,i])
            column.sort()
            result = column - validColumn
            if not all(result == 0):
                # Stops as soon as a wrong column is found.
                log.debug("Column %d fails" % i)
                log.debug(array(self.grid[:,i]))
                return False
        return True

    def print_group(self, i):
        # Print all information about the given group
        # Group may be entered as:
        # 1. struct of type Group
        # 2. index i of type int

        if type(i) is int:
            tempGroup = self.groups[i]
        elif type(Group):
            tempGroup = i
        else:
            log.debug("Not a group. Nothing to print")
            return False
        
        log.debug("Result: %i" % tempGroup.result)
        log.debug("Operator: %r" % tempGroup.operator)
        log.debug("Cells: ")
        for cell in tempGroup.cells:
            log.debug("(%i,%i)" % cell.get_coordinate())
            log.debug("Value: %i" % self.grid[cell.get_coordinate()])

    def evaluate_group(self, i):
        # Check if the group evaluates correctly with the given grid

        log.debug("Evaluating group %i" % i)

        group = self.groups[i]
            
        self.sort_on_value(group.cells)
        outcome = self.grid[group.cells[0].get_coordinate()]

        for cell in group.cells[1:]:
            outcome = self.groups[i].operator(outcome, self.grid[cell.get_coordinate()])

        log.debug("Outcome: %i" % outcome)
        return outcome == self.groups[i].result

    def sort_on_value(self, groupCells):
       # Sort values in a group from high to low
       # Required for correct handling of divisions and substractions

       for j in range(len(groupCells)):
            tempCell = None
            i = j
            while (i < ( len(groupCells)-1 ) and
                    self.grid[groupCells[i].get_coordinate()] < self.grid[groupCells[i+1].get_coordinate()]):
                tempCell = groupCells[i+1]
                groupCells[i+1] = groupCells[i]
                groupCells[i] = tempCell
                i += 1
 
# A Group (of cells) contains:
# 1: references to grid cells 
# 2: a mathematical operator that must be applied to those cells
# 3: the expected result of the operation
class Group(object):
    def __init__(self, result, operator, *cells):
        self.result = result
        self.operator = operator
        self.cells = []
        for cell in cells:
            self.cells.append(cell)

# A Cell defines a certain position in the grid
class Cell(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Return coordinate of this cell
    def get_coordinate(self):
        return (self.x, self.y)
        
    # Set value of this cell
    def set_value(self, value):
        self.value = value

    # Get value of this cell
    def get_value(self):
        return self.value

class CalcudokuSolver(object):
    def __init__(self, size=0):
        self.initialized = False
        if size > 0:
            self.size = size
            self.checker = CalcudokuChecker(self.size)
            self.grid = zeros((self.size,self.size))
            self.initialized = True
            log.info("Initialized")
        else:
            log.warn("Solver init: No real size => Not initialized")
            
        self.solution  = False
        
    def set_size(self, size):
        self.__init__(size)

    def solve(self):
        if not self.initialized:
            log.warn("Solve: Not yet initialized")
            return False
            
        log.info("Going to solve the calcudoku...")

        self.x = 0
        self.y = 0

		# Initialize grid with possible solution
        while (not self.y == self.size):
            
            # Only test values that unique in a row and column
            while ( self.grid[self.y, self.x] == 0
                or (not self.y == 0 and self.grid[self.y, self.x] in self.grid[:self.y,self.x])
                or (not self.x == 0 and self.grid[self.y, self.x] in self.grid[self.y, :self.x])):
                
                self.grid[self.y, self.x] = self.grid[self.y, self.x] + 1
                
            # Cell has valid value, so set marker at next cell
            self.x = self.x + 1
            
            # If at the end of a row, start at the start of the row below
            if self.x > self.size - 1:
                self.x = 0
                self.y = self.y + 1

            log.debug("Building grid: ")
            log.debug(self.grid)
        
        # Find solution by increasing cell values starting at the lower right corner
        self.x = self.size - 1
        self.y = self.size - 1
        while (not self.checker.grid_is_solution(self.grid)):
        	# Always increase cell once to keep progress
            self.force = True
            
            # Only test values that unique in a row and column
            while (self.force == True
                or (not self.y == 0 and self.grid[self.y, self.x] in self.grid[:self.y,self.x])
                or (not self.x == 0 and self.grid[self.y, self.x] in self.grid[self.y, :self.x])):
            
                self.grid[self.y, self.x] = self.grid[self.y, self.x] + 1
                self.force = False
                
            # If a cell exceeds the maximum value, set it to 0 and go one cell back
            if self.grid[self.y, self.x] == self.size + 1:
                self.grid[self.y, self.x] = 0
                self.x = self.x - 1
                # If at the beginning of a row, start at the end of row above
                if self.x < 0:
                    self.y = self.y - 1
                    self.x = self.size - 1
            # Cell has valid value, so set marker at next cell
            else:
                self.x = self.x + 1
                # If at the end of a row, start at the start of the row below
                if self.x > self.size - 1:
                    self.x = 0
                    self.y = self.y + 1
                # If at the end of the grid, set marker back to the last cell
                if self.y == self.size:
                    self.y = self.size - 1
                    self.x = self.y
                    
            log.debug("Trying grid: ")
            log.debug(self.grid)
                
        # If we come out of the while-loop, a solution is found
        self.solution = True
        
    def print_solution(self):
        # Print the graph that is stored as being the solution.
        if self.solution == True:
            log.info("Solution:")
            log.info("\n %s" % self.grid)
        else:
            log.info("No solution found yet")

    def add_group(self, Group):
        if not self.initialized:
            log.warn("Add group: Not yet initialized")
            return False
        # Pass on group to checker.
        self.checker.add_group(Group)

#### MAIN ####
solver = CalcudokuSolver(4)

# test set from Vk430
#grid = array([[2,4,1,3],[1,3,4,2],[4,2,3,1],[3,1,2,4]])
solver.add_group(Group(6, operator.add, Cell(0,0), Cell(1,0), Cell(1,1)))
solver.add_group(Group(10, operator.add, Cell(0,1), Cell(0,2), Cell(0,3), Cell(1,3)))
solver.add_group(Group(24, operator.mul, Cell(2,0), Cell(2,1), Cell(3,0)))
solver.add_group(Group(1, operator.sub, Cell(1,2), Cell(2,2)))
solver.add_group(Group(0, operator.sub, Cell(2,3), Cell(3,1), Cell(3,2), Cell(3,3)))

"""
#test set
#grid = array([[2,4,3,1],[4,1,2,3],[3,2,1,4],[1,3,4,2]])
solver.add_group(Group(32, operator.mul, Cell(0,0), Cell(0,1), Cell(1,0)))
solver.add_group(Group( 4, operator.add, Cell(2,0), Cell(3,0)))
solver.add_group(Group( 1, operator.div, Cell(1,1), Cell(1,2), Cell(2,1)))
solver.add_group(Group( 1, operator.div, Cell(0,2), Cell(0,3), Cell(1,3)))
solver.add_group(Group(12, operator.mul, Cell(2,2), Cell(3,1), Cell(3,2)))
solver.add_group(Group( 2, operator.div, Cell(2,3), Cell(3,3)))
"""
solver.solve()
solver.print_solution()
