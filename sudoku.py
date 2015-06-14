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

class Grid(np.ndarray):
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

        def possible(x):
            return not (row_contains(x) or
                        col_contains(x) or
                        subgrid_contains(x))

        p = (pos for pos in self.possibilities[cell] if possible(pos))
        self.possibilities[cell] = list(p)

        # If there's only one possibility left, fill in the cell
        if len(self.possibilities[cell]) == 1:
            msg = "only one possibility left: {}"
            debug(msg.format(self.possibilities[cell][0]))
            self[cell] = self.possibilities[cell][0]
            return True

        msg = "remaining possibilities for cell {} are: {}"
        debug(msg.format(cell, self.possibilities[cell]))
        return False

    def filter_all(self):
        '''dumb and slow'''
        cells = ((i,j) for j in range(9) for i in range(9))
        empty_cells = (cell for cell in cells if not self[cell])
        for cell in empty_cells:
            self.filter_possible(cell)

    def solved(self):
        cells = ((i,j) for j in range(9) for i in range(9))
        for cell in cells:
            if not self[cell]:
                return False
        return True

    def naive_solve(self):
        '''seriously problematic, temporary measure. Slow, and potential for
        infinite loops. Use with caution.'''
        while not self.solved():
            self.filter_all()

    def dumps(self):
        fmt_s = "{}" * 9
        for row in self:
            print(fmt_s.format(*row))

def new_grid(l):
    '''takes a list of 9 strings, of 9 numbers. Assumes they're well formed'''
    assert len(l) == 9
    g = Grid()
    for i,row in enumerate(l):
        for j,char in enumerate(row):
            g[i,j] = int(char)
    return g

def grid_from_file(f):
    lines = f.read().splitlines()
    g = new_grid(lines)
    return g

def test1():
    with open('grids/test1.txt') as f:
        t1 = grid_from_file(f)
    t1.print_grid()
    t1.dumps()

if __name__ == '__main__':
    test1()
