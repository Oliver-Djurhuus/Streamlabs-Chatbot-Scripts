#!/usr/bin/python
# -*- encoding: utf-8 -*-

""" This script was written by Oliver Djurhuus. Mail: oliverdjurhuus@gmail.com """
"""2018, April 8th"""
""" It was made on the request of EsfandTV for his Twitch channel."""

#---------------------------------------
# Import Libraries
#---------------------------------------
import sys
import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
from datetime import datetime
from random import randint as random
import json

#---------------------------------------
# [Required] Script Information
#---------------------------------------
ScriptName = "Esfands_Rigged_Raffle"
Website = "www.noctum.ninja"
Description = "A game of raffle - totally not rigged!"
Creator = "Oliver Djurhuus"
Version = "1.1.0.0"

#---------------------------------------
# Set Variables
#---------------------------------------
Game = None

#---------------------------------------
# [Required] Intialize Data (Only called on Load)
#---------------------------------------
def Init():
	Parent.SendStreamMessage("► Esfands Rigged Raffle has been loaded! ")
	global Game
	Game = Raffle();
	return

#---------------------------------------
# [Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
	if not len(data.Message):
		return
	if Game.Is_Started() and len(data.Message) == len("!raffle") and data.Message.lower() == "!raffle":
		Game.Add_Participant(data.User)	
	return

#---------------------------------------
# [Required] Tick Function / Idle 
#---------------------------------------
def Tick():
	Game.Tick()
	return

#---------------------------------------
# [Optional] 
#---------------------------------------
def Unload():
	#Triggers when the bot closes / script is reloaded
	return

def ScriptToggled(state):
	if state == True:
		Game.Start()
	else:
		Game.Reset()
	return

def ReloadSettings(jsonData):
	settings = json.loads(jsonData)
	Game.Set_Settings(settings["entry_cost"], settings["reward"], settings["duration"])
	return

#---------------------------------------
# Butter 
#---------------------------------------
class Raffle:

	def __init__(self):
		# 0 - Not started
		# 1 - Countdown
		# [2-3] - Game in session
		# 3 - Game about to end
		# 4 - Game is over 
		self.entry_cost = 2
		self.reward = 10
		self.duration = 120

		self.game_state = 0
		self.participants = []
		self.time_start = 0

		#self.Msg_Start = "► A retbull-raffle for {} retbulls has started!! Entry cost is {} retbulls! Type !raffle in the chat to join!"
		self.Msg_Start = "A RetBull Raffle for {} RetBulls has started!! Entry cost is {} RetBulls! Type !raffle in chat to join!"
		self.Msg_Ending_Soon = "► The raffle is ending in 15sec! Participate by typing !raffle "
		self.Msg_End = "► The retbull-raffle has ended!"

		#self.Msg_Winner = "► The winner is {}! Taking home {} retbulls! Congratz :)"
		self.Msg_Winner = "esfandTV esfandTV The winner is {}! Taking home {} RetBulls! esfandTV esfandTV"
		self.Msg_No_Winner = "► There were no participants, thus no winner.. Alas!"

		self.Msg_Already_In_Session = "► There is already a raffle active."
		self.Msg_Destroyed = "► The retbull-raffle was destroyed!"

	def Is_Started(self):
		if self.game_state == 3 or self.game_state == 2:
			return True;
		return False;

	def Start(self):
		if self.game_state != 0:
			Parent.SendStreamMessage(self.Msg_Already_In_Session)
			return
		self.Reset()

		self.time_start = datetime.now()
		self.game_state = 2
		Parent.SendStreamMessage(self.Msg_Start.format(self.reward, self.entry_cost))
		return

	def End(self):
		if self.game_state == 0:
			pass
		elif len(self.participants) == 0:
			Parent.SendStreamMessage(self.Msg_No_Winner)
			self.game_state = 4
		else:
			for participant in self.participants:
				Parent.RemovePoints(participant, self.entry_cost)

			winner = self.participants[random(0, len(self.participants)-1)]
			Parent.AddPoints(winner, self.reward)
			Parent.SendStreamMessage(self.Msg_Winner.format(Parent.GetDisplayName(winner), self.reward))
			self.game_state = 4
		self.Reset()
		return

	def Reset(self):
		if self.game_state > 0 and self.game_state < 4:
			Parent.SendStreamMessage(self.Msg_Destroyed)
		self.participants = []
		self.game_state = 0
		return

	def Add_Participant(self, user):
		if self.game_state < 2:
			return False

		for participant in self.participants:
			if participant == user:
				return False

		if self.entry_cost > Parent.GetPoints(user):
			return False

		self.participants.append(user)

		Parent.SendStreamMessage(Parent.GetDisplayName(user) + " has joined the raffle!")

		return True

	def Set_Settings(self, new_entry_cost, new_reward, new_duration):
		self.entry_cost = new_entry_cost
		self.reward = new_reward
		self.duration = new_duration

		if self.game_state == 0:
			Parent.SendStreamMessage("► Settings set! Entrycost of " + str(self.entry_cost) + "retbulls --- Reward is " + str(self.reward) + "retbulls --- Game duration " + str(self.duration) +"seconds ")
		else:
			Parent.SendStreamMessage("► Settings updated! Entrycost of " + str(self.entry_cost) + "retbulls --- Reward is " + str(self.reward) + "retbulls --- Game duration " + str(self.duration) +"seconds ")


		if self.entry_cost < 0:
			Parent.SendStreamMessage("Warning: Entrycost is " + str(self.entry_cost) + "!")

		if self.reward < 0:
			Parent.SendStreamMessage("Warning: Reward is " + str(self.reward) + "!")

		if self.entry_cost > self.reward:
			Parent.SendStreamMessage("Warning: Entrycost is greater than the self.reward! ")

		if (self.duration < 0):
			Parent.SendStreamMessage("Warning: The Duration is 0!")

		return

	def Tick(self):
		if self.game_state == 0:
			return

		time_current = datetime.now()
		time_left = self.duration - (time_current - self.time_start).seconds
		if time_left <= 0:
			self.End()
		elif time_left - 15 <= 0 and self.duration > 30 and self.game_state == 2:
			self.game_state = 3
			Parent.SendStreamMessage(self.Msg_Ending_Soon)
		return
