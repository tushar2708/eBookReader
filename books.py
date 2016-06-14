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
#File:        "books.py"; basic data classes for books
#Date:		29-01-2006 [27-06-2003]
#Revision: 0.01
#Author:	willemsh

#It would be too much work create a XHTML renderer from scratch, better
#look for an embeded solution. Anyway this would the base class.

class Glyph:
    def __init__(self):
	pass					

class Word: #Not needed as there is no suport for color or fontsizes
    def __init__(self):
        pass

class Line:
    def __init__(self):
	self.justified = False
	self.words = []

#This would have been a generic class container for glyphs: letters, 
#images, other blocks, pages themselves would have been blocks
class Block:
    def __init__(self):
	pass

class Page:
    def __init__(self):
        self.lines = []	

class Book:
    def __init__(self, filepath, title, author, date, lastpageread, lastFontSize, width=300, height=400):
        self.title = title
        self.author = author
        self.date = date
        self.lastpageread= int(lastpageread)
        self.lastFontSize = int(lastFontSize)
        self.filepath = filepath
        self.width = width
        self.height = height
        self.pages = []
        self.isPaginated = False
        

class Bookshelf(object):
    def __init__(self):
        self.books = []
        self.current = 0
