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

def load_portage_graph():
    packageDict = {}
    
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

    with open('stats.csv', 'w') as fout:
        fout.write('packagename,deps,rdeps,level\n')
        for packageName in packageNameList:
            pObj = packageDict[packageName]
            fout.write('{0},{1},{2},{3}\n'.format(packageName, len(pObj.dependancies), len (pObj.rdeps), pObj.calcLevel()) )
    return packageDict


