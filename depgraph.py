#!/usr/bin/python

import os
import subprocess
import re
import string
import cairo

class Package:
	
	stack = []
	
	def __init__(self, name):
		self.name = name
		self.dependancies = set()
		self.position = (0.0, 0.0)
		self.cache = 0
		self.rdeps = set()
		
	def addDep(self, dep):
		self.dependancies.add(dep)
		dep.addRDep(self)
		
	def addRDep(self, rdep):
		self.rdeps.add(rdep)
		
	def calcLevel(self):
		if self.name in Package.stack:
			print('Circular dependancy detected')
			return 0
			
		if self.cache > 0:
			return self.cache
			
		Package.stack.append(self.name)
		#print('{0}.calcLevel() : callStack = {1}'.format(self.name, stack))
		max = 0
		for dep in self.dependancies:
			depLevel = dep.calcLevel()
			if depLevel > max:
				max = depLevel
		self.cache = max + 1
		Package.stack.pop()
		return self.cache
		
	def __str__(self):
		return '{0} [{1}]'.format(self.name, ','.join([dep.name for dep in self.dependancies]))


def list_portage_dir():
	packageList = set()
	catagoryList = os.listdir('/usr/portage')
	excludes = ['distfiles', 'eclass', 'header.txt', 'licenses', 'local']
	excludes += ['metadata', 'profiles', 'scripts', 'skel.ChangeLog']
	excludes += ['skel.ebuild', 'skel.metadata.xml']
	
	for excludeDir in excludes:
		catagoryList.remove(excludeDir)
		
	for catagoryDir in catagoryList:
		packageDirList = os.listdir('/usr/portage/{0}'.format(catagoryDir))
		if 'metadata.xml' in packageDirList:
			packageDirList.remove('metadata.xml')

		for packageDir in packageDirList:
			packageList.add('{0}/{1}'.format(catagoryDir, packageDir))

	return packageList


def find_direct_dependencies(package):
	print "Checking dependancies for {0}".format(package)
	command = "equery -C depgraph {0}".format(package)
	#print command
	proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	(outdat, indat) = proc.communicate()
	depList = list()
	for dep in outdat.split("\n")[3:-1]:
		#depList.append(re.sub(r'-[0-9]{1,}.*$', '', dep[8:-3]))
		depStr = re.sub(r'-[0-9]{1,}.*$', '', string.strip(dep, ' [  0]  ') )
		if depStr not in  ['', package]:
			depList.append(depStr)
	return set(depList)

	
class SimpleSVG:
	def __init__(self, filename):
		self.surface = cairo.SVGSurface(filename, 16384, 8192)
		self.context = cairo.Context(self.surface)
		
	def drawRect(self, x, y, w, h ):
		self.context.set_source_rgb(0.0, 0.0, 0.0)
		self.context.set_line_width(1)
		self.context.rectangle(x, y, w, h)
		self.context.stroke()
		
		
	def drawText(self, x, y, text):
		self.context.set_source_rgb(0.0, 0.0, 0.0)
		self.context.set_line_width(1)
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
		print('SimpleSVG.finish');
		self.surface.write_to_png('test.png')
		print('SimpleSVG.finish: after write_to_png()');
		self.surface.finish()

		
def drawGraph(packages, excludes):
	svg = SimpleSVG('output.svg')
	xoffsets = dict()
	for package in packages:
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
		
	for package in packages:
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
	print('package is level {0}'.format(packageDict[packageName].calcLevel()))
	print('package is level {0}'.format(packageDict[packageName].calcLevel()))
	#drawGraph(deplist, [])
	#print(','.join([dep.name for dep in deplist]))


packageDict = {}
#for package in set(list_portage_dir()):
#	packageDict[package] = Package(package)
	
processedPackages = set()

progressCount = 0
progressTotal = len(packageDict)

with open('deps.txt') as depFile:
	for depString in depFile:
		#print('reading "{0}" from deps.txt'.format(depString))
		packageName = depString[0:depString.index(' ')]
		packageDict[packageName] = Package(packageName)

# read in processed packages files
with open('deps.txt') as depFile:
	for depString in depFile:
		#print('reading "{0}" from deps.txt'.format(depString))
		packageName = depString[0:depString.index(' ')]
		depList = depString[depString.index('[')+1:depString.index(']')].split(',')
		for depName in depList:
			if depName not in packageDict:
				print
				print('### Error, "{0}" not in packageDict'.format(depName))
				print
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
packageNameList.sort()
#for packageName in packageNameList:
#	print packageDict[packageName]


#with open('stats2.csv', 'w') as fout:
#	fout.write('packagename,deps,rdeps,level\n')
#	for packageName in packageNameList:
#		pObj = packageDict[packageName]
#		fout.write('{0},{1},{2},{3}\n'.format(packageName, len(pObj.dependancies), len (pObj.rdeps), pObj.calcLevel()) )

excludeList = ['dev-util/pkgconfig', 'sys-devel/libtool', 'sys-devel/automake', 'sys-devel/autoconf']	
#drawGraph(packageDict, excludeList)

drawPackageDepGraph('media-libs/libgphoto2', packageDict, excludeList)

print(packageDict['media-libs/libgphoto2'])
for dep in packageDict['media-libs/libgphoto2'].dependancies:
	print dep

	
