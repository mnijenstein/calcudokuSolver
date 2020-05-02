#####################
# Calcudoku Group
#
# 2016-09-04
#
# M. Nijenstein
#####################

import cell
import operator
import weakref

# A Group (of cells) contains:
# 1: references to grid cells 
# 2: a mathematical operator that must be applied to those cells
# 3: the expected result of the operation
class CalcudokuGroup(object):
    def __init__(self, operator, result):
        self.result = result
        self.operator = operator
        self.cells = []
            
    def add_cells(self, *cells):
        for cell in cells:
            self.cells.append(cell)
            
    def group_info(self):
        # Print all information about the given group
        # Group may be entered as:
        
        str = "Result: %i" % self.result
        str += "\nOperator: %r" % self.operator
        str += "\nCells: "
        for cell in self.cells:
            str += "\n(%i,%i)" % cell.get_coordinate()

        return str

    def print_group(self):
        # Print all information about the given group
        # Group may be entered as:
        
        print("Result: %i" % self.result)
        print("Operator: %r" % self.operator)
        print("Cells: ")
        for cell in self.cells:
            print("(%i,%i)" % cell.get_coordinate())

