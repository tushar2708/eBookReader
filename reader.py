#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Python EBook Reader.
#
# Python EBook Reader is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Python EBook Reader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Python EBook Reader; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


#Program:	"pythonebookreader"
#Version: 0.01
#File:        "reader.py"
#Date:		26-01-2006 [25-06-2003]
#Revision: 0.01
#Author:	willemsh

from __future__ import division
import sys
import pygame
from optparse import OptionParser
from books import *
from toolkit import *
from toolkit.events import *
from pygame.locals import *

class DefaultOptions(object):
    def __init__(self):
        self.textWidth = 300
        self.textHeight = 451
        self.leftMarginWidth = 50
        self.topMarginHeight = 50
        self.fontHeight = 18
        self.FGCOLOR = 0, 0, 0
        self.BGCOLOR = 255,255,250
        self.pageNumberTop = 500
        self.fullscreenScreenrect = Rect(0, 0, 1024, 768)
        #self.winstyle = FULLSCREEN
        self.winstyle = 0
        self.normalFont = 'berling.ttf'
        self.normalFont = 'berling antiqua'
        
        self.decorFont = 'clr.ttf'
        self.decorFont = 'Classic Regular'
        #self.cfontName = "Harrington"
        self.spaceWidth = 0
        self.lineHeight = 0
        self.configFilePath = "reader.ini"
        self.inifilepath = "bookshelf.ini"
        self.windowCaption = "pythonebookreader v 0.01"
        self.coverImage = "cover.png"
        self.bookshelfImage = "bscover.png"
        self.bookshelfPath = "bookshelf"
        self.showPaginatingMsg = True
        self.twoPageView = True
        self.pageIncrement = 1
        self.lastBookRead = 0
        self.skin = 'skin/default'
        self.copyrightNotice = "Python EBook Reader version 0.01, Copyright (C) 2003-2006 of author\nPython EBook Reader comes with ABSOLUTELY NO WARRANTY; for details\ntype `show w'.  This is free software, and you are welcome\nto redistribute it under certain conditions; type `show c' \nfor details."
        
class Reader(widgets.App):
    STATE_LOADING = 0
    STATE_SELECTING = 1
    STATE_READING = 2
    def __init__(self, args):
        widgets.App.__init__(self, args)

    def onInit(self, args):
        self.bookshelf = []
        self.currentBook = args[1]
        self.state = self.STATE_LOADING
        self.options = DefaultOptions()
        self.parseCommandLine()
        self.initOptions()
        self.display = widgets.Display(self.eventManager, self.options.screenrect)
        self.display.canvas = self.initDisplay()
        self.mainFrame = widgets.Window(None, self.options.screenrect, (122,122,122))
        self.mainFrame.setEventManager(self.eventManager)
        self.mainFrame.show(True)
        self.image = widgets.Image(self.mainFrame, pygame.Rect(0,0,0,0), pygame.image.load(self.options.skin + '/' + self.options.coverImage))
        #self.button = widgets.GlowingButton(self.mainFrame, pygame.Rect(0,0,0,0), pygame.image.load('d1.png'), pygame.image.load('d2.png'), 4, hasAlpha=True)
        
        self.statusLabel = widgets.Label(self.mainFrame, pygame.Rect(15,513,0,0), u"Loading...", pygame.font.get_default_font(), (192,192,192), 16)
        
        self.image.show(True)
        self.statusLabel.show(True)
        self.display.addView(self.mainFrame)
        self.eventManager.post(UpdateRequest())
        
        self.loadPrefs()
        self.readIni()

        self.eventManager.post(FinishedLoadingEvent())

    def onClick_Loading(self):
        pass
        #self.statusLabel.setText(u"Me han clicao!")
        
    def parseCommandLine(self):
        parser = OptionParser()
        parser.add_option("-f", "--file", dest="filename", help="write report to FILE", metavar="FILE")
        parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
        (options, args) = parser.parse_args()
        
    def initOptions(self):
        options = self.options
        if options.winstyle == FULLSCREEN:           
            options.screenrect = options.fullscreenScreenrect
            options.imgPageWidth = options.textWidth + (2*options.leftMarginWidth)
            options.imgPageHeight = options.textHeight + (2*options.topMarginHeight)
            options.pageNumberTop = options.textHeight + options.topMarginHeight + int((options.topMarginHeight-options.fontHeight)/2)
            left = int( ( options.screenrect.width - ( options.textWidth + ( 2*options.leftMarginWidth ) ) )/2 )
            top = int( (options.screenrect.height-(options.textHeight+(2*options.topMarginHeight)))/2 )
            options.firstPagePos = (left, top)
            if options.twoPageView:
                left = int( ( options.screenrect.width - ( (2*options.textWidth) + ( 4*options.leftMarginWidth ) ) )/2 )
                options.firstPagePos = (left, top)
                options.secondPagePos = (left + options.imgPageWidth + 2, top)
            pygame.mouse.set_visible(False)
        else:       
            options.imgPageWidth = options.textWidth + (2*options.leftMarginWidth)
            options.imgPageHeight = options.textHeight + (2*options.topMarginHeight)
            options.pageNumberTop = options.textHeight + options.topMarginHeight + int((options.topMarginHeight-options.fontHeight)/2)
            options.screenrect = Rect(0, 0, options.imgPageWidth, options.imgPageHeight)
            options.firstPagePos = (0,0)
            pygame.mouse.set_visible(True)

        options.font = pygame.font.Font(pygame.font.match_font(options.normalFont), options.fontHeight)        
        options.cfont = pygame.font.Font(pygame.font.match_font(options.decorFont), options.fontHeight-2)     
        options.defaultfont = pygame.font.Font(pygame.font.get_default_font(), 20)
        options.spaceWidth = options.font.size(" ")[0]
        options.lineHeight = options.font.size(" ")[1]

    def initDisplay(self):
        bestdepth = pygame.display.mode_ok(self.options.screenrect.size, self.options.winstyle, 32)
        screen = pygame.display.set_mode(self.options.screenrect.size, self.options.winstyle, bestdepth)
        pygame.display.set_caption(self.options.windowCaption)
        pygame.display.set_icon(pygame.image.load(self.options.skin + '/' + 'livre.png'))
        return screen

    def readIni(self):
        #load ini file    
        fi = open(self.options.inifilepath, 'r')
        lines = fi.readlines()
        fi.close()
        for line in lines:
            if line.strip() != "":
                (filepath, title, author, date, lastPageRead) = line.strip().split(";")
                book = Book(filepath, title, author, date, lastPageRead)
                self.bookshelf.append(book)
        print self.bookshelf

    def renderLine(self, line):
        #print "Rendering:", line.words
        options = self.options
        imgLine = pygame.Surface((options.textWidth, options.lineHeight))
        imgLine.fill(options.BGCOLOR)
        if line.justified:
            wordsSize = options.font.size("".join(line.words))[0]
            spaceWidth = options.textWidth - options.font.size("".join(line.words))[0]
            totalSpaces = len(line.words) - 1            
            if totalSpaces == 0:
                spacewpw = 0
            else:
                spacewpw = spaceWidth/totalSpaces
            spaceLeft = spaceWidth - (spacewpw*(len(line.words)-1))
            pos = 0
            count = -1
            for word in line.words:
                count += 1
                if count == (len(line.words)-1):
                    pos = options.textWidth - options.font.size(word)[0]
                imgLine.blit(options.font.render(word, 1, options.FGCOLOR, options.BGCOLOR), (int(pos), 0))
                pos = pos + options.font.size(word)[0] + spacewpw
        else:
            imgLine.blit(options.font.render(" ".join(line.words), 1, options.FGCOLOR, options.BGCOLOR), (0, 0))
        return imgLine 
            

    def renderText(self, page):
        options = self.options
        imgText = pygame.Surface((options.textWidth, options.textHeight))
        imgText.fill(options.BGCOLOR) 
        currentHeight = 0
        for line in page.lines:
            imgText.blit(self.renderLine(line), (0, currentHeight))
            currentHeight += options.lineHeight
        return imgText
                

    def renderPage(self):
        options = self.options
        book = self.bookshelf[self.bookNumber]
        pageNumber = self.pageNumber
        totalPages = len(book.pages)
        page = book.pages[pageNumber]
        size = (options.imgPageWidth,options.imgPageHeight)
        imgPage = pygame.Surface(size, SRCALPHA, 32)
        imgPage.fill(options.BGCOLOR)
        #imgPageNumber.fill(options.BGCOLOR)
        #imgPage.blit(imgPageNumber, (int((options.imgPageWidth-imgPageNumber.get_width())/2), options.pageNumberTop))
        imgText = self.renderText(page)
        imgPageNumber = options.cfont.render(str(pageNumber+1) + "/" + str(len(book.pages)), 1, options.FGCOLOR, options.BGCOLOR)
        imgTitle = options.cfont.render(book.title, 1, options.FGCOLOR, options.BGCOLOR)
        imgPage.blit(imgText, (options.leftMarginWidth, options.topMarginHeight))
        progress = (int(pageNumber)+1)/int(totalPages)
        print "progress", progress
        pygame.draw.rect(imgPage, (128,128,128), pygame.Rect(15,options.pageNumberTop-1,(options.imgPageWidth-30),15), 1)
        pygame.draw.rect(imgPage, (0,0,0), pygame.Rect(15,options.pageNumberTop-1,(options.imgPageWidth-30)*(progress),15))
        imgPage.blit(imgPageNumber, (int((options.imgPageWidth-imgPageNumber.get_width())/2), options.pageNumberTop))
        #imgPage.blit(imgPageNumber, (int((options.imgPageWidth-imgPageNumber.get_width())/2), options.pageNumberTop))	
        imgPage.blit(imgTitle, (int((options.imgPageWidth - imgTitle.get_width())/2),15))
        
        #pygame.image.save(imgPage, "t.bmp")
        return imgPage

            
    def loadPrefs(self):
        options = self.options
        fi = open(self.options.configFilePath, 'r')
        lines = fi.readlines()
        for line in lines:
            (key, value)=line.strip().split("=")
            if key == "titleFont":
                options.titleFont = str(value)
            if key == "bookFont":
                options.bookFont = str(value)
            if key == "lastBookRead":
                options.lastBookRead = int(value)
            if key == "fullscreen":
                options.fullscreen = bool(value)
            if key == "twoPageView":
                options.twoPageView = bool(value)
            if key == "bookshelfPath":
                options.bookshelfPath = str(value)
            print key, value
                
    def paginateBook(self, book):
        options = self.options
        bookPath = options.bookshelfPath +'/' + book.filepath
        print "bookPath", bookPath
        fi = open(bookPath, 'r')
        lines = fi.readlines()
        fi.close()    
        book.pages = []
        book.pages.append(Page())
        maxlinenumber = int(options.textHeight/options.lineHeight)
        #print maxlinenumber
        currentPage = 0
        currentLine = -1
        currentWidth = 0
        currentHeight = 0
        LineCount = 0
        lastPercent = 0
        for line in lines:        
            linewords = line.strip().split(" ")
            #if aheight+LINEHEIGHT > self.height: # new Page
            if currentLine +1 >= maxlinenumber:
                currentPage = currentPage + 1
                book.pages.append(Page())
                currentLine = -1
            book.pages[currentPage].lines.append(Line())
            currentLine += 1 
            currentWidth = 0
            lastLine = []
            for word in linewords:			
                #print word
                lastLine.append(word)
                #print lastLine
                lineSize = options.font.size(" ".join(lastLine))
                if  lineSize[0] > options.textWidth: #new Line                
                    lastLine = [word]
                    #print aline, self.pages[apage].lines[aline].words
                    book.pages[currentPage].lines[currentLine].justified = True
                    currentHeight = currentHeight + options.lineHeight
                    currentLine += 1
                    awidth = 0
                    #if aheight + 3*LINEHEIGHT > self.height: # new Page
                    if currentLine+1 > maxlinenumber:
                        currentPage += 1
                        book.pages.append(Page())				
                        book.pages[currentPage].lines.append(Line())
                        #print "page", currentPage+1		
                        currentLine = 0 #reset lines
                        currentHeight = 0
                    else:
                        book.pages[currentPage].lines.append(Line())
                book.pages[currentPage].lines[currentLine].words.append(word)
            book.lastpage = currentPage
        book.isPaginated = True                

    def saveIni(self):
        fo = open(self.options.inifilepath, 'w')
        for book in self.bookshelf:
            line = ";".join([book.filepath, book.title, book.author, book.date, str(book.lastpageread)])+ "\n"
            fo.write(line)
        fo.close()

    def notify(self, event):
        #print "Notify"
        options = self.options
        if isinstance(event, TickEvent):
            return
        elif isinstance(event, UpdateRequest):
            return
        elif isinstance(event, QuitEvent):
            #save and exit
            self.exitNow = True 
            #self.book.lastpageread = self.pageNumber 
            self.end = True
        elif self.state == self.STATE_LOADING:
            print "Loading"
            self.bookNumber = self.options.lastBookRead
            self.image.setSurface(pygame.image.load(self.options.skin + '/' + options.bookshelfImage))
            self.statusLabel.setText(u"")
            self.image.show(True)
            self.lTitle = widgets.Label(self.mainFrame, pygame.Rect(20, 310,0,0), self.bookshelf[self.bookNumber].title, options.normalFont, (234,234,234), 20)
            self.lAuthor = widgets.Label(self.mainFrame, pygame.Rect(60, 310+ options.lineHeight,0,0), self.bookshelf[self.bookNumber].author, options.normalFont, (234,234,234), 20)
            self.lTitle.show(True)
            self.lAuthor.show(True)
            self.eventManager.post(UpdateRequest())
            print self.display.views
            self.state = self.STATE_SELECTING
        elif self.state == self.STATE_READING:
            print "Reading"
            if isinstance(event, KeyCommandEvent):
                book = self.bookshelf[self.bookNumber]
                pageNumber = self.pageNumber
                if event.key == 278:
                    pageNumber = 0
                elif event.key == 279:
                    pageNumber = len(book.pages)-1
                    if options.twoPageView and pageNumber % 2 != 0:
                        pageNumber = pageNumber - 1   
                elif event.key == 275 or event.key == 281:
                    if pageNumber < (len(book.pages)-1):
                        pageNumber += options.pageIncrement 
                elif event.key == 276 or event.key == 280:
                    if pageNumber > 0:
                        pageNumber -= options.pageIncrement
                elif event.key == K_t:
                    options.twoPageView = not options.twoPageView
                    if options.twoPageView:
                        if pageNumber % 2 != 0:
                            pageNumber -= 1                            
                        options.pageIncrement = 2
                    else:
                        options.pageIncrement = 1
                    screen = self.initDisplay()
                    imgPage.fill(options.BGCOLOR)  
                elif event.key == K_f: #F key
                    if options.winstyle == FULLSCREEN:
                        options.winstyle = 0
                    else:
                        options.winstyle = FULLSCREEN
                        options.twoPageView = False
                        options.pageIncrement = 1
                    screen = self.initDisplay()

                if options.winstyle == FULLSCREEN and options.twoPageView:                       
                    pageNumber1 = self.pageNumber - 1
                    pageNumber2 = self.pageNumber
                    print pageNumber, pageNumber1, pageNumber2
                    if pageNumber1 >= 0:
                        self.page1 = self.renderPage(book, pageNumber1, imgPage, imgTitle, imgPageNumber, options)
                        screen.blit(imgPage, options.firstPagePos)
                    else:
                        imgPage.fill(options.BGCOLOR)
                        screen.blit(imgPage, options.firstPagePos)
                    if pageNumber2 < len(book.pages):
                        renderPage(book, pageNumber2, imgPage, imgTitle, imgPageNumber, options)
                        screen.blit(imgPage, options.secondPagePos)
                    else:
                        imgPage.fill(options.BGCOLOR)
                        screen.blit(imgPage, options.firstPagePos)
                    pygame.display.flip()
                    
                else:
                    self.pageNumber = pageNumber
                    self.page = self.renderPage()
                    self.image.setSurface(self.page)
                    self.eventManager.post(UpdateRequest())
                    
        elif self.state == self.STATE_SELECTING:
            print "Selecting"
            bookshelf = self.bookshelf
            book = self.bookshelf[self.bookNumber]
            if isinstance(event, KeyCommandEvent):                
                bookNumber = self.bookNumber
                if event.key == 275 or event.key == 281:
                        bookNumber = (bookNumber + 1) % len(bookshelf) 
                elif event.key == 276 or event.key == 280:
                        bookNumber = (bookNumber - 1) % len(bookshelf) 
                elif event.key == 13:
                    self.statusLabel.setText(u"Paginating book...")
                    self.eventManager.post(UpdateRequest())
                    self.paginateBook(book)
                    self.statusLabel.setText(u"Finished Paginating.")
                    self.eventManager.post(UpdateRequest())
                    self.pageNumber = int(book.lastpageread) % len(book.pages)                    
                    self.page = self.renderPage()
                    self.image.setSurface(self.page)
                    self.lTitle.show(False)
                    self.lAuthor.show(False)
                    self.statusLabel.show(False)
                    self.eventManager.post(UpdateRequest())

                    self.end = False
                    self.exitNow = False
                    self.state = self.STATE_READING
                    return
                self.bookNumber = bookNumber
                book = self.bookshelf[self.bookNumber]
                self.lTitle.setText(book.title)
                self.lAuthor.setText(book.author)
                self.eventManager.post(UpdateRequest()) 


def main(args):
    """..."""
    pygame.mixer.quit()
    test = Reader(args)
    test.run()


if __name__ == "__main__":
    main(sys.argv)
