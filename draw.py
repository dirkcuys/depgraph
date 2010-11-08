#! /usr/bin/python

import pygame, os, sys
from pygame.locals import *


class App:
	def __init__(self, packages):
		self.surface = None
		self.packages = packages

	def onInit(self):
		pygame.init()
		self.window = pygame.display.set_mode((800,600))
		self.surface = pygame.display.get_surface()
		
		xoffsets = dict()
		positions = dict()
		
		for package in self.packages.itervalues():
			level = package.calcLevel()
			xoff = 1
			if level in xoffsets:
				xoffsets[level] += 1
				xoff = xoffsets[level]
			else:
				xoffsets[level] = 1
				
			positions[package] = (100*xoff, 100*level)
			pygame.draw.circle( self.surface, (255,255,255,1), (100*xoff, 100*level), 10, 1)
			
		for package, pos in positions.iteritems():
			for dep in package.dependancies:
				pygame.draw.line( self.surface, (255,255,255,1), pos, positions[dep])
			
		#pygame.draw.circle( self.surface, (255,255,255,1), (100, 100), 10, 1)

	def onMouseMotion(self, mouse_event):
		#print 'Mouse!!'
		#print mouse_event.pos
		#pygame.draw.circle( self.surface, (255,255,255,1), mouse_event.pos, 10, 1)
		pass

	def onExit(self):
		sys.exit(0)

	def onEvent(self,events):
		for event in events:
			if event.type == QUIT:
				self.onExit()
			elif event.type == MOUSEMOTION:
				self.onMouseMotion(event)
			else:
				print event

	def mainLoop(self):
		while True:
			# only look for and get events we are interested in
			if pygame.event.peek((MOUSEMOTION, QUIT)):
				self.onEvent(pygame.event.get((MOUSEMOTION, QUIT)))
			pygame.display.flip()
			
class Package:
	def __init__(self, name):
		self.name = name
		self.dependancies = set()
		
	def calcLevel(self):
		max = 0
		for dep in self.dependancies:
			depLevel = dep.calcLevel()
			if depLevel > max:
				max = depLevel
		return max + 1

plist = dict()

plist['cairo'] = Package('cairo')
plist['libX'] = Package('libX')
plist['qt-core'] = Package('qt-core')
plist['readline'] = Package('readline')
plist['libxml'] = Package('libxml')
plist['qt'] = Package('qt')
plist['kde'] = Package('kde')
plist['gimp'] = Package('gimp')

plist['kde'].dependancies.add(plist['qt'])
plist['kde'].dependancies.add(plist['libxml'])
plist['kde'].dependancies.add(plist['qt-core'])
plist['kde'].dependancies.add(plist['cairo'])

plist['qt'].dependancies.add(plist['cairo'])
plist['qt'].dependancies.add(plist['qt-core'])
plist['qt'].dependancies.add(plist['libX'])

plist['gimp'].dependancies.add(plist['qt'])
plist['gimp'].dependancies.add(plist['cairo'])

plist['libxml'].dependancies.add(plist['readline'])

for package in plist.itervalues():
	print('{0} is level {1}'.format(package.name, package.calcLevel()))
game = App(plist)
game.onInit()
game.mainLoop()
