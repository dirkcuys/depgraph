#!/usr/bin/python

import re
import string

from drawutils import SimpleSVG
from packagegraph import Package
		
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


packageDict = {}
#for package in set(list_portage_dir()):
#	packageDict[package] = Package(package)
	
processedPackages = set()

progressCount = 0
progressTotal = len(packageDict)

completeExclude = ['sys-devel/gettext', 'sys-devel/binutils', 'dev-lang/perl', 'sys-devel/libtool', 'sys-devel/automake']
completeExclude += ['sys-devel/autoconf', 'sys-devel/m4', 'dev-util/pkgconfig', 'dev-libs/glib', 'dev-lang/python']
completeExclude += ['x11/libs/gtk+']

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
				pass
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
packageNameList.sort()
#for packageName in packageNameList:
#	print packageDict[packageName]

with open('stats2.csv', 'w') as fout:
	fout.write('packagename,deps,rdeps,level\n')
	for packageName in packageNameList:
		pObj = packageDict[packageName]
		fout.write('{0},{1},{2},{3}\n'.format(packageName, len(pObj.dependancies), len (pObj.rdeps), pObj.calcLevel()) )

excludeList = ['dev-util/pkgconfig', 'sys-devel/libtool', 'sys-devel/automake', 'sys-devel/autoconf']	
drawGraph(packageDict, excludeList)

#drawPackageDepGraph('media-libs/libgphoto2', packageDict, excludeList)

#print(packageDict['media-libs/libgphoto2'])
#for dep in packageDict['media-libs/libgphoto2'].dependancies:
#	print dep

