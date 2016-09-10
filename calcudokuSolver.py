#####################
# Calcudoku Solver
#
# 2014-12-30
#
# M. Nijenstein
#####################

from numpy import *
import cell
import calcudokuGroup as cg
import operator
import weakref
import itertools
import logging as log
import string
import os
import time

### options ###
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--input-file", dest="INPUT_FILE", 
                  help="solve INPUT_FILE", metavar="INPUT_FILE")
parser.add_option("-v", "--verbose", dest="VERBOSE",
                  help="print verbose output with level VERBOSE and higher\n QUIET, ERR, INFO, DEBUG", metavar="VERBOSE")

(options, args) = parser.parse_args()

### verbose config ###
verbose = options.VERBOSE
if verbose == "ERR":
    log_level = log.ERR
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

### output_dir ###
output_dir = os.path.join(os.getcwd(),"output")

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
                log.debug(self.groups[i].group_info())
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

    def evaluate_group(self, i):
        # Check if the group evaluates correctly with the given grid

        log.debug("Evaluating group %i" % i)
        group = self.groups[i]

        # Only sort for groups that require sorting (substraction and division)
        if (group.operator == operator.sub or
            group.operator == operator.div):
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

class CalcudokuSolver(object):
    def __init__(self, size=0):
        self.initialized = False
        if size > 0:
            self.size = size
            self.checker = CalcudokuChecker(self.size)
            self.grid = zeros((self.size,self.size))
            self.initialized = True
            self.start_time = 0
            self.stop_time = 0
            log.info("Initialized")
        else:
            log.warn("Solver init: No real size => Not initialized")
            
        self.solution  = False
        
    def set_size(self, size):
        self.__init__(size)
        
    def read_calcudoku(self, input_file=None):
        size_known = False
        operators = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "x": operator.mul,
            "/": operator.div,
            ":": operator.div,
            "%": operator.mod
        }
        
        if (input_file == None):
            log.warn("Read calcudoku: No file given")
        else:
            with open(input_file,'r') as file:
                log.debug("Read calcudoku: Opening file '%s'" % input_file)
                for line in file:
                    log.debug("Read line: %s" % line.strip())
                    if (line[0] == "#"): #commented line
                        log.debug("Commented line")
                    else:
                        if not size_known: #search for size first
                            log.debug("Searching for size...")
                            line = string.join(line.split(),"")
                            if line[:4].lower() == "size":
                                line = line[5:].split("#")
                                self.set_size(string.atoi(line[0]))
                                size_known = True
                                log.info("Found size: %i" % self.size)
                        else:
                            line = line.split()
                            if line[0] in operators:
                                group = cg.CalcudokuGroup(operators.get(line[0]),string.atoi(line[1]))
                                for coord in line[2:]:
                                    coords = coord.split(",")
                                    group.add_cells(cell.Cell(string.atoi(coords[0])-1,string.atoi(coords[1])-1))
                                log.debug("Added group: ")
                                log.debug(group.group_info())
                                self.add_group(group)

                            else:
                                log.warn("No operator found as first element in row")
                        
        return

    def solve(self):
        if not self.initialized:
            log.warn("Solve: Not yet initialized")
            return False
            
        log.info("Going to solve the calcudoku...")

        self.x = 0
        self.y = 0

        # Initialize grid with ones
        log.info("Initializing grid...")
        self.grid = ones((self.size, self.size))
        log.info(self.grid)

        self.start_time = time.clock()

        # Find solution by increasing cell values starting at the top left corner
        self.x = 0
        self.y = 0
        self.maxReached = False
        self.force = False
        while (self.y != self.x or self.x != self.size - 1 or 
               not self.checker.grid_is_solution(self.grid)):

            while ((not self.currentCellUnique() and not self.maxReached)
                or self.force):
                self.force = False
                if not self.increaseCurrentCell():
                    self.maxReached = True

            if self.maxReached:
                self.maxReached = False
                self.grid[self.y, self.x] = 1
                self.goToPreviousCell()
                self.force = True
            else:
	        if not self.goToNextCell():
                    self.force = True

            log.debug("Trying grid: ")
            log.debug(self.grid)
                
        # If we come out of the while-loop, a solution is found
        self.stop_time = time.clock()
        self.solution = True

    def goToNextCell(self):
        if self.x == self.size - 1:
            if self.y == self.size - 1:
                log.debug("Cannot go to next cell. Already at the end")
                return False
            else:
                self.y += 1
                self.x = 0
        else:
            self.x += 1

        return True

    def goToPreviousCell(self):
        if self.x == 0:
            if self.y == 0:
                log.debug("Cannot go to previous cell. Already at the start")
                return False
            else:
                self.y -= 1
                self.x = self.size - 1
        else:
            self.x -= 1

        return True

    def increaseCurrentCell(self):
        if self.grid[self.y, self.x] == self.size:
            return False
        else:
            self.grid[self.y, self.x] += 1
        
        return True

    def currentCellUnique(self):
        return ((self.y == 0 or not self.grid[self.y, self.x] in self.grid[:self.y, self.x])
            and (self.x == 0 or not self.grid[self.y, self.x] in self.grid[self.y, :self.x]))

    def print_elapsed_time(self):
        # Print the time it took to solve the puzzle
        if self.solution == True:
            log.info("Elapsed time: %.2f s" % (self.stop_time-self.start_time))

    def print_solution(self):
        # Print the graph that is stored as being the solution.
        if self.solution == True:
            log.info("Solution:")
            log.info("\n %s" % self.grid)
        else:
            log.info("No solution found yet")

    def write_solution_to_file(self, output_file=None):
        if self.solution == False:
            log.info("Cannot print solution: No solution found yet.")
        else:
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)
            if output_file == None:
                log.debug("No filename given. Making one up myself.")
                output_file = datetime.now().strftime(YYYYmmddHHmmss)
                output_file = os.path.join(output_file,".out")
            output_path = os.path.join(output_dir,os.path.basename(output_file))
            log.debug(output_path)
            
            #outFile = open(output_path,'w')
            #log.debug(outFile)
            #log.debug(self.grid)
            format = 'd '*self.size
            savetxt(output_path,self.grid,fmt='%d')
            #outFile.write(self.grid)
            #outFile.close()

    def add_group(self, group):
        if not self.initialized:
            log.debug("Add group: Not yet initialized")
            return False
        # Pass on group to checker.
        self.checker.add_group(group)

#### MAIN ####
solver = CalcudokuSolver()
if not (input_file == ""):
    solver.read_calcudoku(input_file)

print("Calcudoku succesfully read")
raw_input("Press key to continu...")

solver.solve()
solver.print_solution()
solver.print_elapsed_time()
solver.write_solution_to_file(input_file)
