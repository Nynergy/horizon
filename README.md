# horizon

A TUI controller for Logitech Media Server

### *This is a work in progress :: Use at your own risk :)*

------------------------------------------------------------------------------

## What is horizon and why does it exist?

_horizon_ is a Terminal User Interface (TUI) meant to control and display
information from a [Logitech Media
Server](https://en.wikipedia.org/wiki/Logitech_Media_Server) (LMS). Users of
[ncmpcpp](https://github.com/ncmpcpp/ncmpcpp) may find the look and feel of
_horizon_ pretty similar, and that is by design. I've used ncmpcpp with mpd
extensively in the past, but recently I've moved to hosting my own music server
using LMS, which means no mpd, and therefore no ncmpcpp.

Luckily, someone went through the trouble of writing a [Python
library](https://github.com/roberteinhaus/lmsquery) that can query the LMS for
information, and even run commands! All you need to provide it is the IP and
Port your LMS is running on, which in most cases you'll know if you've set up
the LMS on your home network.

So I did what I do best -- go overboard by making a TUI just for an app I may
end up discarding in favor of a browser-based option down the road.

## What exactly does it do?

At the moment, not much. It doesn't have any command capabilities yet, so it
won't affect your server/players. But it is able to query a player for status
information, the current playlist, the current track playing, stuff like that.
You can scroll around the playlist screen and resize everything and watch the
progress bar go left to right as you listen to your music.

In the future I plan to allow you access to your media library, similar to what
ncmpcpp does, and give you commands to load songs/albums into the playlist and
play them. I would also like to give the user command over things like volume,
repeat/shuffle controls, saving and loading playlists, etc.

## How can I run it?

First, you'll need to make sure you have the proper libraries installed. See the
link to `lmsquery` above to find installation instructions for that. Otherwise,
just make sure you have curses for Python.

Then, from the base directory, run `./main.py`

The main file specifies python3.8 due to `lmsquery`, so make sure you have that
version of Python installed.

## How can I configure it?

For right now, configuration is done in the `config.json` file. See the config
file provided in the repository for how to customize it.

## How do I use it?

Here are the commands that exist right now:

### Playlist Commands

Key | Action
----|-------
<kbd>q</kbd> | quit horizon
<kbd>j</kbd> and <kbd>k</kbd> | change track focus up and down

## Now what?

Wait until I implement more stuff, I don't know. Be patient. :)
