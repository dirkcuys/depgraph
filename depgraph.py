#!/usr/bin/python

import os
import subprocess
import re
import string

class Package:
	def __init__(self, name):
		self.name = name
		self.dependancies = set()

	def __str__(self):
		return '{0} -> {1}'.format(self.name, self.dependancies)


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

for package in packageDict.iterkeys():
	depSet = find_direct_dependencies(package)
	print depSet
	for dependancy in depSet:
		if dependancy not in packageDict:
			print('### Error, {0} not in packageDict'.format(dependancy))
		else:
			packageDict[package].dependancies.add(dependancy)
	print packageDict[package]
	print
