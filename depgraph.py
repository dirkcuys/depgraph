#!/usr/bin/python

import re
import string
import math
from random import random
from drawutils import SimpleSVG
from packagegraph import Package

import pygame, os, sys
from pygame.locals import *
		
def drawGraph(packageDict, excludes):
	svg = SimpleSVG('output.svg')
	xoffsets = dict()
	for package in packageDict.itervalues():
		if package.name in excludes:
			continue
		print ('drawing {0}'.format(package.name))
		level = package.calcLevel()
		xoff = 1
		if level in xoffsets:
			xoffsets[level] += 1
			xoff = xoffsets[level]
		else:
			xoffsets[level] = 1
			
		package.position = (5 + 10*xoff, 5 + 30*level)
		#svg.drawText(*package.position, text=package.name)
		svg.drawRect(package.position[0] - 3, package.position[1] - 3, 6, 6)
		
	for package in packageDict.itervalues():
		if package.name in excludes:
			continue
		print ('drawing {0} dependancies'.format(package.name))
		for dep in package.dependancies:
			if dep.name not in excludes:
				x1, y1 = package.position
				x2, y2 = dep.position
				svg.drawLine( x1, y1, x2, y2)
	svg.finish()
	
def drawPackageDepGraph(packageName, packageDict, excludes):
	"""draw dependancy graph for a specific package"""
	
	if packageName not in packageDict:
		print('{0} not in packageDict'.format(packageName))
		return
	
	deplist = []
	
	def drawGraphRecursive(package, stack):
		if package in stack:
			return
		if package in deplist:
			return
		if package in excludes:
			return
		deplist.append(package)
		#print (','.join([dep.name for dep in stack]))
		stackCopy = list(stack)
		stack.append(package)
		for dep in package.dependancies:
			drawGraphRecursive(dep, stack)	
		stack.pop()
		if stack != stackCopy:
			print('stack corrupted')
	
	#drawGraphRecursive(packageDict[packageName], [])
	packageDict[packageName].calcLevel()
	print('{0} dependancies for package {1}'.format(len(deplist), packageName))
	print('package is level {0}'.format(packageDict[packageName].calcLevel()))
	#drawGraph(deplist, [])
	#print(','.join([dep.name for dep in deplist]))

def drawCircleGraph(packageDict):
	
	svg = SimpleSVG('circle_out.svg')
	package_count = len(packageDict)
	
	pygame.init()
	width, height = 1024, 1024
	surface = pygame.display.set_mode((width, height))
	radius = width/2.0 - 100
	
	#calculate x,y positions for packages
	for index, package in enumerate(packageDict.itervalues()):
		x = radius*math.cos(index/(0.5*package_count)*math.pi)
		y = radius*math.sin(index/(0.5*package_count)*math.pi)
		package.position = (width/2.0 + x, height/2.0 + y)
		package.colour = (255*random(), 255*random(), 255*random(), 0.4)
		sizeX = len(package.dependancies)
		sizeY = len(package.rdeps)/10
		if sizeY < 0.5:
			sizeY = 1
		
		rect = (package.position[0] - sizeX/2.0, package.position[1] - sizeY/2.0, sizeX, sizeY)
		x2 = width/2.0 + (sizeY+radius)*math.cos(index/(0.5*package_count)*math.pi)
		y2 = height/2.0 + (sizeY+radius)*math.sin(index/(0.5*package_count)*math.pi)
		#pygame.draw.rect( surface, package.colour, rect, 1)
		pygame.draw.line( surface, package.colour, package.position, (x2, y2), 1)
		
		if len(package.dependancies) > 2000 or len(package.rdeps) > 20:
			text = pygame.font.SysFont('Arial', 9).render(package.name[depString.index('/')+1:], False, package.colour)
			if index > 0.25*package_count and index < 0.75*package_count:
				surface.blit(text, (x2 - text.get_width(), y2))
			else:
				surface.blit(text, (x2, y2))
	
	for package in packageDict.itervalues():
		print ('drawing {0} dependancies'.format(package.name))
		for dep in package.dependancies:
			# only draw deps that is in the package dictionary
			if dep.name in packageDict:
				x1, y1 = package.position
				x2, y2 = dep.position
				#svg.drawLine( x1, y1, x2, y2)
				pygame.draw.line( surface, dep.colour, (x1, y1), (x2, y2), 1)
				
	pygame.display.flip()
		
	while True:
		# only look for and get events we are interested in
		if pygame.event.peek((QUIT,)):
			for event in pygame.event.get((QUIT,)):
				if event.type == QUIT:
					sys.exit(0)
				else:
					print event
	
packageDict = {}
#for package in set(list_portage_dir()):
#	packageDict[package] = Package(package)
	
processedPackages = set()

progressCount = 0
progressTotal = len(packageDict)

completeExclude = ['sys-devel/gettext', 'sys-devel/binutils', 'dev-lang/perl', 'sys-devel/libtool', 'sys-devel/automake']
completeExclude += ['sys-devel/autoconf', 'sys-devel/m4', 'dev-util/pkgconfig', 'dev-libs/glib', 'dev-lang/python']
completeExclude += ['x11-libs/gtk+', 'app-arch/unzip', 'sys-apps/sed', 'app-admin/eselect-python', 'dev-util/cmake']
completeExclude += ['sys-libs/zlib', 'dev-util/automoc', 'dev-java/java-config', 'dev-java/ant-core' , 'dev-util/intltool']
completeExclude += ['app-text/sword-modules', 'app-xemacs/xemacs-packages-all', 'app-text/texlive']
completeExclude += ['gnome-base/gnome', 'dev-util/netbeans', 'media-video/mplayer', 'media-sound/squeezeboxserver']
completeExclude += ['media-video/vlc', 'x11-base/xorg-x11', 'x11-base/xorg-server', 'app-editors/padre']
completeExclude += ['app-office/openoffice', 'x11-base/xorg-drivers', 'media-tv/xbmc', 'net-zope/zope']
completeExclude += ['kde-base/kdelibs']
completeExclude = []

with open('deps.txt') as depFile:
	for depString in depFile:
		#print('reading "{0}" from deps.txt'.format(depString))
		packageName = depString[0:depString.index(' ')]
		if packageName in completeExclude:
			continue
		packageDict[packageName] = Package(packageName)

# read in processed packages files
with open('deps.txt') as depFile:
	for depString in depFile:
		#print('reading "{0}" from deps.txt'.format(depString))
		packageName = depString[0:depString.index(' ')]
		if packageName in completeExclude:
			continue
		depList = depString[depString.index('[')+1:depString.index(']')].split(',')
		for depName in depList:
			if depName not in packageDict:
				#print('### Error, "{0}" not in packageDict'.format(depName))
				continue
			elif depName in completeExclude:
				continue
			else:
				packageDict[packageName].addDep(packageDict[depName])
		processedPackages.add(packageName)
		progressCount += 1

# process remaining packages
for packageName in packageDict.iterkeys():
	if packageName in processedPackages:
		#print('{0} already processed'.format(packageName))
		#print
		continue
	print('Processing {0} ({1} of {2})'.format(packageName, progressCount, progressTotal))
	depSet = find_direct_dependencies(packageName)
	print(depSet)
	for depName in depSet:
		if depName not in packageDict:
			print
			print('### Error, "{0}" not in packageDict'.format(depName))
			print
		else:
			packageDict[packageName].addDep(packageDict[depName])
	with open('deps.txt', 'a+') as depFile:
		depFile.write('{0}\n'.format(packageDict[packageName].__str__()))
	progressCount += 1
	
packageNameList = list(packageDict.iterkeys())
#packageNameList.sort()
#for packageName in packageNameList:
#	print packageDict[packageName]

#with open('stats2.csv', 'w') as fout:
#	fout.write('packagename,deps,rdeps,level\n')
#	for packageName in packageNameList:
#		pObj = packageDict[packageName]
#		fout.write('{0},{1},{2},{3}\n'.format(packageName, len(pObj.dependancies), len (pObj.rdeps), pObj.calcLevel()) )

excludeList = ['dev-util/pkgconfig', 'sys-devel/libtool', 'sys-devel/automake', 'sys-devel/autoconf']
#excludeList = excludeList[:] + completeExclude[:]
#drawGraph(packageDict, excludeList)

#excludeList = excludeList[:] + [package.name for package in packageDict.itervalues() if len(package.dependancies) < 5 and len(package.rdeps) < 5]
#for excl in set(excludeList):
#	if excl in packageDict.keys():
#		del packageDict[excl]
		
#while len(packageDict) > 5000:
#	packageDict.popitem()
	
drawCircleGraph(packageDict)


#drawPackageDepGraph('media-libs/libgphoto2', packageDict, excludeList)

#print(packageDict['media-libs/libgphoto2'])
#for dep in packageDict['media-libs/libgphoto2'].dependancies:
#	print dep

