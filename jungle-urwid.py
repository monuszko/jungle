from __future__ import division, print_function
import urwid
import core

COLS = 7
ROWS = 9
# TODO: Try to remove globals


legend = {
        '.': ('light green', 'dark green'), # grass
        '^': ('light gray', 'yellow'), # trap
        'Z': ('dark gray', 'dark gray'), # black lair
        'z': ('light gray', 'light gray'), # white lair
        '~': ('light blue', 'dark blue') # water
        }

class BoardSizer(urwid.Overlay):


    def calculate_padding_filler(self, size, focus):
        maxcol, maxrow = size
        n = max(1, min(maxcol // COLS, maxrow // ROWS))
        left = (maxcol - n * COLS) // 2
        right = maxcol - n * COLS - left
        top = (maxrow - n * ROWS) // 2
        bottom = maxrow - n * ROWS - top
        return [max(0, x) for x in (left, right, top, bottom)]

class Display(urwid.WidgetWrap):
    '''
    The widget displaying the board.
    '''
    def __init__(self, width, height, legend):
        self.legend = legend

        lines = []
        for y in range(height):
            row = []
            for x in range(width):
                square = urwid.AttrMap(urwid.SolidFill('x'), urwid.AttrSpec('default', 'default'))
                row.append(square)
            row = urwid.Columns(row)
            lines.append(row)
        
        grid = urwid.Pile(lines)
        urwid.WidgetWrap.__init__(self, grid)

    def update(self, board):
        for y in range(board.height):
            for x in range(board.width):
                brush = self.looks(board, x, y)
                self.paint(x, y, brush)

    def looks(self, board, x, y):
        '''
        Returns a tuple (glyph, fg, bg)
        '''
        animal = board.abylocation((x, y))
        ground = board.getground((x, y))
        bg = self.legend[ground][1]
        if animal is not None:
            glyph = str(animal.rank)
            fg = animal.color.lower()
        else:
            glyph = board.getground((x, y))
            fg = self.legend[ground][0]
        return (glyph, fg, bg)

    def paint(self, x, y, how):
        '''
        How - a tuple (glyph, fg, bg)
        '''
        self._w.widget_list[y].widget_list[x].original_widget.fill_char = how[0]
        amap = {None: urwid.AttrSpec(how[1], how[2])}
        self._w.widget_list[y].widget_list[x].set_attr_map(amap)


class GameStateManager():
    def __init__(self, board, display, mesg):
        self.board = board
        self.display = display
        self.mesg = mesg
        self.state = 'animal' 
        self.actor = None # Which animal is currently moving
        self.movekeys = 'abcd'
    def handle_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        if self.board.winner():
            raise urwid.ExitMainLoop()
        elif self.state == 'animal':
            self.choose_animal(key)
        elif self.state == 'destination':
            self.choose_destination(key)
    def choose_animal(self, key):
        active = self.board.activeanimals()
        for anim in active:
            if str(anim.rank) == key:
                self.state = 'destination'
                self.actor = anim
                self.paint_destinations()
    def choose_destination(self, key):
        if key == str(self.actor.rank):
            self.state = 'animal'
            self.display.update(self.board)
            return
        pass
    def paint_destinations(self):
        for move in zip(self.actor.allowedmoves(self.board), self.movekeys):
            x, y = move[0]
            self.mesg.set_text(str(move))
            self.display.paint(x, y, ('!', 'white', 'dark red'))

if __name__ == '__main__':
    b = core.Board()
    b.setup()
    bg = urwid.SolidFill('`')

    display = Display(COLS, ROWS, legend)
    display.update(b)

    header = urwid.Text('Jungle')
    footer = urwid.Text('Messages')
    topwidget = urwid.Frame(BoardSizer((display), bg, 'left', 1, 'top', 1),
                            header=header,
                            footer=footer
                            )
    #display.paint(2, 3, ('C', 'dark magenta', 'dark cyan'))

    gsm = GameStateManager(b, display, footer)
    loop = urwid.MainLoop(topwidget, unhandled_input=gsm.handle_input)
    loop.run()


print('{} player surrenders.'.format(b.turn))
