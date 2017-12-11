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

def addsugg(spellnames, selected, screen, maxy, maxx, posy, posx):
    lineno=posy
    colno=posx
    clearandborder(screen)
    for spell in spellnames:
        if colno>=maxx-len(spell):
            colno=posx
            lineno+=1
        if colno>=maxx-len(spell): #still
            raise Exception("You're too big!", spell)
        if lineno>=maxy:
            break

        if spell==selected:
            screen.addstr(lineno, colno, spell, curses.A_STANDOUT)
        else:
            screen.addstr(lineno, colno, spell, curses.A_UNDERLINE)
        colno+=len(spell)

        if colno<maxx-len('\t\t'):
            screen.addstr(lineno, colno, '\t\t')
            colno+=len('\t\t')
    screen.border()


def adddesc(lstr, screen, maxy, maxx, posy, posx, scroll):
    lineno=posy
    colno=posx
    lines=textwrap.wrap(lstr, maxx-1)
    if scroll>len(lines):
        scroll=len(lines)
    for line in lines[scroll:]:
        screen.addstr(lineno, colno, line)
        lineno+=1
        if lineno==maxy:
            break

stdscr = curses.initscr()
curses.cbreak()

spells=[]
searchterms=[]

with open("spells.json") as jfile:
    jdata=json.load(jfile)

spellbook={spell['name']:spell for spell in jdata}
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

debugWiny=1
debugWinx=x+1
debugWin=curses.newwin(debugWiny,debugWinx,y,0)
debugWin.border()

searchWiny=1
searchWinx=x-1
searchWin=curses.newwin(searchWiny,searchWinx,y-1,1)
searchWin.keypad(True)

suggWiny=y-resWiny-searchWiny-1
suggWinx=x-1
suggWin=curses.newwin(suggWiny,suggWinx,resWiny+1,1)
suggWin.border()
suggWin.refresh()

selected=''
selectionno=0
scroll=0
init=0
try:
    while(True):
        searchWin.addstr(0, 0, "Search: ")
        if not init:
            ch='\x17'
            init=1
        else:
            ch=searchWin.getkey(0,8+i)
        stdscr.border()
        if ch in ['KEY_RESIZE']:
            raise Exception('Ham and green eggs')
        elif ch in ['KEY_BACKSPACE']:
            if i>0:
                i-=1
            searchterms=searchWin.instr(0, 8, i).decode("utf-8").lower().split(' ')
            spells=search(searchterms, jdata)
        elif ch in ['^W', '\x17'] or not init:
            i=searchWin.instr(0,8,i).decode("utf-8").rfind(' ')
            if i<0:
                i=0
            searchWin.move(0, 8+i)
            searchterms=searchWin.instr(0, 8, i).decode("utf-8").lower().split(' ')
            spells=search(searchterms, jdata)
        elif ch in ['KEY_ENTER', '\n']:
            ch='KEY_ENTER'
            i=len(selected)
            searchWin.addstr(0, 8, selected)
            searchterms=searchWin.instr(0, 8, i).decode("utf-8").lower().split(' ')
            spells=search(searchterms, jdata)
            pass
        elif ch in ['KEY_RIGHT', 'KEY_LEFT', 'KEY_UP', 'KEY_DOWN']:
            if ch=='KEY_RIGHT':
                if selectionno<len(suggestions)-1:
                    selectionno+=1
                else:
                    selectionno=len(suggestions)-1
                scroll=0
            elif ch=='KEY_LEFT':
                if selectionno>0:
                    selectionno-=1
                scroll=0
            elif ch=='KEY_UP':
                if scroll>0:
                    scroll-=1
            elif ch=='KEY_DOWN':
                scroll+=1
            selected=suggestions[selectionno]
        elif ch in string.printable:
            if i<searchWinx-10:
                i+=1
            searchterms=searchWin.instr(0, 8, i).decode("utf-8").lower().split(' ')
            spells=search(searchterms, jdata)
        else:
            raise Exception("What was that?")

        # Suggestions
        clearandborder(suggWin)
        suggestions=[spell['name'] for spell in spells]
        if not selected or (selected not in suggestions and len(suggestions)):
            selected=suggestions[0]
            selectionno=0

        if selected:
            if selected in suggestions:
                selectionno=suggestions.index(selected)
            elif len(suggestions):
                selected=suggestions[0]
                selectionno=0

            clearandborder(resWin)
            resWin.addstr(1,1,spellbook[selected]['name'])
            adddesc(spellbook[selected]['description'], resWin, resWiny-1, resWinx-1, 2, 1, scroll)

        addsugg(suggestions, selected, suggWin, suggWiny-1, suggWinx-1, 1, 1)

        searchWin.move(0, 8+i)
        searchWin.clrtoeol()
        
        clearandborder(debugWin)
        debugWin.addstr(0, x-30, ' '+str(scroll)+' ')
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

