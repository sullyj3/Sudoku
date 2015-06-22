#! /usr/bin/env python3

import timeit
import numpy as np
from collections import defaultdict
from math import floor
from itertools import chain
import cProfile

debug = print

def col_coords(j):
    for i in range(9):
        yield (i,j)

def row_coords(i):
    for j in range(9):
        yield (i,j)

def cell_subgrid(cell):
    i,j = cell
    return floor(i/3),floor(j/3)

def subgrid_coords(cell):
    I,J = cell_subgrid(cell)
    for n in range(3):
        for m in range(3):
            yield (I*3+n,J*3+m)

def print_line():
    print('-----+-----+-----')

def poslist():
    return {n:True for n in range(1,10)}

def possible(poslist):
    for n in poslist:
        if poslist[n]:
            yield n

def get_true(d):
    for k in d:
        if d[k]:
            return k
    raise ValueError("True not found")

# defaultdict requires a callable. Used for initialising Grid.pos_count
nine = lambda: 9

class Grid(np.ndarray):
    def __new__(cls):
        ret = super().__new__(cls, buffer=None,shape=(9,9),dtype=int,order=None)
        ret.fill(0)

        return ret

    def __init__(self):
        # each cell has an dict with key:val = (1..9):bool
        # each bool represents whether that cell can possibly be number key
        self.possibilities = defaultdict(poslist)
        self.pos_count = defaultdict(nine)

    def print_row(self, row):
        #make zeros spaces
        r = ( x if x else ' ' for x in self[row] )
        s = '{} {} {}|{} {} {}|{} {} {}'.format(*r)
        print(s)

    def cells(self):
        for i in range(9):
            for j in range(9):
                yield(i,j)

    def emptys(self):
        for c in self.cells():
            if not self[c]:
                yield c
        
    def show(self):
        for row in range(3):
            self.print_row(row)
        print_line()
        for row in range(3,6):
            self.print_row(row)
        print_line()
        for row in range(6,9):
            self.print_row(row)

    def row_contains(self, n, i):
        return n in self.row(i)

    def col_contains(self, n, j):
        return n in self.col(j)

    def subgrid_contains(self, n, cell):
        return n in self.subgrid(cell)

    def collision(self, n, cell):
        ''' for given cell, checks whether or not either the row, col, or
        subgrid the cell is in contain the number n'''
        i,j = cell
        if self.row_contains(n, i):
            return True
        if self.col_contains(n, j):
            return True
        if self.subgrid_contains(n, cell):
            return True
        return False

    def row(self, i):
        return self[i]

    def col(self, j):
        return self[:,j]

    def subgrid(self, cell):
        '''returns coords of 3*3 subgrid cell is in. (0..3,0..3)'''
        I,J = cell_subgrid(cell)
        return self[I*3:I*3+3,J*3:J*3+3]

    def filter_possible(self, cell):
        '''Function assumes cell is empty. Returns whether there's only one
        possibility left''' 
        # debug("filtering possibilities at  {},{}".format(*cell))

        # apply filter
        for n in possible(self.possibilities[cell]):
            if self.collision(n, cell):
                self.possibilities[cell][n] = False
                self.pos_count[cell] -= 1
                assert(self.pos_count[cell] > 0)
                if self.pos_count[cell] == 1:
                    return True

    def filter_each(self, coords):
        '''assumes coord_list is pre-filtered for emptiness. returns list of
        coords with one possibility left'''
        oneleft = []
        for coord in coords:
            if self.filter_possible(coord):
                oneleft.append(coord)
        return oneleft

    def filter_all(self):
        '''dumb and slow'''
        cells = ((i,j) for j in range(9) for i in range(9))
        empty_cells = (cell for cell in cells if not self[cell])
        for cell in empty_cells:
            self.filter_possible(cell)

    def filter_all2(self):
        cells = ((i,j) for j in range(9) for i in range(9))
        empty_cells = (cell for cell in cells if not self[cell])
        for cell in empty_cells:
            if self.filter_possible(cell):
                i,j = cell
                self.filter_each(row_coords(i))
                self.filter_each(col_coords(j))
                self.filter_each(subgrid_coords(cell))

    def check_n_group(self, group, n):
        '''checks whether a group (subgrid or row or column) has only one cell
        where n is still a possible candidate'''
        count = 0
        ret = None
        for cell in group:
            if self[cell] == n:
                raise ValueError('n is already present in group')

            # skip cells that are already filled in
            elif self[cell]:
                continue

            if self.possibilities[cell][n]:
                count += 1
                ret = cell
                # if there's more than one cell in group with n a possibility:
                # return None early
                if count > 1:
                    return

        # return the only cell in group with n as a possibility
        return ret

    def solved(self):
        # ndarray method is probably faster
        return self.all()

    def solved2(self):
        # linear time
        try:
            next(self.emptys())
        # if there aren't empty cells, grid is solved
        except StopIteration:
            return True
        return False

    ''' HOW SOLVING WORKS:
        For each cell in the grid, we keep a record of which numbers could
        possibly occupy that particular cell. We deduce this gradually by
        checking cells in the same row, col, and subgrid. Once there is only
        one possible value for a cell left, the cell is set to that value,
        and the possibility list of all related cells are updated
        accordingly.

        This method is still incomplete, as it ignores other possible rules
        of inference, and does not solve all solvable  grids.
        this is a TODO
    '''

    def naive_solve(self):
        '''seriously problematic, temporary measure. Very slow, won't solve
        every solvable puzzle, and can cause infinite loops. Use with caution.
        '''
        while not self.solved():
            self.filter_all()

    def naive_solve2(self):
        '''seriously problematic, temporary measure. Very slow, won't solve
        every solvable puzzle, and can cause infinite loops. Use with caution.
        '''
        while not self.solved():
            self.filter_all2()

    def solve_v1(self):
        '''WARNING INFINITE LOOPS'''
        while not self.solved():
            oneleft = self.filter_each(self.emptys())
            self.set_each(oneleft)

    def setval(self, cell, n):
        '''sets cell value to n, as well as updating possibility of n in all
        nearby cells. returns list of cells with only one possibility left
        for caller to deal with'''
        # set cell to n
        self[cell] = n
        i,j = cell
        
        # iterate through all empty related cells, setting possibility of n to
        # false in each. remember each coord with only one possibility left
        oneleft = []
        
        empty_in_row = (c for c in row_coords(i) if not self[c])
        empty_in_col = (c for c in col_coords(j) if not self[c])
        empty_in_subgrid = (c for c in subgrid_coords(cell) if not self[c])

        related = chain(empty_in_row, empty_in_col, empty_in_subgrid)

        for cell in related:
            if self.possibilities[cell][n]:
                self.possibilities[cell][n] = False
                self.pos_count[cell] -= 1
                assert(self.pos_count[cell] > 0)
                if self.pos_count[cell] == 1:
                    oneleft.append(cell)

        return oneleft

    def set_each(self, cell_list):
        # takes list of cells with only one possibility left, and sets them.
        # recursively sets each cell affected
        for cell in cell_list:
            # there should be only one True in self.possibilities[c]
            n = get_true(self.possibilities[cell])
            curr_list = self.setval(cell, n)
            self.set_each(curr_list)

    def dumps(self):
        fmt_s = "{}" * 9
        for row in self:
            print(fmt_s.format(*row))

def new_grid(l):
    '''takes a list of 9 strings, of 9 numbers each. Assumes they're well formed'''
    assert len(l) == 9
    g = Grid()
    for i,row in enumerate(l):
        for j,char in enumerate(row):
            g[i,j] = int(char)
    return g

def grid_from_file(f):
    lines = f.read().splitlines()
    if len(lines) != 9:
        raise ValueError('Need exactly 9 lines')
    g = new_grid(lines)
    return g

def test1():
    with open('grids/test1.txt') as f:
        t1 = grid_from_file(f)
    t1.show()
    t1.dumps()

def naive_solve(lines):
    g = new_grid(lines)
    g.naive_solve()
    return g

def naive_solve2(lines):
    g = new_grid(lines)
    g.naive_solve2()
    return g

def speedtest():
    with open('grids/test1.txt') as f:
        lines = f.read().splitlines()
    iters = 1000
    print("testing naivesolve {} times".format(iters))
    for i in range(iters):
        g = new_grid(lines)
        g.naive_solve()
    print("testing naivesolve2 {} times".format(iters))
    for i in range(iters):
        g = new_grid(lines)
        g.naive_solve2()

def loadt1():
    with open('grids/test1.txt') as f:
        global g
        g = grid_from_file(f)
    print ("read in grids/test1.txt as g")
    g.show()

def test_solve_v1():
    l = get_lines_from_file('grids/test1.txt')
    g = new_grid(l)
    g.show()
    print()
    print(len(g.emptys()))
    g.solve_v1()
    g.show()

def get_lines_from_file(path):
    with open(path) as f:
        lines = f.read().splitlines()
    return lines

def solvev1_speedtest():
    l = get_lines_from_file('grids/test1.txt')
    count = 10**2
    print("testing solve_v1 {} times".format(count))
    for i in range(count):
        g = new_grid(l)
        g.solve_v1()
    print("done")

if __name__ == '__main__':
    test_solve_v1()

# if __name__ == '__main__':
#     l = get_lines_from_file('grids/test1.txt')
#     cmd =   "for i in range(100):\n"\
#             "    g=new_grid(l)\n"\
#             "    g.solve_v1()"
# 
#     cProfile.run(cmd, 'solve_v1-profile.txt')
#     g.show()
