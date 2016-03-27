# somy

A simple & fast internet radio player for the terminal.  
Runs an mplayer instance and controls it via a FIFO.  
I wrote this for myself but it might work for you too, who knows.  
Inspired by [soma](http://www.dawoodfall.net/slackbuilds/noversion/soma).

![a screenshot](https://github.com/kamiheku/somy/raw/master/screenshot.png)

## Requirements:

- urwid
- mplayer
- aplay on Linux, afplay on OS X

## Installation:

1. Copy somy to your $PATH
2. Copy the supplied configuration files (and static.wav) to ~/.somy/
3. Edit the configuration files.
4. Install urwid and mplayer.
5. Run and enjoy.

## Usage:

- up/down or j/k: move up and down on the stations list
- Enter: play
- Numbers (1..0): control the volume (0%..100%)
- m: mute
- s: stop the playback
- q: quit

## stations.conf:

The format is as follows:

```
The name of the stations,http://the-url-of-the-stream/stream.pls,tag1;tag2;tag3
```
