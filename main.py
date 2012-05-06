#! /usr/bin/env python3 
#    written for Python 3.2
#    Copyright (C) 2012 Marek Onuszko
#    marek.onuszko@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, print_function
import core

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


def boardplusmoves(board, keymoves):
    '''
    Returns str(board) with added movement hints.
    '''
    view = str(board).split('\n')
    view = [list(line) for line in view]
    for key in keymoves:
        x, y = keymoves[key][0], keymoves[key][1]
        view[y][x] = key

    view = [''.join(line) for line in view]
    view = '\n'.join(view)
    return view

def selectanimal(board, char):
        a = b.abyglyph(char)
        moves = a.allowedmoves(b)
        selectdestination(board, a, moves)

def selectdestination(board, animal, moves):
    keymoves = {}
    for key, move in enumerate(moves):
        keymoves[str(key + 1)] = move 
    print(boardplusmoves(b, keymoves))
    print("{} to select destination, {} to deselect animal.".format(
                                      ', '.join(keymoves.keys()), str(animal)))
    char = getch()
    while char not in keymoves and char != str(animal):
        char = getch()
    if char == str(animal):
        return
    b.moveanimal(animal.pos, keymoves[char])

getch = _Getch()

b = core.Board()
b.setup()

while not b.winner():
    print(b)

    glyphs = []
    for animal in b.animals.values():
        if animal.color == b.turn and animal.allowedmoves(b):
            glyphs.append(str(animal))
    glyphs = sorted(glyphs)

    print("{} player's turn. {} to select animal, q to quit.".format(
                                                    b.turn, ', '.join(glyphs)))
    char = getch()
    while char not in glyphs and char != 'q':
        char = getch()
    if char == 'q':
        break

    selectanimal(b, char)
    print()

winner = b.winner()
if winner is not None:
    print('The {} player has won !'.format(winner))
else:
    print('{} player surrenders.'.format(b.turn))
