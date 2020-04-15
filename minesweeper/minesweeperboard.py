#    Minesweeper
#    Copyright (C) 2020  Deidre House
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see https://www.gnu.org/licenses/.

import random
from builtins import input # Python 2 & 3 cross-compatibility
from msvcrt import getch
import pickle
import os

_savefile_extension = ".minesweeper"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_board(w,h,m):
    """Generate a minesweeper board of size (w,h) with m (random) mines"""
    board = fill_board(w,h)
    locations = random.sample(range(w*h),m)
    for location in locations:
        board[location // w][location % w] = True
    return board

def fill_board(w,h,x=False):
    """Initialize a blank board"""
    return [[x for _ in range(w)] for _ in range(h)]


class MinesweeperBoard(object):
    
    def __init__(self, board):
        """board is an array indicating locations of mines"""
        self.rows = len(board)
        self.cols = len(board[0])
        if [len(r) for r in board] != [self.cols]*self.rows:
            raise ValueError("Non-rectangular array")
        self.mines = [[bool(c) for c in r] for r in board]
        self.mine_count = sum([sum(r) for r in self.mines])
        self.target = self.rows*self.cols - self.mine_count
        self.neighbors = []
        for r in range(self.rows):
            l = []
            for c in range(self.cols):
                l.append(sum([self.mines[R][C] for R,C in self.adjacent(r,c)]))
            self.neighbors.append(l)
        #[[sum([self.mines[R][C] for R,C in self.adjacent(r,c)]) for c in range(self.cols)] for r in range(self.rows)]
        self.reset()
    
    def reset(self):
        self.cursor = [0,0]
        self.revealed = fill_board(self.cols,self.rows)
        self.visible = 0
        self.flagged = fill_board(self.cols,self.rows)
        self.flag_count = 0
        self.won = self.boom = False        
    
    def __repr__(self):
        return "{}({})".format(type(self).__name__,self.mines)
    
    def adjacent(self, row, col):
        """Fetch all valid cell addresses adjacent to the cell (row, col)."""
        ans = []
        for v,h in self.directions(row, col):
            R, C = row + v, col + h
            if 0<= R < self.rows and 0<= C < self.cols:
                ans.append([R,C])
        return ans
    
    def reveal(self, row, col):
        """Reveal the cell at (row, col).
           If cell has no neighboring mines, reveal more."""
        self.visible += not self.revealed[row][col]
        self.revealed[row][col] = True
        if self.neighbors[row][col] == 0:
            frontier = [[row,col]]
            while frontier:
                tmp = []
                for r,c in frontier:
                    for R,C in self.adjacent(r,c):
                        if not (self.revealed[R][C] or self.flagged[R][C]):
                            self.revealed[R][C] = True
                            self.visible += 1
                            if self.neighbors[R][C] == 0:
                                tmp.append([R,C])
                frontier = tmp
    
    def select(self, row, col):
        """Select a cell to click on."""
        if self.flagged[row][col]:
            return
        if self.mines[row][col]:
            self.detonate()
        else:
            if not self.revealed[row][col]:
                self.reveal(row, col)
            else:
                m = 0
                unclicked = []
                for R,C in self.adjacent(row,col):
                    m += self.flagged[R][C]
                    if not (self.revealed[R][C] or self.flagged[R][C]):
                        unclicked.append([R,C])
                if m == self.neighbors[row][col]:
                    for R,C in unclicked:
                        if self.mines[R][C]:
                            self.detonate()
                            break
                        self.reveal(R, C)
            if self.visible == self.target:
                self.win()
    
    def toggle_flag(self, row, col):
        self.flag_count += (-1)**self.flagged[row][col]
        self.flagged[row][col] = not self.flagged[row][col]
    
    def mark(self, row, col):
        """Select a cell to flag."""
        if not self.revealed[row][col]:
            self.toggle_flag(row, col)
        else:
            m = u = 0
            unclicked = []
            for R,C in self.adjacent(row, col):
                m += self.flagged[R][C]
                if not (self.revealed[R][C] or self.flagged[R][C]):
                    unclicked.append([R,C])
                    u += 1
            if m + u == self.neighbors[row][col]:
                for R,C in unclicked:
                    self.toggle_flag(R,C)
    
    def symbol(self, row, col):
        """Fetches the symbol that should be printed in cell (row, col)."""
        n = self.neighbors[row][col]
        s = hex(n)[-1] if n else ' '
        return ('*' if self.mines[row][col] else s) if self.revealed[row][col] else 'X' if self.flagged[row][col] else '?'
    
    def win(self):
        self.won = True
        self.revealed = fill_board(self.cols,self.rows,True)
        self.flag_count = self.mine_count
    
    def detonate(self):
        self.boom = True
        self.revealed = fill_board(self.cols,self.rows,True)
    
    helpmessage = """Controls:
arrow keys - move cursor
enter - click cell
space - flag/unflag cell
h - display/hide help
q - quit game
s - save game"""
    
    def play(self):
        show_help = False
        clear()
        print("Mines remaining: {}".format(self.mine_count - self.flag_count))
        print(self)
        
        while not (self.won or self.boom):
            print("Current location: ({0},{1})   ".format(self.cursor[0]+1,self.cursor[1]+1))
            if show_help:
                print(self.helpmessage)
            k = ord(getch())
            # arrow key:
            if k == 224:
                d = ord(getch())
                # up arrow:
                if d == 72:
                    self.cursor[0] = max(0, self.cursor[0] - 1)
                elif d == 75:
                    self.cursor[1] = max(0, self.cursor[1] - 1)
                elif d == 77:
                    self.cursor[1] = min(self.cols - 1,
                                         self.cursor[1] + 1)
                elif d == 80:
                    self.cursor[0] = min(self.rows - 1 ,
                                         self.cursor[0] + 1)
            elif k == 32:
                self.mark(*self.cursor)
            elif k == 13:
                self.select(*self.cursor)
            elif k in [81, 113]:
                print("Sure you want to quit? (y/n)")
                k2 = ord(getch())
                if k2 in [89, 121]:
                    self.detonate()
                elif k2 in [0, 244]:
                    getch()
            elif k in [72, 104]:
                #help message
                show_help = not show_help
            elif k in [83, 115]:
                # save game
                savename = input("Save game as:")
                with open(savename + _savefile_extension, 'wb') as f:
                    pickle.dump(self, f, protocol=2)                
            elif k == 0:
                getch()
            clear()
            print("Mines remaining: {}".format(self.mine_count - self.flag_count))
            print(self)
        
        if self.won:
            print("You win!")
        elif self.boom:
            print("BOOM! game over.")

class SquareBoard(MinesweeperBoard):
    
    displayname = "Classic"
    
    defaults = [10,10,20]
    
    def directions(self, r, c):
        return [[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]]
    
    def __str__(self):
        lpad = len(hex(self.rows)) - 2
        lines = [' '*(lpad+1) + ''.join(['{:^2}'.format(hex(c)[2:] if c-1 != self.cursor[1] else '*') for c in range(1,self.cols+1)])]
        lines.append(' '*lpad + '_'+'_'*2*self.cols)
        for row in range(self.rows):
            sides = '*' if row == self.cursor[0] else hex(row+1)[2:]
            line = [self.symbol(row,col) for col in range(self.cols)]
            line.append(sides)
            lines.append('{n:>{pad}}|'.format(n=sides,pad=lpad) + '|'.join(line))
        lines.append(' '*lpad + '‾'+'‾'*2*self.cols)
        lines.append(lines[0])
        return "\n".join(lines)

class TriangularBoard(MinesweeperBoard):

    displayname = "Triangular"
    
    defaults = [15,8,20]
    
    def directions(self, r, c):
        dirs =[[1,0],[1,1],[0,1],[0,2],[-1,1],[-1,0],[-1,-1],[0,-2],[0,-1],[1,-1]]
        return dirs + ([[1,-2],[1,2]] if (r+c) % 2 else [[-1,2],[-1,-2]])

    def __str__(self):
        lines = ['  ' + ''.join(['{:^3}'.format(c if c-1 != self.cursor[1] else '*') for c in range(1,self.cols+1)])]
        lines.append(' '+'_'*(3*self.cols + 2*(self.cols % 2)))
        for row in range(self.rows):
            sides = '*' if row == self.cursor[0] else str(row+1)
            if row % 2:
                line1 = ['{:>2}/'.format(sides)]
                line2 = [' /']
                for col in range(self.cols):
                    if col % 2:
                        line1.append(format(self.symbol(row,col), "^3") + '/')
                        line2.append('_/')
                    else:
                        line1.append(self.symbol(row,col) +  '\\')
                        line2.append('___\\')
                line1 += sides
            else:
                line1 = [' \\']
                line2 = ['{:>2}\\'.format(sides)]
                for col in range(self.cols):
                    if col % 2:
                        line1.append(self.symbol(row,col) +  '\\')
                        line2.append('___\\')
                    else:
                        line1.append(format(self.symbol(row,col),"^3")+'/')
                        line2.append('_/')
                line2 += sides
            lines.append(''.join(line1))
            lines.append(''.join(line2))
        lines.append(lines[0])
        return "\n".join(lines)


class HexagonalBoard(MinesweeperBoard):

    displayname = "Hexagonal"
    
    defaults = [15,8,20]
    
    def directions(self, r, c):
        dirs = [[1,0],[0,1],[-1,0],[0,-1]]
        return  dirs + ([[1,1],[1,-1]] if c % 2 else [[-1,-1],[-1,1]])

    def __str__(self):
        lines = ['   ' + ''.join(['{:<2}'.format(c if c-1 != self.cursor[1] else '*') for c in range(1,self.cols+1)])]
        lines.append('   ' +'_   '*((self.cols+1)//2))
        for row in range(self.rows):
            line1 = ['  ']
            sides = '*' if row == self.cursor[0] else str(row+1)
            line2 = ['{:2}\\'.format(sides)]
            for col in range(self.cols):
                if col % 2:
                    line1.append("_")
                    line2.append(self.symbol(row,col)+'\\')
                else:
                    line1.append('/' + self.symbol(row,col) + '\\')
                    line2.append("_/")
            if row and not (self.cols % 2):
                line1.append("/")
            lines.append(''.join(line1))
            lines.append(''.join(line2) + sides)
        lines.append('    ' + '\\_/ '*(self.cols//2))
        lines.append(lines[0])        
        return "\n".join(lines)

class TruncatedSquareBoard(MinesweeperBoard):
    
    displayname = "Truncated Square"
    
    defaults = [15,8,20]
        
    def directions(self, r, c):
        ds = [[1,0],[-1,0],[0,1],[0,-1]]
        if (r+c)%2:
            return ds
        else:
            return ds + [[-1,1],[1,1],[-1,-1],[1,-1]]
   
    def __str__(self):
        lpad = len(hex(self.rows)) - 2
        m = self.cols
        lines = [' '*(lpad+1) + ''.join(['{:^2}'.format(hex(c)[2:] if c-1 != self.cursor[1] else '*') for c in range(1,m+1)])]
        lines.append(' '* lpad +"_".join((m+1)//2 * ["/‾\\"]) + (m+1)%2 * "_")
        for row in range(self.rows):
            sides = '*' if row == self.cursor[0] else hex(row+1)[2:]
            lines.append("{n:>{pad}}|".format(n=sides,pad=lpad)+
                         "|".join([self.symbol(row,col) for col in range(m)]+[sides]))
            line = " "*lpad
            if row % 2:
                line += "/" if row < self.rows-1 else " "
                for col in range(m):
                    if col % 2:
                        line += "_/"
                    else:
                        line += "‾\\"
                if row == self.rows-1 and m % 2:
                    line = line[:-1]
            else:
                for col in range(m):
                    if col % 2:
                        line += "/‾"
                    else:
                        line += "\\_"
                if row == self.rows-1:
                    if m % 2:
                        line += "/"
                else:
                    if m % 2:
                        line += "/"
                    else:
                        line += "\\"
                    
            lines.append(line)
        lines.append(lines[0])
        return "\n".join(lines)
