#!/bin/env python3


import json
import sys
import curses
import string
import textwrap
import traceback

stdscr = curses.initscr()
#curses.noecho()
curses.cbreak()
stdscr.keypad(True)

try:
    with open("spells.json") as jfile:
        jdata=json.load(jfile)
    stdscr.border()
    stdscr.refresh()
    y=curses.LINES-1
    x=curses.COLS-1

    i=0
    inp=""
    
    resWiny=int(y*0.7)
    resWinx=x-1
    resWin=curses.newwin(resWiny,resWinx,1,1)

    resWin.border()
    resWin.refresh()
    
    searchWiny=1
    searchWinx=x-1
    searchWin=curses.newwin(searchWiny,searchWinx,y-1,1)

    suggWiny=y-resWiny-searchWiny-1
    suggWinx=x-1
    suggWin=curses.newwin(suggWiny,suggWinx,resWiny+1,1)
    suggWin.border()
    suggWin.refresh()


    while(True):
        searchWin.addstr(0, 0, "Search: ")
        ch=searchWin.getkey(0,8+i)
        if ch in [curses.KEY_RESIZE]:
            raise Exception('Ham and green eggs')
        elif ch in [curses.KEY_BACKSPACE, '\b', '\x7f']:
            if i>0:
                i-=1
        elif ch in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP, curses.KEY_DOWN]:
            pass
        elif ch in string.printable:
            if i<x-2:
                i+=1
        searchWin.clrtoeol()

        if i>0:
            # Results
            searchstr=searchWin.instr(0, 8, i).decode("utf-8").lower().split(' ')
            first=False
            suggestions=[]
            for spell in jdata:
                if all(term in spell["name"].lower() for term in searchstr):
                    if not first:
                        first=True
                        resWin.move(0,0)
                        resWin.clrtobot()
                        resWin.border()
                        resWin.addstr(1, 1, spell["name"])
                        lineno=0
                        for line in textwrap.wrap(spell["description"],
                                resWinx-2):
                            resWin.addstr(2+lineno, 1, line)
                            lineno+=1
                            if lineno==resWiny-4:
                                break
                    resWin.refresh()
                    suggestions.append("'"+spell['name'].replace(' ', '_')+"'")
            # Suggestions
            suggestions='\t'.join(suggestions)
            suggestions=textwrap.wrap(suggestions, int(suggWinx-2))
            lineno=0
            suggWin.move(0,0)
            suggWin.clrtobot()
            suggWin.border()
            for line in suggestions:
                suggWin.addstr(1+lineno,1,line.replace('_', ' '))
                lineno+=1
#               break
                if lineno==suggWiny-2:
                    break
            suggWin.refresh()
        else:
            pass

except Exception as e:
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    traceback.print_exc()
    for line in suggestions:
        print(line)
    exit()
curses.nocbreak()
stdscr.keypad(False)
curses.echo()
curses.endwin()

