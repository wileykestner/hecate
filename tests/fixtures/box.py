#!/usr/bin/env python3

import curses


def start(screen):
    curses.cbreak()
    curses.noecho()
    curses.curs_set(0)

    text_window = screen.subwin(3, 12, 0, 0)
    text_window.box()
    text_window.addstr(1, 1, "I am a box")
    screen.noutrefresh()
    text_window.noutrefresh()
    curses.doupdate()

    while True:
        c = screen.getch()
        if c == ord('q'):
            break

    curses.endwin()


def main():
    curses.wrapper(start)


if __name__ == "__main__":
    main()
