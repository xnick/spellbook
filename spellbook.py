#!/bin/env python3


import sys
import curses
import string
import textwrap
import traceback

from model import *
from programState import *
from exceptions import *


def addsugg(spellnames, selected, screen, maxy, maxx, posy, posx):
    lineno=posy
    colno=posx
    for spell in spellnames:
        if colno>=maxx-len(spell):
            colno=posx
            lineno+=1
        if colno>=maxx-len(spell): #still
            raise NotEnoughColumnsException()
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

def prepareDescription(spell):
    desc=[]
    desc.append(spell.get('level')+
            " "+spell.get('school')+' ('+
            spell.get('class')+')')
    desc.append('Range: '+spell.get('range'))
    desc.append('Casting Time: '+spell.get('casting_time'))
    desc.append('Duration: '+spell.get('duration'))
    desc.append('Description:')
    desc.extend(spell.get('desc').replace('<p>', '    ').split('</p>'))
    if spell.get('higher_level') is not None:
        desc.append('At Higher Levels:')
        desc.extend( spell.get(
                    'higher_level').replace('<p>', '    ').split('</p>'))
    return desc

def adddesc(desc, screen, maxy, maxx, posy, posx, scroll):
    lineno=posy
    colno=posx
    lines=[]
    if maxy<=3:
        raise NotEnoughRowsException()
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



if __name__ == "__main__":
    debug=False
    
    data=Model()
    windows=ProgramState(debug)

    inp=""
    selected=''
    selectionno=0
    scroll=0
    init=False
    dosearch=True
    try:
        while(True):
            windows.setSearch()
            if not init:
                ch='\x17' # piggy-back
                init=True
            else:
                ch=windows.getInput()
            windows.stdscr.border()
            if ch in ['KEY_RESIZE', 'KEY_ESCAPE', '\x1b']:
                windows.resize()
                dosearch=True
            elif ch in ['KEY_BACKSPACE', '\b', '\x7f']:
                if windows.index>0:
                    windows.index-=1
                dosearch=True
            elif ch in ['^W', '\x17']:
                windows.eraseWord()
                if windows.index<0:
                    windows.index=0
                dosearch=True
            elif ch in ['KEY_ENTER', '\n']:
                # Also make this enter fullscreen mode
                windows.fullscreen()
                # windows.index=len(selected)
                # windows.searchWin.win.addstr(0, 8, selected)
                # dosearch=True
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
                    scroll+=windows.resWin.y-1
                elif ch=='KEY_PPAGE':
                    scroll-=windows.resWin.y-1
                    if scroll<0:
                        scroll=0
            elif ch in ['KEY_END', 'KEY_HOME']:
                if ch=='KEY_END':
                    scroll+=999999#Sup
                elif ch=='KEY_HOME':
                    scroll=0
            elif ch in string.printable:
                if windows.index<windows.searchWin.x-10:
                    windows.index+=1
                dosearch=True
            else:
                raise Exception("What was that?")

            if dosearch:
                searchterms=windows.getInputString().lower().split(' ')
                spells=data.search(searchterms)
                dosearch=False

            windows.suggWin.clearAndBorder()
            suggestions=[spell['name'] for spell in spells]
            if not selected or (selected not in suggestions and len(suggestions)):
                selected=suggestions[0]
                selectionno=0
                scroll=0

            if selected in suggestions:
                selectionno=suggestions.index(selected)
            elif len(suggestions):
                selected=suggestions[0]
                selectionno=0

            windows.resWin.clearAndBorder()
            windows.resWin.win.addstr(1,1,selected)

            desc=prepareDescription(data.spelllist[selected])
            
            try:
                scroll=adddesc(desc, 
                    windows.resWin.win, windows.resWin.y-1, 
                    windows.resWin.x-1, 2, 1, scroll)
            except NotEnoughRowsException:
                print("Not enough rows, please resize your terminal")

            windows.suggWin.clearAndBorder()
            try:
                addsugg(suggestions, selected, windows.suggWin.win,
                        windows.suggWin.y-1, windows.suggWin.x-1, 1, 1)
            except NotEnoughColumnsException:
                print("Not enough columns, please resize your terminal")

            windows.searchWin.win.move(0, 8+windows.index)
            windows.searchWin.win.clrtoeol()
            windows.searchWin.win.addstr(0, 8, ' '.join(searchterms))
            
            if debug:
                windows.debugWin.clearAndBorder()
                windows.debugWin.win.addstr(0, windows.x-30, ' '+str(scroll)+' ')
                windows.debugWin.win.addstr(0, windows.x-25, ' '+str(windows.index)+' ')
                #windows.debugWin.win.addstr(0, windows.x-20, ' '+ch+' ')
                windows.debugWin.win.addstr(0, 2, ' '.join(searchterms))
                windows.debugWin.win.refresh()
            windows.refresh()

    except KeyboardInterrupt as e:
        curses.nocbreak()
        windows.stdscr.keypad(False)
        curses.endwin()
        traceback.print_exc()
        print(ch)
        exit()

    except Exception as e:
        curses.nocbreak()
        windows.stdscr.keypad(False)
        curses.endwin()
        traceback.print_exc()
        print(ch)
        print(":".join("{:02x}".format(ord(c)) for c in ch))
        print(data.spelllist[selected]["name"])
        exit()

