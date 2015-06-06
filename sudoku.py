import numpy as np
from collections import defaultdict
from math import floor

debug = print

# i,j
# 0,0 rows 0,3 | cols 0,3
# 0,1 rows 0,3 | cols 3,6
# 0,2 rows 0,3 | cols 6,9
# 1,0 rows 3,6 | cols 0,3 
# 1,1
# 1,2
# 2,0
# 2,1
# 2,2

class grid(np.ndarray):
    def __new__(cls):
        ret = super().__new__(cls, buffer=None,shape=(9,9),dtype=int,order=None)
        ret.fill(0)

        return ret

    def __init__(self):
        l = lambda: list(range(1,10))
        self.possibilities = defaultdict(l)

    def print_row(self, row):
        #make zeros spaces
        r = ( x if x else ' ' for x in self[row] )
        s = '{} {} {}|{} {} {}|{} {} {}'.format(*r)
        print(s)
        

    def print_line(self):
        print('-----+-----+-----')

    def print_grid(self):
        for row in range(3):
            self.print_row(row)
        self.print_line()
        for row in range(3,6):
            self.print_row(row)
        self.print_line()
        for row in range(6,9):
            self.print_row(row)

    def row(self, i):
        return self[i]

    def col(self, j):
        return self[:,j]

    def subgrid_slice(self, bigsquare):
        i,j = bigsquare
        return self[i*3:i*3+3,j*3:j*3+3]

    def get_subgrid(self, cell):
        i,j = cell
        return floor(i/3),floor(j/3)

    def filter_possible(self, cell):
        '''cell should be a 2 tuple i,j. Function assumes cell hasn't
        already been filled in. Returns whether or not it suceeded at 
        filling in the cell'''
        
        debug("filtering possibilities at  {},{}".format(*cell))

        subgrid = self.get_subgrid(cell)
        i,j = cell

        row_contains     = lambda x: x in self.row(i)
        col_contains     = lambda x: x in self.col(j)
        subgrid_contains = lambda x: x in self.subgrid_slice(subgrid)

        # possible = lambda x: not (row_contains(x) or col_contains(x) or subgrid_contains(x))
        # loop through current possible candidates for cell, removing
        # impossible ones.
        # TODO: current problem: when we remove a number, it fucks with the
        # for loop.
        # eg: for loop on 1 at index [0], 1 gets removed, 2 now at index [0]
        # iteration moves on to 3 at index [1], skipping 2
        msg = "self.possibilities[{}] = {}"
        debug(msg.format(cell,self.possibilities[cell]))
        for possibility in self.possibilities[cell]:
            debug("checking {}".format(possibility))
            if row_contains(possibility):
                msg = "can't be {}, it's elsewhere in row {}"
                debug(msg.format(possibility, i))
                self.possibilities[cell].remove(possibility)

            elif col_contains(possibility):
                msg = "can't be {}, it's elsewhere in col {}"
                debug(msg.format(possibility, j))
                self.possibilities[cell].remove(possibility)

            elif subgrid_contains(possibility):
                msg = "can't be {}, it's elsewhere in subgrid {},{}"
                debug(msg.format(possibility, *subgrid))
                self.possibilities[cell].remove(possibility)

        # If there's only one possibility left, fill in the cell
        if len(self.possibilities[cell]) == 1:
            msg = "only one possibility left: {}"
            debug(msg.format(self.possibilities[cell][0]))
            self[cell] = self.possibilities[cell][0]
            return True

        msg = "remaining possibilities for cell {} are: {}"
        debug(msg.format(cell, self.possibilities[cell]))
        return False

def create_test1():
    g = grid()
    g[0,6] = 5
    g[1,0] = 3
    g[1,2] = 2
    g[1,4] = 7
    g[1,6] = 9
    g[1,7] = 1
    g[2,0] = 6
    g[2,3] = 9
    g[3,7] = 2
    g[3,8] = 6
    g[4,1] = 2
    g[4,3] = 3
    g[4,6] = 1
    g[4,7] = 5
    g[4,8] = 9
    g[5,0] = 7
    g[5,1] = 9
    g[5,3] = 6
    g[5,5] = 5
    g[5,7] = 8
    g[6,0] = 1
    g[6,2] = 9
    g[6,3] = 7
    g[7,0] = 4
    g[7,1] = 5
    g[7,6] = 2
    g[7,7] = 3
    g[8,1] = 3
    g[8,2] = 8
    g[8,3] = 4
    g[8,4] = 5
    g[8,6] = 6
    return g

if __name__ == '__main__':
    t1 = create_test1()
    t1.print_grid()
    t1.filter_possible((4,0))
    t1.print_grid()


