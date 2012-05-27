#! /usr/bin/env python3

import unittest
from core import DIRS, Board, Animal, SwimmingAnimal, JumpingAnimal

class TestBoard(unittest.TestCase):
    """
    A test for the Board class. Tests only for more complicated methods.
    """
    def setUp(self):
        self.board = Board()
        self.board.setup()

    def test_moveanimal(self):

        self.assertIn((0, 0), self.board.animals)
        self.board.moveanimal((0, 0), (0, 1))
        self.assertNotIn((0, 0), self.board.animals)
        self.assertEqual(self.board.animals[(0, 1)].name, 'Lion')
    
    def test_contains(self):
        self.assertTrue(self.board.contains((0, 0)))
        self.assertTrue(self.board.contains((1, 1)))
        self.assertTrue(self.board.contains((6, 8)))

        self.assertFalse(self.board.contains((-1, 0)))
        self.assertFalse(self.board.contains((1, -1)))
        self.assertFalse(self.board.contains((7, 7)))
        self.assertFalse(self.board.contains((6, 9)))

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBoard))


if __name__ == '__main__':
    unittest.main()
