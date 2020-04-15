#    Minesweeper
#    Copyright (C) 2020 Deidre House
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

import os
import random
from builtins import input # Python 2 & 3 cross-compatibility
from minesweeper import minesweeperboard
from msvcrt import getch
import pickle


_savefile_extension = ".minesweeper"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_board(w,h,m):
    """Generate a minesweeper board of size (w,h) with m (random) mines"""
    board = minesweeperboard.fill_board(w,h)
    locations = random.sample(range(w*h),m)
    for location in locations:
        board[location // w][location % w] = True
    return board

class MinesweeperInterface(object):

    def __init__(self):
        self.game_loop()
        

class MinesweeperCLI(MinesweeperInterface):

    def game_loop(self):
        board_types = minesweeperboard.MinesweeperBoard.__subclasses__()
        ngames = 0
        hasquit = False
        while True:
            if not ngames:
                clear()
            print("Welcome to minesweeper!") # welcome screen
            savedgames = [f for f in os.listdir() if os.path.splitext(f)[1] == _savefile_extension]
            while savedgames: #new/continue screen
                print("0 - New game")
                print("1 - Load game")
                print("2 - Delete saved game")
                print("q - quit")
                k = ord(getch())
                if k in [48,78,110]:
                    break
                elif k in [49,76,108]:
                    print("Saved games:") # show saves
                    for (i, f) in enumerate(savedgames):
                        print(str(i) + " - " + os.path.splitext(f)[0])
                    selection = input("Select save file to load (enter a number):")
                    try:
                        n = int(selection)
                        game_to_load = savedgames[n]
                        with open(game_to_load, 'rb') as f:
                            m = pickle.load(f)
                        self.play(m)
                    except (ValueError, IndexError):
                        print("Invalid selection")
                    except FileNotFoundError:
                        print("File not found!")
                        savedgames.pop(n)
                elif k in [50,68,100]:
                    print("Saved games:")
                    for (i, f) in enumerate(savedgames):
                        print(str(i) + " - " + os.path.splitext(f)[0])
                    selection = input("Select save file to delete (enter a number):")
                    try:
                        n = int(selection)
                        game_to_del = savedgames[n]
                        os.remove(game_to_del)
                        savedgames.pop(n)
                    except (ValueError, IndexError):
                        print("Invalid selection")
                    except FileNotFoundError:
                        print("File not found!")
                        savedgames.pop(n)
                elif k in [81, 113]:
                    hasquit = True
                    break
            if hasquit:
                print("Bye!")
                break
            print("Select board type:")
            for i, bt in enumerate(board_types):
                print("{0}- {1} minesweeper".format(i,bt.displayname))
            print("q- quit")
            choice = ord(getch())
            while choice not in list(range(48, 48 + len(board_types))) +[81,113]:
                print("Invalid input: enter the board number or q to quit\r", end = '')
                choice = ord(getch())
            if choice in [81,113]:
                print("Bye!" + " "*60)
                break
            board_type = board_types[choice-48]
            print(board_type.displayname + " board" + " "*50)
            default = board_type.defaults
            
            print("Select options   ")
            print("1- Default board")
            print("2- Custom board")
            print("q - cancel")
            option = chr(ord(getch()))
            while option not in "12qQ":
                print("Invalid input\r", end='')
                option = chr(ord(getch()))
            if option in "qQ": continue
            if option == "2":
                while True:
                    try:
                        rows = int(input("Number of rows: "))
                        assert(rows > 0)
                        columns = int(input("Number of columns: "))
                        assert(columns >0)
                        mines = int(input("Number of mines: "))
                        assert(0 < mines < rows * columns)
                        default = [columns, rows, mines]
                        break
                    except:
                        print("Invalid input")
            self.play(board_type(generate_board(*default)))
            ngames += 1

    
    def play(self, board):
        show_help = False
        clear()
        print("Mines remaining: {}".format(board.mine_count - board.flag_count))
        print(board)
        
        while not (board.won or board.boom):
            print("Current location: ({0},{1})   ".format(board.cursor[0]+1,board.cursor[1]+1))
            if show_help:
                print(board.helpmessage)
            k = ord(getch())
            # arrow key:
            if k == 224:
                d = ord(getch())
                # up arrow:
                if d == 72:
                    board.cursor[0] = max(0, board.cursor[0] - 1)
                elif d == 75:
                    board.cursor[1] = max(0, board.cursor[1] - 1)
                elif d == 77:
                    board.cursor[1] = min(board.cols - 1,
                                         board.cursor[1] + 1)
                elif d == 80:
                    board.cursor[0] = min(board.rows - 1 ,
                                         board.cursor[0] + 1)
            elif k == 32:
                board.mark(*board.cursor)
            elif k == 13:
                board.select(*board.cursor)
            elif k in [81, 113]:
                print("Sure you want to quit? (y/n)")
                k2 = ord(getch())
                if k2 in [89, 121]:
                    board.detonate()
                elif k2 in [0, 244]:
                    getch()
            elif k in [72, 104]:
                #help message
                show_help = not show_help
            elif k in [83, 115]:
                # save game
                savename = input("Save game as:")
                with open(savename + _savefile_extension, 'wb') as f:
                    pickle.dump(board, f, protocol=2)                
            elif k == 0:
                getch()
            clear()
            print("Mines remaining: {}".format(board.mine_count - board.flag_count))
            print(board)
        
        if board.won:
            print("You win!")
        elif board.boom:
            print("BOOM! game over.")


# One day!
#class MinesweeperGUI(MinesweeperInterface):



