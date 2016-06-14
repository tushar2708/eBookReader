#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import os
import sys
import decimal
import pygame
import Summarize
from optparse import OptionParser
from books import *
from toolkit import *
from toolkit.events import *
from pygame.locals import *
import textrect as tx

class DefaultOptions(object):
    def __init__(self):
        self.textWidth = 300
        self.textHeight = 451
        self.leftMarginWidth = 50
        self.topMarginHeight = 50
        self.fontHeight = 22
        self.FGCOLOR = 0, 0, 0
        self.BGCOLOR = 255,255,250
        self.pageNumberTop = 500
        self.fullscreenScreenrect = Rect(0, 0, 1024, 768)
        self.uperHalfScreenrect = Rect(0, 0, 500, 200)
        self.lowerHalfScreenrect = Rect(0, 200, 400, 400)
        self.summary = Rect(5, 260, 390, 300)
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
        self.windowCaption = "QuadReader v 0.01"
        self.coverImage = "cover.png"
        self.bookshelfImage = "bscover.png"
        self.bookshelfPath = "bookshelf"
        self.showPaginatingMsg = True
        self.twoPageView = True
        self.pageIncrement = 1
        self.lastBookRead = 0
        self.skin = 'skin/default/'
        self.copyrightNotice = "Nothing decided yet"
        
        self.bookThumbContainerW = 100
        self.bookThumbContainerH = 150
        
        self.bookThumbMargin = 25;
        self.bookThumbW = 40;
        self.bookThumbH = 60;
        
        self.bookThumbTitleH = 50
        self.bookThumbAuthorH = 30;
        
class Reader(widgets.App):
    STATE_LOADING = 0
    STATE_BOOK_SHELF = 1
    STATE_SELECTING = 2
    STATE_SUMMARY = 3
    STATE_READING = 4
    
    def __init__(self):
        widgets.App.__init__(self)

    def onInit(self):
        self.bookshelf = []
        #self.currentBook = args[1]
        self.state = self.STATE_BOOK_SHELF
        self.options = DefaultOptions()
        self.parseCommandLine()
        self.loadPrefs()
        self.readIni()
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

        self.eventManager.post(FinishedLoadingEvent())

    def onClick_Loading(self):
        pass
        #self.statusLabel.setText(u"Me han clicao!")
        
    def parseCommandLine(self):
        parser = OptionParser()
        parser.add_option("-f", "--file", dest="filename", help="write report to FILE", metavar="FILE")
        parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
        (options, args) = parser.parse_args()
        
    def initOptions(self, fontHeight = -1):
        
        if (fontHeight == -1):
            fontHeight = self.options.fontHeight
        else:
            self.options.fontHeight = fontHeight
            
        options = self.options        
        if options.winstyle == FULLSCREEN:           
            options.screenrect = options.fullscreenScreenrect
            options.imgPageWidth = options.textWidth + (2*options.leftMarginWidth)
            options.imgPageHeight = options.textHeight + (2*options.topMarginHeight)
            options.pageNumberTop = options.textHeight + options.topMarginHeight + int((options.topMarginHeight-fontHeight)/2)
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
            options.pageNumberTop = options.textHeight + options.topMarginHeight + int((options.topMarginHeight-fontHeight)/2)
            options.screenrect = Rect(0, 0, options.imgPageWidth, options.imgPageHeight)
            options.firstPagePos = (0,0)
            pygame.mouse.set_visible(True)

        options.font = pygame.font.Font(pygame.font.match_font(options.normalFont), fontHeight)        
        options.cfont = pygame.font.Font(pygame.font.match_font(options.decorFont), fontHeight-2)     
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
                (filepath, title, author, date, lastPageRead, lastFontSize) = line.strip().split(";")
                book = Book(filepath, title, author, date, lastPageRead, lastFontSize)
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
        print "pageNumber", pageNumber
        totalPages = len(book.pages)
        print "totalPages", totalPages
        page = book.pages[pageNumber]
        size = (options.imgPageWidth,options.imgPageHeight)
        imgPage = pygame.Surface(size, SRCALPHA, 32)
        imgPage.fill(options.BGCOLOR)
        #imgPageNumber.fill(options.BGCOLOR)
        #imgPage.blit(imgPageNumber, (int((options.imgPageWidth-imgPageNumber.get_width())/2), options.pageNumberTop))
        imgText = self.renderText(page)
        progress = (int(pageNumber)+1)/int(totalPages)
        remaining_time = book.timeToRead*(1-progress)
        remaining_time = round(remaining_time,2)
        print "progress", progress
        print "remaining_time", remaining_time
        imgPageNumber = options.cfont.render(str(pageNumber+1) + "/" + str(len(book.pages)) + " : " + str(remaining_time) + " min remaining", 1, options.FGCOLOR, options.BGCOLOR)
        imgTitle = options.cfont.render(book.title, 1, options.FGCOLOR, options.BGCOLOR)
        imgPage.blit(imgText, (options.leftMarginWidth, options.topMarginHeight))
        
        '''
        if (progress <= 0.33):
            color = (255,60,50)
        elif (0.33 < progress <= 0.66):
            color = (255,215,50)
        else:
            color = (50,205,50)
        '''
        
        color = ((1-progress)*255,progress*255,50)
        
        pygame.draw.rect(imgPage, (128,128,128), pygame.Rect(15,options.pageNumberTop-1,(options.imgPageWidth-30),10), 1)
        pygame.draw.rect(imgPage, color, pygame.Rect(15,options.pageNumberTop-1,(options.imgPageWidth-30)*(progress),10))
        
        imgPage.blit(imgPageNumber, (int((options.imgPageWidth-imgPageNumber.get_width())/2), options.pageNumberTop+12))
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
        bookPath = options.bookshelfPath +'/' + book.filepath + '/' + "text.txt"
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
                    if currentLine+1 >= maxlinenumber:
                        currentPage += 1
                        book.pages.append(Page())				
                        book.pages[currentPage].lines.append(Line())
                        #print "page", currentPage+1		
                        currentLine = 0 #reset lines
                        currentHeight = 0
                    else:
                        book.pages[currentPage].lines.append(Line())
                #print "current page is %s " %currentPage
                #print "currentLine is %s" %currentLine         
                book.pages[currentPage].lines[currentLine].words.append(word)
            book.lastpage = currentPage
        book.isPaginated = True                

    def saveIni(self):
        fo = open(self.options.inifilepath, 'w')
        print "Log the progress in " + self.options.inifilepath
        for book in self.bookshelf:
            print book
            line = ";".join([book.filepath, book.title, book.author, book.date, str(book.lastpageread), str(book.lastFontSize)])+ "\n"
            fo.write(line)
        fo.close()

    def showBook(self):
        book = self.bookshelf[self.bookNumber]
        self.initOptions(book.lastFontSize)
        self.statusLabel.setText(u"Paginating book...")
        self.eventManager.post(UpdateRequest())
        self.paginateBook(book)
        self.statusLabel.setText(u"Finished Paginating.")
        self.eventManager.post(UpdateRequest())
        
        print "calculting page number ... book.lastpageread is %s ....book.pages is %s" %(book.lastpageread, len(book.pages))
        self.pageNumber = int(book.lastpageread) % len(book.pages)
        #self.pageNumber = int(book.lastpageread)                    
        self.page = self.renderPage()
        self.image.setSurface(self.page)
        #self.lTitle.show(False)
        #self.lAuthor.show(False)
        self.statusLabel.show(False)
        self.eventManager.post(UpdateRequest())

        self.end = False
        self.exitNow = False
        self.state = self.STATE_READING

    def showBookDetails(self, screen, options):
        self.bookNumber = self.index
        print "index", self.index
        book = self.bookshelf[self.bookNumber]
        
        self.font = pygame.font.SysFont('Arial', 15)
        
        rendered_title = tx.render_textrect("\'" + book.title + "\' by \'" + book.author +"\'", self.font, Rect(20, 200, 400, 400), (255, 255, 255), (48, 48, 48), 0)
        screen.blit(rendered_title, options.lowerHalfScreenrect.topleft)
        

        (self.summary, timeToRead) = Summarize.main(options.bookshelfPath +'/' + book.filepath + '/' + "text.txt", 20)
        book.timeToRead = round(timeToRead,2)
        self.summary = self.summary[:650] + "..."
        print "*summary*", self.summary, " : ", "*timeToRead*", book.timeToRead
        
        screen.blit(self.font.render("Estimated time to read : " + str(book.timeToRead) + " min", True, (250,150,150)), (0, 220))
        
        rendered_sumtitle = tx.render_textrect("Summary :", self.font, Rect(20, 240, 400, 400), (48, 48, 48), (200, 200, 200), 0)
        screen.blit(rendered_sumtitle, (0, 240))
        
        rendered_summary = tx.render_textrect(self.summary, self.font, options.summary, (60, 60, 60), (230, 230, 230), 0)
        
        if rendered_summary:
            screen.blit(rendered_summary, options.summary.topleft)

        #screen.blit(self.font.render(summary, True, (255,0,0)), (40, 200))
        pygame.display.flip()

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
        elif self.state == self.STATE_BOOK_SHELF:
            print "Book Shelf..."
            screen = self.initDisplay()
            summaryText = pygame.Surface((500, 300))
            
            screen.fill(options.BGCOLOR)
            pygame.draw.rect(screen, (150, 150, 150), options.uperHalfScreenrect)
            pygame.draw.rect(screen, (100, 100, 100), options.lowerHalfScreenrect)
            
            #self.bookNumber = -1
            for bookNo in range(3):
                book = self.bookshelf[bookNo]
                print book.author
                color = (255,255,255);
                book_cover = pygame.image.load(options.bookshelfPath +'/' + book.filepath + '/' + "cover.jpg").convert()
                book_cover_rect = book_cover.get_rect()
                book_cover = pygame.transform.scale(book_cover, (options.bookThumbContainerW, options.bookThumbContainerH))
                book_cover_rect.x = options.bookThumbMargin + (options.bookThumbContainerW + options.bookThumbMargin)*bookNo
                book_cover_rect.y = options.bookThumbMargin
                book_cover_rect.width = options.bookThumbContainerW
                book_cover_rect.height = options.bookThumbContainerH
                
                #screen.blit(button,(300,200))
                #book_cover = pygame.image.load(spaceship).convert_alpha()
                #pygame.draw.rect(screen, color, [options.bookThumbMargin + (options.bookThumbContainerW + options.bookThumbMargin)*bookNo, options.bookThumbMargin, options.bookThumbContainerW, options.bookThumbContainerH])
                screen.blit(book_cover, book_cover_rect)
                pygame.display.flip();
                
            if isinstance(event, KeyCommandEvent):
                self.index = event.key - pygame.K_1
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3): 
                    self.showBookDetails(screen, options)
                    #imgSummary = options.cfont.render(summary, 1, options.FGCOLOR, options.BGCOLOR)
                    #screen.blit(imgSummary, (int((options.imgPageWidth - imgSummary.get_width())/2),15))
                    #self.lTitle = widgets.Label(self.mainFrame, pygame.Rect(20, 310,0,0), self.bookshelf[self.bookNumber].title, options.normalFont, (234,234,234), 20)
                    #self.Summary = widgets.Label(self.mainFrame, pygame.Rect(20, 220, 0, 0), summary, options.normalFont, (234,234,234), 20)
                    #self.Summary.show(True)
                    #self.eventManager.post(UpdateRequest())
                print "key", event.key
                if event.key == 13:
                    print "number", self.bookNumber
                    if self.bookNumber in (0, 1, 2):
                        self.showBook()
                        #return
                        #self.state = self.STATE_SELECTING
                    else:
                        print "boom"
            
        elif self.state == self.STATE_LOADING:
            print "Loading"
            self.bookNumber = self.options.lastBookRead
            self.image.setSurface(pygame.image.load(self.options.skin + '/' + options.bookshelfImage))
            self.statusLabel.setText(u"")
            self.image.show(True)
            self.lTitle = widgets.Label(self.mainFrame, pygame.Rect(20, 310,0,0), self.bookshelf[self.bookNumber].title, options.normalFont, (234,234,234), 20)
            self.lAuthor = widgets.Label(self.mainFrame, pygame.Rect(60, 310+options.lineHeight,0,0), self.bookshelf[self.bookNumber].author, options.normalFont, (234,234,234), 20)
            self.lTitle.show(True)
            self.lAuthor.show(True)
            self.eventManager.post(UpdateRequest())
            print self.display.views
            #self.state = self.STATE_SELECTING
            self.state = self.STATE_BOOK_SHELF; # Temporary
            
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
        elif self.state == self.STATE_READING:
            print "Reading"
            if isinstance(event, KeyCommandEvent):
                book = self.bookshelf[self.bookNumber]
                pageNumber = self.pageNumber
                book.lastpageread = pageNumber
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
                elif event.key == 273:  # Up key
                    book.lastFontSize += 2
                    self.saveIni()
                    self.showBook()
                elif event.key == 274:  # Down key
                    book.lastFontSize -= 2
                    self.saveIni()
                    self.showBook()
                elif event.key == K_t:
                    options.twoPageView = not options.twoPageView
                    if options.twoPageView:
                        if pageNumber % 2 != 0:
                            pageNumber -= 1               
                        options.pageIncrement = 2
                    else:
                        options.pageIncrement = 1
                    screen = self.initDisplay()
                    screen.fill(options.BGCOLOR)  
                elif event.key == K_f: #F key
                    if options.winstyle == FULLSCREEN:
                        options.winstyle = 0
                    else:
                        options.winstyle = FULLSCREEN
                        options.twoPageView = False
                        options.pageIncrement = 1
                    screen = self.initDisplay()
                elif event.key == pygame.K_TAB:
                    self.saveIni()
                    self.state = self.STATE_BOOK_SHELF

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
                    



def main(args):
    """..."""
    pygame.mixer.quit()
    test = Reader()
    test.run()


if __name__ == "__main__":
    main(sys.argv)
