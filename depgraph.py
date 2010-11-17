#!/usr/bin/python

import os
import subprocess
import re
import string

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
	#print outdat
	#print outdat.split("\n")[3:-1]
	#print depList
	return set(depList)


packageDict = dict()
for package in list_portage_dir():
	packageDict[package] = Package(package)
	
processedPackages = set()

# read in processed packages files
with open('deps.txt') as depFile:
	for depString in depFile:
		packageName = depString[0:depString.index(' ')]
		depList = depString[depString.index('[')+1:depString.index(']')].split(',')
		for depName in depList:
			if depName not in packageDict:
				print
				print('### Error, {0} not in packageDict'.format(depName))
				print
			else:
				packageDict[packageName].dependancies.add(packageDict[depName])
		processedPackages.add(packageName)

# process remaining packages
for packageName in packageDict.iterkeys():
	if packageName in processedPackages:
		print('{0} already processed'.format(packageName))
		print
		continue
	print('Processing {0}'.format(packageName))
	depSet = find_direct_dependencies(packageName)
	print(depSet)
	for depName in depSet:
		if depName not in packageDict:
			print
			print('### Error, {0} not in packageDict'.format(depName))
			print
		else:
			packageDict[packageName].dependancies.add(packageDict[depName])
	with open('deps.txt', 'a+') as depFile:
		depFile.write('{0}\n'.format(packageDict[packageName].__str__()))
	print
