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

class Event:
	"""this is a superclass for any events that might be generated by an
	object and sent to the EventManager"""
	def __init__(self):
		self.name = "Generic Event"

class TickEvent(Event):
	def __init__(self):
		self.name = "CPU Tick Event"

class QuitEvent(Event):
	def __init__(self):
		self.name = "Program Quit Event"

class GameStartedEvent(Event):
	def __init__(self, game):
		self.name = "Game Started Event"
		self.game = game

class GameFinishedEvent(Event):
	def __init__(self, game):
		self.name = "Game Finished Event"
		self.game = game

class BoardLoadedEvent(Event):
	def __init__(self, board):
		self.name = "Board Loaded Event"
		self.board = board

class PlayerMoveRequest(Event):
	def __init__(self, player, pos):
		self.name = "Player Move Request"
		self.player = player
		self.pos = pos

class PlayerMoveEvent(Event):
	def __init__(self, player, pos):
		self.name = "Player Move Event"
		self.player = player
		self.pos = pos

class PlayerPlaceEvent(Event):
    """this event occurs when a Player is *placed* in a board position, 
    ie it doesn't move there from another board position."""
    def __init__(self, player):
        self.name = "Player Placement Event"
        self.player = player

class LostTurnEvent(Event):
    """this event occurs when a Player fails to answer a question"""
    def __init__(self):
        self.name = "Lost Turn Event"

class ShowPlayerRequest(Event):
    def __init__(self):
        self.name = "Show Player Event"

class HidePlayerRequest(Event):
    def __init__(self):
        self.name = "Hide Player Event"

class ShowSignsRequest(Event):
    def __init__(self):
        self.name = "Hide Sign Event"

class HideSignsRequest(Event):
    def __init__(self):
        self.name = "Hide Sign Event"

class ThrowDiceRequest(Event):
    def __init__(self):
        self.name = "Throw Dice Request"

class ThrowDiceEvent(Event):
    def __init__(self, dice):
        self.name = "Throw Dice Event"
        self.dice = dice

class UpdateRequest(Event):
    def __init__(self):
        self.name = "Update Display Request"

class FinishedLoadingEvent(Event):
    def __init__(self):
        self.name = "Finished Loading Event"        


class AskQuestionRequest(Event):
    def __init__(self, player):
        self.name = "Ask Question Request"
        self.player = player

class KeyCommandEvent(Event):
    def __init__(self, command):
	self.name = "Key Command Event"
	self.key = command

class MouseCommandEvent(Event):
    def __init__(self, command):
	self.name = "Mouse Command Event"
	self.command = command

class LeftButtonClickEvent(Event):
    def __init__(self, pos):
	self.name = "Left Button Click Event"
	self.pos = pos
	
class LeftButtonUpEvent(Event):
    def __init__(self, pos):
	self.name = "Left Button Up Event"
	self.pos = pos

