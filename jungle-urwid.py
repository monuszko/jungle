from __future__ import division, print_function
import urwid
import core

def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

legend = {
        '.': ('light green', 'dark green'), # grass
        '^': ('light gray', 'yellow'), # trap
        'Z': ('dark gray', 'dark gray'), # black lair
        'z': ('light gray', 'light gray'), # white lair
        '~': ('light blue', 'dark blue') # water
        }

class Viewport(urwid.WidgetWrap):
    '''
    The widget displaying the board.
    '''
    def __init__(self, board):
        self.board = board # The brain
        lines = []
        for y in range(self.board.height):
            row = []
            for x in range(self.board.width):
                glyph, fg, bg = self.looks(x, y, legend)
                square = urwid.AttrMap(urwid.SolidFill(glyph), 
                                                        urwid.AttrSpec(fg, bg))
                row.append(square)
            row = urwid.Columns([('fixed', 2, square) for square in row])
            lines.append(row)

        display_widget = urwid.Pile([('fixed', 2, line) for line in lines])
        urwid.WidgetWrap.__init__(self, display_widget)

    def looks(self, x, y, legend):
        '''
        Returns a tuple (glyph, fg, bg)
        '''
        animal = self.board.abylocation((x, y))
        ground = self.board.getground((x, y))
        bg = legend[ground][1]
        if animal is not None:
            glyph = str(animal.rank)
            fg = animal.color.lower()
        else:
            glyph = self.board.getground((x, y))
            fg = legend[ground][0]
        return (glyph, fg, bg)

    def paint(self, x, y, how):
        '''
        How - a tuple (glyph, fg, bg)
        '''
        self._w.widget_list[y].widget_list[x].original_widget.fill_char = how[0]
        amap = {None: urwid.AttrSpec(how[1], how[2])}
        self._w.widget_list[y].widget_list[x].set_attr_map(amap)



b = core.Board()
b.setup()
viewport = urwid.LineBox(Viewport(b))

fill = urwid.Filler(viewport)
loop = urwid.MainLoop(fill, unhandled_input=show_or_exit)
loop.run()
