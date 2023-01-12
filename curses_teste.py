import curses

screen = curses.initscr()

screen.addstr("Hello, I will be cleared in 2 seconds.")
# get some input
screen.getch()
screen.refresh()
curses.napms(2000)

# Wipe the screen buffer and set the cursor to 0,0
screen.clear()

screen.refresh()
curses.napms(2000)

curses.endwin()