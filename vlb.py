import urwid

class VimListBox(urwid.ListBox):
    """A ListBox subclass which provides vim-like and mouse scrolling."""

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
