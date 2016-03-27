import time
import urwid
import configparser
from os import mkfifo, remove
from os.path import expanduser
from subprocess import Popen, DEVNULL, run
from vlb import VimListBox

# TODO:
# [✓] mute / stop
# [✓] tags (genres)
# [✓] colors (for genres too)
# [✓] title (now playing)
# [✓] quit with 'q'
# [✓] tag colors in a config file
# [ ] cleanup
# [ ] comments

home = expanduser('~')
stations_file = home + "/.somy/stations.conf"
config_file = home + "/.somy/somy.conf"
noise_file = home + "/.somy/static.wav"

config = configparser.ConfigParser()
config.read(config_file)

genre_colors = config["colors"]

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

colors_reverse = {x[0]:'reversed' for x in colors}
colors_reverse.update({None:'reversed'})

def parseStations():
    """Parses stations from the stations file.
    
    Returns:
        A list of Stations.
    """
    stations = []
    with open(stations_file, 'r') as f:
        for line in f:
            chaninfo = line.strip().split(',')
            stations.append(Station(chaninfo[0], chaninfo[1], chaninfo[2]))
    return stations

def colorizeTags(tags):
    tagsplit = tags.split(";")
    colTags = [('dark gray', '[')]
    for i in range(len(tagsplit)):
        # colTags.append((choice(list(x[0] for x in colors)), tagsplit[i]))
        genre = tagsplit[i]
        if genre in genre_colors.keys():
            color = genre_colors[genre]
        else:
            color = "light gray"
        colTags.append((color, genre))
        if i < len(tagsplit) - 1:
            colTags.append(("white", " / "))
    colTags.append(('dark gray', ']'))
    return colTags

class Station:
    def __init__(self, name, url, tags):
        self.name = name
        self.url = url
        self.tags = tags

class Player:
    def __init__(self, station, config):
        self.config = config
        self.station = station
        self.process = None
        self.fifopath = "/tmp/somy.fifo"
        self.volume = 100
        mkfifo(self.fifopath)

    def stop(self):
        self.cmd("stop")

    def mute(self):
        self.cmd("mute")

    def play(self, station):
        self.station = station
        Popen([self.config["config"]["simple_audio_player"], noise_file],
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
        self.set_volume(self.volume)

    def cmd(self, command):
        with open(self.fifopath, 'w') as fifo:
            fifo.write("{}\n".format(command))

    def set_volume(self, volume):
        self.volume = volume
        self.cmd("set_property volume {}".format(volume))

class Somy:
    def __init__(self, config):
        self.config = config
        self.player = Player("/usr/bin/mplayer", self.config)
        self.stations = parseStations()
        self.title = ('logo', u'somy v0.0')
        self.header = urwid.Text(self.title, 'center')
        self.main = self.draw_menu(self.stations)

    def draw_menu(self, stations):
        body = []
        for station in stations:
            button = urwid.Button([station.name + ' '] + colorizeTags(station.tags))
            urwid.connect_signal(button, 'click', self.item_chosen, user_args=[station, self.player])
            body.append(urwid.AttrMap(button, None, focus_map=colors_reverse))
        menu = VimListBox(urwid.SimpleFocusListWalker(body))
        top = urwid.Overlay(menu, urwid.SolidFill(u' '),
            align='center', width=('relative', 100),
            valign='middle', height=('relative', 100),
            min_width=20, min_height=9)
        frame = urwid.Frame(top, self.header)
        return (frame)

    def update_title(self, newtitle):
        self.header.set_text([self.title, " | Now Playing: " + newtitle])

    def item_chosen(self, station, player, button):
        self.update_title(station.name)
        player.play(station)

    def key_handler(self, key):
        if key in ('q', 'Q'):
            self.player.stop()
            remove(self.player.fifopath)
            raise urwid.ExitMainLoop()
        elif key in ('s', 'S'):
            self.header.set_text(self.title)
            self.player.stop()
        elif key in ('m', 'M'):
            self.player.mute()
        elif key in ('1','2','3','4','5','6','7','8','9'):
            self.player.set_volume(int(key + "0"))
        elif key == '0':
            self.player.set_volume(100)

def main():
    somy = Somy(config)
    urwid.MainLoop(somy.main,
                   palette=[('reversed', 'standout', ''),
                            ('station', 'light blue', ''),
                            ('tags', 'light blue', ''),
                            ('logo', 'dark blue', '')] + colors,
                   unhandled_input=somy.key_handler).run()

if __name__ == "__main__":
    with open("/home/karri/somylog", 'w') as logfile:
        main()
