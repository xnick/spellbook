import curses


class ProgramState:
    index=8
    def __init__(self, debug):
        self.debug=debug
        self.stdscr = curses.initscr()
        curses.cbreak()
        self.stdscr.border()
        self.stdscr.refresh()

        self.y=curses.LINES-1
        self.x=curses.COLS-1

        self.resWin=Window(min(int(self.y*0.8), self.y-5),self.x-1,1,1)
        self.resWin.win.border()

        if self.debug:
            self.debugWin=Window(1,self.x+1,self.y,0)
            self.debugWin.win.border()
        
        self.searchWin=Window(1,self.x-1,self.y-1,1)
        self.searchWin.win.keypad(True)

        self.suggWin=Window(self.y-self.resWin.y-self.searchWin.y-1,
                self.x-1,self.resWin.y+1,1)
        self.suggWin.win.border()
    
    def setSearch(self):
        self.searchWin.win.addstr(0,0,'Search: ')

    def getInput(self):
        return self.searchWin.win.getkey(0,8+self.index)

    def getInputString(self):
        return self.searchWin.win.instr(0, 8, self.index).decode("utf-8")
    
    def refresh(self):
        if self.debug:
            self.debugWin.refresh()

        self.resWin.win.refresh()
        self.suggWin.win.refresh()
        self.searchWin.win.refresh()
    
    def eraseWord(self):
        self.index=self.searchWin.win.instr(0,8,self.index).decode("utf-8").rfind(' ')
        self.searchWin.win.move(0, 8+self.index)

    def resize(self):
        curses.resize_term(*self.stdscr.getmaxyx())

        self.stdscr.refresh()

        self.y=curses.LINES-1
        self.x=curses.COLS-1

        self.resWin.y=min(int(self.y*0.8), self.y-5)
        self.resWin.x=self.x-1
        self.resWin.win.resize(self.resWin.y,self.resWin.x)
        self.resWin.win.border()
        
        if self.debug:
            self.debugWin.y=1
            self.debugWin.x=self.x+1
            self.debugWin.win.resize(self.debugWin.y,self.debugWin.x)
            self.debugWin.win.border()

        self.searchWin.y=1
        self.searchWin.x=self.x-1
        self.searchWin.win.resize(self.searchWin.y,self.searchWin.x)
        self.searchWin.win.mvwin(self.y-1,1)

        self.suggWin.y=self.y-self.resWin.y-self.searchWin.y-1
        self.suggWin.x=self.x-1
        self.suggWin.win.resize(self.suggWin.y,self.suggWin.x)
        self.suggWin.win.mvwin(self.resWin.y+1, 1)
        self.suggWin.win.border()


class Window:
    def __init__(self, y, x, my, mx):
        self.y=y
        self.x=x
        self.my=my
        self.mx=mx
        self.win=curses.newwin(y,x,my,mx)

    def clearAndBorder(self):
        self.win.move(0,0)
        self.win.clrtobot()
        self.win.border()





