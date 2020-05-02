#####################
# Calcudoku Definition
#
# 2016-10-30
#
# M. Nijenstein
#####################

import cell
import calcudokuGroup as cg
import operator
import logging as log
import string

class CalcudokuDefinition(object):
    def __init__(self):
        self.groups = []

    def set_size(self, size):
        self.size = size
        
    def get_size(self):
        return self.size

    def read_from_file(self, input_file=None):
        size_known = False
        operators = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "x": operator.mul,
            "/": operator.truediv,
            ":": operator.truediv,
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

                            if line[:4].lower() == "size":
                                line = line[5:].split("#")
                                self.set_size(int(line[0]))
                                size_known = True
                                log.info("Found size: %i" % self.size)
                        else:
                            line = line.split()
                            if line[0] in operators:
                                group = cg.CalcudokuGroup(operators.get(line[0]),int(line[1]))
                                for coord in line[2:]:
                                    coords = coord.split(",")
                                    group.add_cells(cell.Cell(int(coords[0])-1,int(coords[1])-1))
                                log.debug("Added group: ")
                                log.debug(group.group_info())
                                self.groups.append(group)

                            else:
                                log.warn("No operator found as first element in row")
                        
        return

