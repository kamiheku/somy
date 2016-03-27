import os
import time
import urwid
from subprocess import Popen, DEVNULL, run
from vlb import VimListBox

# TODO:
# [✓] mute / stop
# [✓] tags (genres)
# [✓] colors (for genres too)
# [✓] title (now playing)
# [✓] quit with 'q'
# [ ] tag colors in a config file
# [ ] cleanup
# [ ] comments

stationsFile = "/home/karri/.somy/stations.conf"

colors = [('black','black',''),
          ('dark red','dark red',''),
          ('dark green','dark green',''),
          ('brown','brown',''),
          ('dark blue','dark blue',''),
          ('dark magenta','dark magenta',''),
          ('dark cyan','dark cyan',''),
          ('light gray','light gray',''),
          ('dark gray','dark gray',''),
          ('light red','light red',''),
          ('light green','light green',''),
          ('yellow','yellow',''),
          ('light blue','light blue',''),
          ('light magenta','light magenta',''),
          ('light cyan','light cyan',''),
          ('white','white','')]

genreColors = {'ambient':'dark cyan',
               'chillout':'light cyan',
               'soul':'brown',
               'lounge':'yellow',
               'jazz':'yellow',
               'techno':'dark blue',
               'tech house':'light blue',
               'deep house':'dark magenta',
               'house':'light magenta',
               'dubstep':'dark red',
               'dub-techno':'dark red',
               'electro':'light red',
               'breaks':'light red',
               'electronic':'light green',
               'downtempo':'dark green'}


colorsReverse = {x[0]:'reversed' for x in colors}
colorsReverse.update({None:'reversed'})

class Station:
    def __init__(self, name, url, tags):
        self.name = name
        self.url = url
        self.tags = tags

class Player:
    def __init__(self, station):
        self.station = station
        self.process = None
        self.fifopath = "/tmp/somy.fifo"
        os.mkfifo(self.fifopath)
    def stop(self):
        self.cmd("stop")
    def mute(self):
        self.cmd("mute")
    def play(self, station):
        self.station = station
        Popen(["aplay", "/home/karri/radio.wav"],
            stdin=DEVNULL,
            stdout=DEVNULL,
            stderr=DEVNULL)
        if self.process != None:
            if self.station.url[-3:] in ("pls", "m3u"):
                self.cmd("loadlist " + station.url)
            else:
                self.cmd("loadfile " + station.url)
        else:
            self.process = Popen(
                ["mplayer",
                 "-cache",
                 "64",
                 "-softvol",
                 "-prefer-ipv4",
                 "-slave",
                 "-idle",
                 "-ao",
                 "alsa",
                 "-input",
                 "file=" + self.fifopath,
                 "-playlist" if (self.station.url[-3:] in ("pls", "m3u")) else '',
                 self.station.url],
                stdin=DEVNULL,
                stdout=logfile,
                stderr=logfile)
    def cmd(self, command):
        with open(self.fifopath, 'w') as fifo:
            fifo.write("{}\n".format(command))

def parseStations():
    stations = []
    with open(stationsFile, 'r') as f:
        for line in f:
            chaninfo = line.strip().split(',')
            stations.append(Station(chaninfo[0], chaninfo[1], chaninfo[2]))
    return stations

def colorizeTags(tags):
    tagsplit = tags.split(" / ")
    colTags = [('dark gray', '[')]
    for i in range(len(tagsplit)):
        # colTags.append((choice(list(x[0] for x in colors)), tagsplit[i]))
        genre = tagsplit[i]
        if genre in genreColors.keys():
            color = genreColors[genre]
        else:
            color = "light gray"
        colTags.append((color, genre))
        if i < len(tagsplit) - 1:
            colTags.append(("white", " / "))
    colTags.append(('dark gray', ']'))
    return colTags

class Somy:
    def __init__(self):
        self.player = Player("/usr/bin/mplayer")
        self.stations = parseStations()
        self.title = ('logo', u'somy v0.0')
        self.header = urwid.Text(self.title, 'center')
        self.main = self.drawMenu(self.stations)

    def drawMenu(self, stations):
        body = []
        for station in stations:
            button = urwid.Button([station.name + ' '] + colorizeTags(station.tags))
            urwid.connect_signal(button, 'click', self.item_chosen, user_args=[station, self.player])
            body.append(urwid.AttrMap(button, None, focus_map=colorsReverse))
        menu = VimListBox(urwid.SimpleFocusListWalker(body))
        top = urwid.Overlay(menu, urwid.SolidFill(u' '),
            align='center', width=('relative', 100),
            valign='middle', height=('relative', 100),
            min_width=20, min_height=9)
        frame = urwid.Frame(top, self.header)
        return (frame)

    def updateTitle(self, newtitle):
        self.header.set_text([self.title, " | Now Playing: " + newtitle])

    def item_chosen(self, station, player, button):
        self.updateTitle(station.name)
        player.play(station)

    def keyHandler(self, key):
        if key in ('q', 'Q'):
            self.player.stop()
            os.remove(self.player.fifopath)
            raise urwid.ExitMainLoop()
        elif key in ('s', 'S'):
            self.header.set_text(self.title)
            self.player.stop()
        elif key in ('m', 'M'):
            self.player.mute()
        elif key in ('1','2','3','4','5','6','7','8','9'):
            self.player.cmd("set_property volume {}0".format(key))
        elif key == '0':
            self.player.cmd("set_property volume 100".format(key))

def main():
    somy = Somy()
    urwid.MainLoop(somy.main,
                   palette=[('reversed', 'standout', ''),
                            ('station', 'light blue', ''),
                            ('tags', 'light blue', ''),
                            ('logo', 'dark blue', '')] + colors,
                   unhandled_input=somy.keyHandler).run()

if __name__ == "__main__":
    with open("/home/karri/somylog", 'w') as logfile:
        main()
