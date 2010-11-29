import os
import subprocess
import re
import string

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
