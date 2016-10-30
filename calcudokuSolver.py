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
import calcudokuDefinition as cd
import calcudokuChecker as cc
import operator
import weakref
import itertools
import logging as log
import string
import os
import time
import threading

### options ###
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--input-file", dest="INPUT_FILE", 
                  help="solve INPUT_FILE", metavar="INPUT_FILE")
parser.add_option("-t", "--threads", dest="NR_OF_THREADS", type="int", default=1,
                  help="number of threads to use (max=size)", metavar="NR_OF_THREADS")
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

### number of threads ###
nr_of_threads = options.NR_OF_THREADS

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

    def solve(self,nr_threads):
        # Create the number of requested threads and start each of them at equal distances between 1 and size

        # Nr of threads cannot be larger than size
        if nr_threads > self.size:
            nr_threads = self.size
        log.debug("Nr of threads: %i" % nr_threads)

        self.start_time = time.clock()

        threads = []
        for i in range(nr_threads):
            start_number = 1 + i*(self.size / nr_of_threads)
            log.info("Starting thread with start_number %i" % start_number)
            t = threading.Thread(target=self.solver_thread, args=(start_number,))
            threads.append(t)
            t.start()

        main_thread = threading.currentThread()

        for t in threading.enumerate():
            if t is main_thread:
                continue
            log.debug('Joining %s', t.getName())
            t.join()

        # If we come out of one of the threads, a solution is found
        self.stop_time = time.clock()
        self.solution = True

    def solver_thread(self,start_number=1):
        if not self.initialized:
            log.warn("Solve: Not yet initialized")
            return False
            
        log.info("Going to solve the calcudoku...")

        local_x = 0
        local_y = 0

        # Initialize grid with start_number
        log.info("Initializing grid...")
        local_grid = start_number*ones((self.size, self.size))
        log.info(local_grid)

        # Find solution by increasing cell values starting at the top left corner
        local_x = 0
        local_y = 0
        local_maxReached = False
        local_force = False
        local_nrOfTries = 0
        while (local_y != local_x or local_x != local_size - 1 or 
               not local_checker.grid_is_solution(local_grid)):

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

    def write_to_file(self, solution=None, output_file=None):
        if solution == None:
            log.info("Cannot print. No solution given.")
        else:
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)
            if output_file == None:
                log.debug("No filename given. Making one up myself.")
                output_file = input_file + time.strftime('%Y%m%d%H%M%S') + ".out"
            output_path = file(os.path.join(output_dir,os.path.basename(output_file)),'w')
            log.debug(output_path)
            
            #outFile = open(output_path,'w')
            format = 'd '*self.size
            savetxt(output_path,self.grid,fmt='%d')
            output_path.write("\n")
            output_path.write("Elapsed time: %.2f s\n" % (self.stop_time-self.start_time))
            output_path.write("Number of tries: %i\n" % self.nrOfTries)
            #outFile.write(self.grid)
            #outFile.close()

#### MAIN ####
calcudoku = cd.CalcudokuDefinition()
if not (input_file == ""):
    calcudoku.read_from_file(input_file)

print("Calcudoku succesfully read")
raw_input("Press key to continu...")

solution = ""
solution = cs.solve(calcudoku,1)
print solution
#print cs.get_elapsed_time() 
#write_to_file(solution)
