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

from minesweeper import minesweeperboard
from msvcrt import getch
import pickle

def game_loop():
    board_types = minesweeperboard.MinesweeperBoard.__subclasses__()
    ngames = 0
    hasquit = False
    while True:
        if not ngames:
            minesweeperboard.clear()
        print("Welcome to minesweeper!")
        savedgames = [f for f in os.listdir() if os.path.splitext(f)[1] == minesweeperboard._savefile_extension]
        while savedgames:
            print("0 - New game")
            print("1 - Load game")
            print("2 - Delete saved game")
            print("q - quit")
            k = ord(getch())
            if k in [48,78,110]:
                break
            elif k in [49,76,108]:
                print("Saved games:")
                for (i, f) in enumerate(savedgames):
                    print(str(i) + " - " + os.path.splitext(f)[0])
                selection = input("Select save file to load (enter a number):")
                try:
                    n = int(selection)
                    game_to_load = savedgames[n]
                    with open(game_to_load, 'rb') as f:
                        m = pickle.load(f)
                    m.play()
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
        board_type(minesweeperboard.generate_board(*default)).play()
        ngames += 1
		
if __name__ == "__main__":
    game_loop()