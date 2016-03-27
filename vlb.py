import urwid

class VimListBox(urwid.ListBox):
    """A ListBox subclass which provides vim-like and mouse scrolling.

    Additional properties:
    size -- a tuple (width, height) of the listbox dimensions
    total_lines -- total number of lines
    pos -- a string containing vim-like scroll position indicator

    Additional signals:
    changed -- emited when the listbox content changes
    """
    signals = ['changed']

    def keypress(self, size, key):
        """Overrides ListBox.keypress method.

        Implements vim-like scrolling.
        """
        if key == 'j':
            self.keypress(size, 'down')
            return True
        if key == 'k':
            self.keypress(size, 'up')
            return True
        return self.__super.keypress(size, key)
