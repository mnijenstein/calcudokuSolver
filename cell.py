#####################
# Cell
#
# 2016-09-04
#
# M. Nijenstein
#####################

# A Cell defines a certain position in a 2d grid
class Cell(object):
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def set_coordinate(self, x, y):
        self.x = x
        self.y = y

    # Return coordinate of this cell
    def get_coordinate(self):
        return (self.x, self.y)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    # Set value of this cell
    def set_value(self, value):
        self.value = value

    # Get value of this cell
    def get_value(self):
        return self.value
