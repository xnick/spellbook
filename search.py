#!/bin/env python3


import json
import sys
import curses
import string
import textwrap
import traceback

def clearandborder(screen):
    screen.move(0,0)
    screen.clrtobot()
    screen.border()

def addlong(lstr, screen, maxy, maxx, posy, posx):
    lineno=0
    for line in textwrap.wrap(lstr, maxx-1):
        screen.addstr(posy+lineno, posx, line)
        lineno+=1
        if lineno==maxy:
            break

stdscr = curses.initscr()
#curses.noecho()
curses.cbreak()

try:
    with open("spells.json") as jfile:
        jdata=json.load(jfile)
    stdscr.border()
    stdscr.refresh()
    y=curses.LINES-1
    x=curses.COLS-1

    i=0
    inp=""
    
    resWiny=int(y*0.8)
    resWinx=x-1
    resWin=curses.newwin(resWiny,resWinx,1,1)
    resWin.border()
    resWin.refresh()
    
    searchWiny=1
    searchWinx=x-1
    searchWin=curses.newwin(searchWiny,searchWinx,y-1,1)
    searchWin.keypad(True)

    suggWiny=y-resWiny-searchWiny-1
    suggWinx=x-1
    suggWin=curses.newwin(suggWiny,suggWinx,resWiny+1,1)
    suggWin.border()
    suggWin.refresh()


    while(True):
        searchWin.addstr(0, 0, "Search: ")
        ch=searchWin.getkey(0,8+i)
        stdscr.border()
        if ch in ['KEY_RESIZE']:
            raise Exception('Ham and green eggs')
        elif ch in ['KEY_BACKSPACE']:
            if i>0:
                i-=1
        elif ch in ['^W', '\x17']:
            i=searchWin.instr(0,8,i).decode("utf-8").rfind(' ')
            if i<0:
                i=0
            searchWin.move(0, 8+i)
        elif ch in ['KEY_ENTER', '\n']:
            pass
        elif ch in ['KEY_RIGHT', 'KEY_LEFT', 'KEY_UP', 'KEY_DOWN']:
            # Select spells from suggestions
            pass
        elif ch in string.printable:
            if i<searchWinx-10:
                i+=1
        else:
            raise Exception("What was that?")
        stdscr.addstr(y, searchWinx-20, ' '+str(i)+' ')
        stdscr.addstr(y, searchWinx-15, ' '+ch+' ')
        searchWin.clrtoeol()

        if i>0:
            # Results
            searchstr=searchWin.instr(0, 8, i).decode("utf-8").lower().split(' ')
            result=False
            suggestions=[]
            for spell in jdata:
                if all(term in spell["name"].lower() for term in searchstr):
                    if not result:
                        result=True
                        clearandborder(resWin)
                        resWin.addstr(1, 1, spell["name"])
                        addlong(spell["description"], resWin, resWiny-3,
                                resWinx-2, 2, 1)
                    suggestions.append("'"+spell['name'].replace(' ', '_')+"'")
            # Suggestions
            suggestions='\t'.join(suggestions)
            clearandborder(suggWin)
            addlong(suggestions, suggWin, suggWiny-2, suggWinx-2, 1,1)
        else:
            clearandborder(resWin)
            clearandborder(suggWin)

        stdscr.refresh()
        resWin.refresh()
        suggWin.refresh()

except KeyboardInterrupt as e:
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    traceback.print_exc()
    exit()
except Exception as e:
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    traceback.print_exc()
    print(hex(int(ch)))
    exit()
curses.nocbreak()
curses.echo()
curses.endwin()

