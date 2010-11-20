#! /usr/bin/python

import os, sys
import cairo
import json

class Package:
	def __init__(self, name):
		self.name = name
		self.dependancies = set()
		self.position = (0.0, 0.0)
		
	def calcLevel(self):
		max = 0
		for dep in self.dependancies:
			depLevel = dep.calcLevel()
			if depLevel > max:
				max = depLevel
		return max + 1
		
	def __str__(self):
		return '{0} [{1}]'.format(self.name, ','.join([dep.name for dep in self.dependancies]))
		
		
class SimpleSVG:
	def __init__(self, filename):
		self.surface = cairo.SVGSurface(filename, 1920, 1080)
		self.context = cairo.Context(self.surface)
		
	def drawRect(self, x, y, w, h ):
		self.context.set_source_rgb(0.0, 0.0, 0.0)
		self.context.set_line_width(10)
		self.context.rectangle(x, y, w, h)
		self.context.stroke()
		
		
	def drawText(self, x, y, text):
		self.context.set_source_rgb(0.0, 0.0, 0.0)
		self.context.set_line_width(0.5)
		self.context.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		self.context.set_font_size(10)
		x_bearing, y_bearing, width, height = self.context.text_extents(text)[:4]
		self.context.move_to(x - x_bearing, y - height / 2 - y_bearing)
		self.context.text_path(text)
		self.context.fill()
		
	def drawLine(self, x1, y1, x2, y2):
		self.context.set_source_rgb(0.0, 0.0, 0.0)
		self.context.set_line_width(1)
		self.context.move_to(x1, y1)
		self.context.line_to(x2, y2)
		self.context.stroke()
		
	def finish(self):
		self.surface.write_to_png('test.png')
		self.surface.finish()
		
def drawGraph(packages):
	
	svg = SimpleSVG('output.svg')
	xoffsets = dict()
	for package in packages.itervalues():
		level = package.calcLevel()
		xoff = 1
		if level in xoffsets:
			xoffsets[level] += 1
			xoff = xoffsets[level]
		else:
			xoffsets[level] = 1
			
		package.position = (100*xoff, 100*level)
		#svg.drawText(*package.position, text=package.name)
		svg.drawRect(package.position[0], package.position[1], 2, 2)
		
	for package in packages.itervalues():
		for dep in package.dependancies:
			x1, y1 = package.position
			x2, y2 = dep.position
			svg.drawLine( x1, y1, x2, y2)

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
	print(package)
	print('{0} is level {1}'.format(package.name, package.calcLevel()))
	
drawGraph(plist)
