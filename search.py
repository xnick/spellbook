#!/bin/env python3


import json
import sys
import curses
import string
import textwrap
import traceback

def search(terms, spelllist):
    spells=[]
    for spell in spelllist:
        if all(term in spell["name"].lower() for term in terms):
            spells.append(spell)
    return spells


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
curses.cbreak()

spells=[]
searchterms=[]

try:
    with open("spells.json") as jfile:
        jdata=json.load(jfile)
    stdscr.border()
    stdscr.refresh()
    y=curses.LINES-1
    x=curses.COLS

    i=0
    inp=""
    
    resWiny=int(y*0.8)
    resWinx=x-1
    resWin=curses.newwin(resWiny,resWinx,1,1)
    resWin.border()
    resWin.refresh()
    
    debugWiny=1
    debugWinx=x
    debugWin=curses.newwin(debugWiny,debugWinx,y,0)
    debugWin.border()
    debugWin.keypad(True)
    
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
            if i>0:
                searchterms=searchWin.instr(0, 8, i).decode("utf-8").lower().split(' ')
                spells=search(searchterms, jdata)
                if len(spells)>0:
                    clearandborder(resWin)
                    resWin.addstr(1,1,spells[0]['name'])
                    addlong(spells[0]['description'], resWin, resWiny-3, resWinx-2, 2, 1)
        elif ch in ['^W', '\x17']:
            i=searchWin.instr(0,8,i).decode("utf-8").rfind(' ')
            if i<0:
                i=0
            searchWin.move(0, 8+i)
        elif ch in ['KEY_ENTER', '\n']:
            ch='KEY_ENTER'
            pass
        elif ch in ['KEY_RIGHT', 'KEY_LEFT', 'KEY_UP', 'KEY_DOWN']:
            # Select spells from suggestions
            pass
        elif ch in string.printable:
            if i<searchWinx-10:
                i+=1
            searchterms=searchWin.instr(0, 8, i).decode("utf-8").lower().split(' ')
            spells=search(searchterms, jdata)
            if len(spells)>0:
                clearandborder(resWin)
                resWin.addstr(1,1,spells[0]['name'])
                addlong(spells[0]['description'], resWin, resWiny-3, resWinx-2, 2, 1)
        else:
            raise Exception("What was that?")

        # Suggestions
        clearandborder(suggWin)
        addlong('\t'.join(spell['name'] for spell in spells), suggWin, suggWiny-2, suggWinx-2, 1,1)

        searchWin.move(0, 8+i)
        searchWin.clrtoeol()
        searchWin.vline(0,searchWinx-1,'|', 1)
        
        clearandborder(debugWin)
        debugWin.addstr(0, x-25, ' '+str(i)+' ')
        debugWin.addstr(0, x-20, ' '+ch+' ')
        debugWin.addstr(0, 2, ' '.join(searchterms))

        debugWin.refresh()
        searchWin.refresh()
        resWin.refresh()
        suggWin.refresh()

except KeyboardInterrupt as e:
    curses.nocbreak()
    stdscr.keypad(False)
    curses.endwin()
    traceback.print_exc()
    print(ch)
    exit()
except Exception as e:
    curses.nocbreak()
    stdscr.keypad(False)
    curses.endwin()
    traceback.print_exc()
    print(ch)
    exit()

