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

import pygame
#import Numeric
import numpy
import time

from pygame.constants import *
from events import *

class EventManager:
    """this object is responsible for coordinating most communication
    between the Model, View, and Controller."""
    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()

    def registerListener(self, listener):
        self.listeners[listener] = 1

    def unregisterListener(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]
		
    def post(self, event):
        for listener in self.listeners.keys():
            #If the weakref has died, it will be autoremoved
            listener.notify(event)

class ConsoleKeyboardController:
    """..."""
    def __init__(self, eventManager):
        self.eventManager = eventManager
        self.eventManager.registerListener(self)

    def notify(self, ev):        
        if isinstance(ev, TickEvent):
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.eventManager.post(QuitEvent() )
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.eventManager.post(LeftButtonClickEvent(event.pos))
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        self.eventManager.post(LeftButtonUpEvent(event.pos))
                elif event.type == KEYDOWN:
                    print "Tecla ", event.key
                    self.eventManager.post(KeyCommandEvent(event.key))
            

class CPUSpinnerController:
    """..."""
    def __init__(self, eventManager):
        self.eventManager = eventManager
        self.eventManager.registerListener(self)
        self.keepGoing = True
        self.ticks = 0
        self.lastTime = 0

    def run(self, fast=True):
        while self.keepGoing:
            newTime = time.time()
            if self.lastTime < newTime or fast:
                self.ticks += 1
                event = TickEvent()
                self.lastTime = newTime
                self.eventManager.post(event)
        print self.ticks

    def notify(self, event):
        #print "Spinner!"
        if isinstance(event, QuitEvent):
        #this will stop the while loop from running
            self.keepGoing = False

class Display(object):
    def __init__(self, eventManager, rect):
        self.canvas = pygame.display.set_mode((rect.width, rect.height))
        self.eventManager = eventManager
        eventManager.registerListener(self)
        self.views = []

    def addView(self, view):
        self.views.append(view)

    def notify(self, evt):
        if isinstance(evt, UpdateRequest):
            self.canvas.fill((0, 0, 0))
            for view in self.views:
                view.draw(self.canvas)                
            pygame.display.update()


class View(object):
    def __init__(self, parent, rect):
        self.parent = parent
        if parent != None:
            parent.addView(self)
            self.setEventManager(parent.eventManager)
            self.rect = rect.move(parent.rect.left, parent.rect.top)
            self.rect = self.parent.rect.clip(self.rect)
        else:
            self.rect = rect
        self.views = []
        self.isVisible = False

    def addView(self, view):
        self.views.append(view)
        
    def draw(self, canvas):
        if self.isVisible:
            for view in self.views:
                view.draw(canvas)
        
    def move(self, x, y):
        self.rect.move_ip(x,y)
        if self.parent != None:
            self.rect = self.parent.rect.clip(self.rect)
        for view in self.views:
            view.move(x, y)
   
    def notify(self, evt):
        pass

    def setEventManager(self, eventManager):
        self.eventManager = eventManager
        eventManager.registerListener(self)

    def show(self, boolean):
        self.isVisible = boolean
        

class Window(View):
    def __init__(self, parent, rect, color):
        View.__init__(self, parent, rect)
        self.color = color    
    
    def draw(self, canvas):
        if self.isVisible:
            if self.parent != None:
                canvas.fill(self.color, self.parent.rect.clip(self.rect))
            else:
                canvas.fill(self.color, self.rect)
            for view in self.views:
                view.draw(canvas)
    
class Label(View):
    def __init__(self, parent, rect, text, font, color, size):
        View.__init__(self, parent, rect)
        self.text = text
        self.fontSize= size
        self.fontName = font
        self.font = pygame.font.Font(pygame.font.match_font(font), size)
        self.color = color
        self.imgText = self.font.render(text, True, self.color)
        self.rect = self.imgText.get_rect()
        self.rect.move_ip(parent.rect.left + rect.left, parent.rect.top + rect.top)
        self.rect = self.parent.rect.clip(self.rect)
    
    def draw(self, canvas):
        if self.isVisible:
            if self.parent != None:
                canvas.blit(self.imgText, (self.rect.left, self.rect.top), (0,0, self.rect.width, self.rect.height))
            else:
                canvas.blit(self.imgText, (self.rect.left, self.rect.top))
            for view in self.views:
                view.draw(canvas)

    def setColor(self, color):
        self.color = color
                
    def setText(self, text):
        self.text = text
        self.imgText = self.font.render(text, True, self.color)
        oldRect = self.rect
        self.rect = self.imgText.get_rect()
        self.rect = self.parent.rect.clip(self.rect)
        self.rect.move_ip(oldRect.left, oldRect.top)


class Image(View):
    def __init__(self, parent, rect, surface):
        View.__init__(self, parent, rect)
        self.surface = surface
        self.rect = self.surface.get_rect()
        self.rect.move_ip(parent.rect.left + rect.left, parent.rect.top + rect.top)
        self.rect = self.parent.rect.clip(self.rect)
    
    def draw(self, canvas):
        if self.isVisible:
            if self.parent != None:
                canvas.blit(self.surface, (self.rect.left, self.rect.top), (0,0, self.rect.width, self.rect.height))
            else:
                canvas.blit(self.surface, (self.rect.left, self.rect.top))
            for view in self.views:
                view.draw(canvas)

    def setSurface(self, surface):
        self.surface = surface

class GlowingImage(Image):
    def __init__(self, parent, rect, surface, alphaVelocity):
        Image.__init__(self, parent, rect, surface)
        self.alpha = 0
        self.alphaVelocity = alphaVelocity
        self.alphaIncreasing = True
                    
    def notify(self, evt):
        if isinstance(evt, TickEvent):
            if self.alphaIncreasing:
                self.alpha += self.alphaVelocity
                if self.alpha > 255:
                    self.alpha = 255
                    self.alphaIncreasing = False               
            else:
                self.alpha -= self.alphaVelocity
                if self.alpha < 0:
                    self.alpha = 0
                    self.alphaIncreasing = True
            self.img.set_alpha(self.alpha)
            self.eventManager.post(UpdateRequest())

class ImageButton(View):
    def __init__(self, parent, rect, imgUp, imgDown):
        View.__init__(self, parent, rect)
        self.isDown = False
        self.imgUp = imgUp
        self.imgDown = imgDown
        self.rect = self.imgUp.get_rect()
        self.rect.move_ip(parent.rect.left + rect.left, parent.rect.top + rect.top)
        self.rect = self.parent.rect.clip(self.rect)
    
    def draw(self, canvas):
        if self.isVisible:
            if self.isDown:
                img = self.imgDown  
            else:
                img = self.imgUp
            img.unlock()
            if self.parent != None:
                canvas.blit(img, (self.rect.left, self.rect.top), (0,0, self.rect.width, self.rect.height))
            else:
                canvas.blit(img, (self.rect.left, self.rect.top))
            for view in self.views:
                view.draw(canvas)
                
    def notify(self, evt):
        if isinstance(evt, LeftButtonClickEvent):
            if self.rect.collidepoint(evt.pos):
                self.isDown = True
                self.eventManager.post(UpdateRequest())
                self.eventManager.post(MouseCommandEvent(self))
        if isinstance(evt, LeftButtonUpEvent):
                self.isDown = False
                self.eventManager.post(UpdateRequest())

class TextButton(ImageButton):
    def __init__(self, parent, rect, text):
        self.text = text
        self.isDown = False
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 14)
        imgUp = self.font.render(text, True, (0, 0, 0), (250, 250, 250))
        imgDown = self.font.render(text, True, (255, 255, 255), (192, 192, 192))
        ImageButton.__init__(self, parent, rect, imgUp, imgDown)

class GlowingButton(ImageButton):
    def __init__(self, parent, rect, imgUp, imgDown, alphaVelocity, hasAlpha = False):
        self.alpha = 0
        self.hasAlpha = hasAlpha
        self.alphaVelocity = alphaVelocity
        self.alphaIncreasing = True
        self.buffer = imgUp.copy()
        ImageButton.__init__(self, parent, rect, imgUp, imgDown)


    def notify(self, evt):
        if isinstance(evt, TickEvent):
            self.imgUp = self.buffer.copy()
            if self.alphaIncreasing:
                self.alpha += self.alphaVelocity
                if self.alpha > 255:
                    self.alpha = 255
                    self.alphaIncreasing = False               
            else:
                self.alpha -= self.alphaVelocity
                if self.alpha < 0:
                    self.alpha = 0
                    self.alphaIncreasing = True
            if self.hasAlpha:
                alpha = pygame.surfarray.pixels_alpha(self.imgUp)
                multAlpha = alpha * self.alpha
                multAlpha >>= 8
                alpha[:] = multAlpha.astype(Numeric.UInt8)
            else:                    
                self.imgUp.set_alpha(self.alpha)
            self.eventManager.post(UpdateRequest())
        else:
            ImageButton.notify(self, evt)

                
class MovingWindow(Window):
    def __init__(self, parent, rect, color, xAxisVelocity, yAxisVelocity):
        Window.__init__(self, parent, rect, color)
        self.xAxisVelocity = xAxisVelocity
        self.yAxisVelocity = yAxisVelocity

    def notify(self, evt):
        if isinstance(evt, TickEvent):
            self.move(self.xAxisVelocity, self.yAxisVelocity)
            self.eventManager.post(UpdateRequest())

class App(object):
    def __init__(self):
        pygame.init()
        self.eventManager = EventManager()
        self.eventManager.registerListener(self)
        self.spinner = CPUSpinnerController(self.eventManager)
        self.keyboard = ConsoleKeyboardController(self.eventManager)
        self.display = None
        self.onInit()
        pass

    def onInit(self):
        pass

    def run(self):
        self.spinner.run()

    def notify(self, event):
        pass

    
def main():
    """..."""
    test = Test()
    test.run(fast = True)
	
if __name__ == "__main__":
    main()					
