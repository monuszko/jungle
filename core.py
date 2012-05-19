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

DIRS = ((0, 1), (1, 0), (0, -1), (-1, 0))

# Z - Black lair
# z - White lair

class Board:
    def __init__(self):
        self.terrain = ['..^Z^..',
                        '...^...',
                        '.......',
                        '.~~.~~.',
                        '.~~.~~.',
                        '.~~.~~.',
                        '.......',
                        '...^...',
                        '..^z^..']
        self.width = len(self.terrain[0])
        self.height = len(self.terrain)
        self.animals = dict()
        self.turn = 'White'

    def setup(self):

        self.placeanimal((0, 0), JumpingAnimal('Lion', 7, 'Black'))
        self.placeanimal((6, 0), JumpingAnimal('Tiger', 6, 'Black'))
        self.placeanimal((1, 1), Animal('Dog', 3, 'Black'))
        self.placeanimal((5, 1), Animal('Cat', 2, 'Black'))
        self.placeanimal((0, 2), SwimmingAnimal('Rat', 1, 'Black'))
        self.placeanimal((2, 2), Animal('Leopard', 5, 'Black'))
        self.placeanimal((4, 2), Animal('Wolf', 4, 'Black'))
        self.placeanimal((6, 2), Animal('Elephant', 8, 'Black'))

        self.placeanimal((6, 8), JumpingAnimal('Lion', 7, 'White'))
        self.placeanimal((0, 8), JumpingAnimal('Tiger', 6, 'White'))
        self.placeanimal((5, 7), Animal('Dog', 3, 'White'))
        self.placeanimal((1, 7), Animal('Cat', 2, 'White'))
        self.placeanimal((6, 6), SwimmingAnimal('Rat', 1, 'White'))
        self.placeanimal((4, 6), Animal('Leopard', 5, 'White'))
        self.placeanimal((2, 6), Animal('Wolf', 4, 'White'))
        self.placeanimal((0, 6), Animal('Elephant', 8, 'White'))
        
    def __str__(self):
        ret = []
        for y in range(self.height):
            line = ''
            for x in range(self.width):
                a = self.animals.get((x, y))
                if a:
                    line += str(a)
                else:
                    line += self.terrain[y][x]
            ret.append(line)
        return '\n'.join(ret)

    def placeanimal(self, coords, animal):
        self.animals[coords] = animal
        self.animals[coords].pos = coords

    def contains(self, coords):
        '''
        Checks if coordinates are within bounds.
        '''
        if coords[0] < 0 or coords[0] >= len(self.terrain[0]):
            return False
        if coords[1] < 0 or coords[1] >= len(self.terrain):
            return False
        return True

    def getground(self, coords):
        return self.terrain[coords[1]][coords[0]]

    def iswet(self, coords):
        if self.getground(coords) == '~':
            return True
        return False

    def abylocation(self, coords):
        if coords in self.animals:
            return self.animals[coords]
        return None

    def abyrank(self, rank):
        for a in self.animals.values():
            if a.rank == int(rank) and a.color == self.turn:
                return a
        return None

    def abyglyph(self, glyph):
        for a in self.animals.values():
            if str(a) == glyph and a.color == self.turn:
                return a
        return None

    def moveanimal(self, start, dest):
        '''
        Move an animal from start to dest. No questions asked.
        '''
        self.animals[dest] = self.animals[start]
        self.animals[dest].pos = dest
        del self.animals[start]
        self.turn = 'Black' if self.animals[dest].color == 'White' else 'White'

    def winner(self):
        '''
        Returns:
        None if game is not yet finished
        'Black' if Black has won, etc.
        '''
        for a in self.animals.values():
            if self.getground(a.pos) in ('z', 'Z'): # Won by lair capture
                return a.color

        canmove = False
        for a in self.animals.values():
            if a.color == self.turn and a.allowedmoves(self):
                canmove = True
                break
        if not canmove:
            return 'White' if self.turn == 'Black' else 'Black'
        
        return None

    def activeanimals(self):
        '''
        Returns a list of animals allowed to move this turn
        '''
        active = []
        for a in self.animals.values():
            if a.color == self.turn and a.allowedmoves(self):
                active.append(a)
        return active


class Animal:
    def __init__(self, name, rank, color):
        self.name  = name
        self.rank  = rank
        self.color = color
        self.pos   = None
        self.GLYPHS = 'abcdefgh' # For graphical representation

    def __str__(self):
        glyph = self.GLYPHS[self.rank - 1]
        if self.color == 'White':
            return glyph 
        return glyph.upper() 

    def allowedmoves(self, board):
        '''
        Returns possible moves, taking color and capturing into account.
        '''
        accepted = []
        for dest in self.listmoves(board, self.pos):
            victim = board.animals.get(dest)
            if not victim:
                g = board.getground(dest)
                if self.color == 'White' and g == 'z':
                    continue
                if self.color == 'Black' and g == 'Z':
                    continue
                accepted.append(dest)
            elif self.color == victim.color:
                continue
            elif board.iswet(self.pos) != board.iswet(dest):
                continue # Attack only water->water or ground->ground
            elif board.getground(dest) == '^':
                accepted.append(dest) # Anyone can kill a trapped animal
            elif self.rank == 1 and victim.rank == 8:
                accepted.append(dest) # Rat kills Elephant if it attacks first.
            elif self.rank < victim.rank:
                continue
            else:
                accepted.append(dest) # can be attacked
        return accepted

    def listmoves(self, board, start):
        '''
        Combines methods of movement (walking, swimming, jumping)
        '''
        moves = []
        moves.extend(self.walkmoves(board, start))
        return moves

    def walkmoves(self, board, start):
        '''
        Returns squares which can be entered by walking.
        '''
        walkmoves = []
        for di in DIRS:
            dest = (start[0] + di[0], start[1] + di[1])
            if board.contains(dest):
                if board.getground(dest) == '~': # can't walk INTO water
                    continue
                walkmoves.append(dest)
        return walkmoves

class SwimmingAnimal(Animal):
    def listmoves(self, board, start):
        '''
        Combines methods of movement (walking, swimming, jumping)
        '''
        moves = []
        moves.extend(self.walkmoves(board, start))
        moves.extend(self.swimmoves(board, start))
        return moves

    def swimmoves(self, board, start):
        swimmoves = []
        for di in DIRS:
            dest = (start[0] + di[0], start[1] + di[1])
            if board.contains(dest):
                if board.getground(dest) == '~':
                    swimmoves.append(dest)
        return swimmoves

class JumpingAnimal(Animal):
    def listmoves(self, board, start):
        '''
        Combines methods of movement (walking, swimming, jumping)
        '''
        moves = []
        moves.extend(self.walkmoves(board, start))
        moves.extend(self.jumpmoves(board, start))
        return moves

    def jumpdest(self, board, start, vector):
        '''
        Return a destination of a jump or None if impossible
        '''
        dest = start
        while board.contains(dest) and board.getground(dest) == '~':
            if board.animals.get(dest) is not None:
                return None
            dest = (dest[0] + vector[0], dest[1] + vector[1])
        if board.getground(dest) != '~': # There is land past the lake
            return dest

    def jumpmoves(self, board, start):
        jumpmoves = []
        for di in DIRS:
            first = (start[0] + di[0], start[1] + di[1])
            if board.contains(first) and board.getground(first) == '~':
                dest = self.jumpdest(board, first, di)
                if dest is not None:
                    jumpmoves.append(dest)
        return jumpmoves

