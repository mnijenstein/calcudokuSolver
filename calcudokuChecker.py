#####################
# Calcudoku Checker
#
# 2016-10-30
#
# M. Nijenstein
#####################

from numpy import *
import cell
import calcudokuGroup as cg
import calcudokuDefinition as cd
import operator
import weakref
import itertools
import logging as log

class CalcudokuChecker(object):
    def __init__(self):
        self.grid = None
        self.definition = None
        self.size = 0

    def validate(self, grid, definition):
        # Returns whether the grid is a valid solution to the calcudoku.

        log.debug("Checking grid...")

        if 0 in grid:
            return False

        self.grid = grid
        self.definition = definition
        self.size = self.definition.get_size()
            
        # Check groups. Stop if one fails.
        # Groups are probably added from top left to bottom right. 
        # The grid is changed most in the bottom right corner, 
        # so checking the groups in reverse should be a little more efficient.
        for i in range(len(self.definition.groups))[::-1]:
            if not self.evaluate_group(i):
                log.debug("Group %d fails" % i)
                log.debug(self.definition.groups[i].group_info())
                return False

        # Check rows and colums. Stop if one fails.
        return (self.check_rows() AND self.check_columns())
            
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
        validColumn = arange(1, size+1).transpose()

        for i in range(size):
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
        group = self.definition.groups[i]

        # Only sort for groups that require sorting (substraction and division)
        if (group.operator == operator.sub or
            group.operator == operator.div):
            self.sort_on_value(group.cells)

        outcome = grid[group.cells[0].get_coordinate()]
        for cell in group.cells[1:]:
            outcome = group.operator(outcome, self.grid[cell.get_coordinate()])

        log.debug("Outcome: %i" % outcome)
        return outcome == group.result

    def sort_on_value(self, groupCells):
       # Sort values in a group from high to low
       # Required for correct handling of divisions and substractions

       for j in range(len(groupCells)):
            tempCell = None
            i = j
            while (i < ( len(groupCells)-1 ) and
                    self.grid[groupCells[i].get_coordinate()] < grid[groupCells[i+1].get_coordinate()]):
                tempCell = groupCells[i+1]
                groupCells[i+1] = groupCells[i]
                groupCells[i] = tempCell
                i += 1

