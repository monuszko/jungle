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

terrain = ['..^@^..',
           '...^...',
           '.......',
           '.~~.~~.',
           '.~~.~~.',
           '.~~.~~.',
           '.......',
           '...^...',
           '..^@^..']

class Board:
    def __init__(self, terrain):
        self.terrain = terrain
        self.width = len(self.terrain[0])
        self.height = len(self.terrain)
        self.animals = dict()
        self.turn = 'white'

    def __str__(self):
        ret = ''
        for y in range(self.height):
            for x in range(self.width):
                a = self.animals.get((x, y))
                if a:
                    ret += str(a.rank)
                else:
                    ret += self.terrain[y][x]
            ret += '\n'
        return ret

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
        if self.terrain[coords[1]][coords[1]] == '~':
            return True
        return False

    def abylocation(self, coords):
        return self.animals[coords]

    def abyrank(self, rank, color):
        for v in self.animals.values():
            if v.rank == rank and v.color == color:
                return v

    def moveanimal(self, start, dest):
        '''
        Move an animal from start to dest. No questions asked.
        '''
        self.animals[dest] = self.animals[start]
        self.animals[dest].pos = dest
        del self.animals[start]
        self.turn = 'black' if self.animals[dest] == 'white' else 'white'


class Animal:
    def __init__(self, name, rank, color):
        self.name  = name
        self.rank  = rank
        self.color = color
        self.pos   = None

    def allowedmoves(self, board):
        '''
        Start - coords from which the animal moves
        '''
        accepted = []
        for dest in self.listmoves(board, self.pos):
            victim = board.animals.get(dest)
            if not victim:
                accepted.append(dest)
            elif self.color == victim.color:
                continue
            elif board.iswet(start) != board.iswet(dest):
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
        # TODO: make it impossible to walk into your own lair
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
            if board.getground(first) == '~':
                dest = self.jumpdest(board, first, di)
                if dest is not None:
                    jumpmoves.append(dest)
        print('jumps:', jumpmoves)
        return jumpmoves



  
if __name__ == '__main__':
    pass

b = Board(terrain)
b.placeanimal((1, 4), SwimmingAnimal('Szczur', 1, 'black'))
b.placeanimal((3, 4), JumpingAnimal('Kot', 2, 'black'))
print(b)
#a = b.abylocation((2, 6))
a = b.abyrank(2, 'black')
print(a.allowedmoves(b))
