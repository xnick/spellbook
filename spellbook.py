#!/bin/env python3


import json
import sys
import curses
import string
import textwrap
import traceback

def search(terms, spelllist):
    spells=[]
    if terms[0].startswith('^'):
        term=' '.join(terms)[1:]
        for spell in spelllist:
            if spell['name'].lower().startswith(term):
                spells.append(spell)
    else:
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


def adddesc(desc, screen, maxy, maxx, posy, posx, scroll):
    lineno=posy
    colno=posx
    lines=[]
    for lstr in desc:
        if lstr is not None:
            lines.extend(textwrap.wrap(lstr, maxx-1))
            lines.append('\n')
    if scroll>len(lines):
        scroll=len(lines)
    for line in lines[scroll:]:
        if line is not '\n':
            screen.addstr(lineno, colno, line)
        lineno+=1
        if lineno==maxy:
            break
    return scroll

stdscr = curses.initscr()
curses.cbreak()

spells=[]
searchterms=[]
debug=False

with open("dnd-spells/spells.json") as jfile:
    jdata=json.load(jfile)

spellbook={spell['name']:spell for spell in jdata}

stdscr.border()
stdscr.refresh()

y=curses.LINES-1
x=curses.COLS-1


resWiny=min(int(y*0.8), y-5)
resWinx=x-1
resWin=curses.newwin(resWiny,resWinx,1,1)
resWin.border()

if debug:
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

i=0
inp=""
selected=''
selectionno=0
scroll=0
init=False
dosearch=True
try:
    while(True):
        searchWin.addstr(0, 0, "Search: ")
        if not init:
            ch='\x17' # piggy-back
            init=True
        else:
            ch=searchWin.getkey(0,8+i)
        stdscr.border()
        if ch in ['KEY_RESIZE']:
            curses.resize_term(*stdscr.getmaxyx())

            stdscr.refresh()

            y=curses.LINES-1
            x=curses.COLS-1

            resWiny=min(int(y*0.8), y-5)
            resWinx=x-1
            resWin.resize(resWiny,resWinx)
            resWin.border()
            
            if debug:
                debugWiny=1
                debugWinx=x+1
                debugWin.resize(debugWiny,debugWinx)
                debugWin.border()

            searchWiny=1
            searchWinx=x-1
            searchWin.resize(searchWiny,searchWinx)
            searchWin.mvwin(y-1,1)

            suggWiny=y-resWiny-searchWiny-1
            suggWinx=x-1
            suggWin.resize(suggWiny,suggWinx)
            suggWin.mvwin(resWiny+1, 1)
            suggWin.border()
            dosearch=True
        elif ch in ['KEY_BACKSPACE', '\b', '\x7f']:
            if i>0:
                i-=1
            dosearch=True
        elif ch in ['^W', '\x17']:
            i=searchWin.instr(0,8,i).decode("utf-8").rfind(' ')
            if i<0:
                i=0
            searchWin.move(0, 8+i)
            dosearch=True
        elif ch in ['KEY_ENTER', '\n']:
            ch='KEY_ENTER'
            i=len(selected)
            searchWin.addstr(0, 8, selected)
            dosearch=True
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
        elif ch in ['KEY_NPAGE', 'KEY_PPAGE']:
            if ch=='KEY_NPAGE':
                scroll+=resWiny-1
            elif ch=='KEY_PPAGE':
                scroll-=resWiny-1
                if scroll<0:
                    scroll=0
        elif ch in ['KEY_END', 'KEY_HOME']:
            if ch=='KEY_END':
                scroll+=999999#Sup
            elif ch=='KEY_HOME':
                scroll=0
        elif ch in string.printable:
            if i<searchWinx-10:
                i+=1
            dosearch=True
        else:
            raise Exception("What was that?")

        if dosearch:
            searchterms=searchWin.instr(0, 8, i).decode("utf-8").lower().split(' ')
            spells=search(searchterms, jdata)
            dosearch=False

        clearandborder(suggWin)
        suggestions=[spell['name'] for spell in spells]
        if not selected or (selected not in suggestions and len(suggestions)):
            selected=suggestions[0]
            selectionno=0
            scroll=0

        if selected:
            if selected in suggestions:
                selectionno=suggestions.index(selected)
            elif len(suggestions):
                selected=suggestions[0]
                selectionno=0

            clearandborder(resWin)
            resWin.addstr(1,1,spellbook[selected]['name'])

            desc=[]
            desc.append(spellbook[selected].get('level')+
                    " "+spellbook[selected].get('school')+' ('+
                    spellbook[selected].get('class')+')')
            desc.append('Range: '+spellbook[selected].get('range'))
            desc.append('Casting Time: '+spellbook[selected].get('casting_time'))
            desc.append('Duration: '+spellbook[selected].get('duration'))
            desc.append('Description:')
            desc.extend(spellbook[selected].get('desc').replace('<p>', 
                '    ').split('</p>'))
            if spellbook[selected].get('higher_level') is not None:
                desc.append('At Higher Levels:')
                desc.extend( spellbook[selected].get(
                            'higher_level').replace('<p>', '    ').split('</p>'))

            scroll=adddesc(desc, 
                resWin, resWiny-1, resWinx-1, 2, 1, scroll)

        addsugg(suggestions, selected, suggWin, suggWiny-1, suggWinx-1, 1, 1)

        searchWin.move(0, 8+i)
        searchWin.clrtoeol()
        searchWin.addstr(0, 8, ' '.join(searchterms))
        
        if debug:
            clearandborder(debugWin)
            debugWin.addstr(0, x-30, ' '+str(scroll)+' ')
            debugWin.addstr(0, x-25, ' '+str(i)+' ')
            debugWin.addstr(0, x-20, ' '+ch+' ')
            debugWin.addstr(0, 2, ' '.join(searchterms))
            debugWin.refresh()

        resWin.refresh()
        suggWin.refresh()
        searchWin.refresh()

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
    print(":".join("{:02x}".format(ord(c)) for c in ch))
    print(spellbook[selected]["name"])
    exit()

