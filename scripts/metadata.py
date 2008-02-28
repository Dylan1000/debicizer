#!/usr/bin/env python

# control.py - Debian-style control file creator
#
# Uses PListReader developed by Andrew Shearer <awshearer@shearersoftware.com>
#
# Created by Lukas Pitschl <lukas@chrisandtheothergirls.com> on 02/07/08
# gpl v3
#

import sys
import os, os.path
from os import popen
import PListReader
import xml.sax
from glob import glob
import types
def plistToPython(file):
    """Creates a python structure from the passed plist file"""
    # parse the file
    reader = PListReader.PListReader()
    parser = xml.sax.make_parser()
    for key, value in reader.getRecommendedFeatures().items():
        parser.setFeature(key, value)
    parser.setContentHandler(reader)
    parser.parse(open(file, 'r'))
    
    return reader.getResult()

def package_name(package):
    """Recevies a filename and extracts the package name from it"""
    file = os.path.basename(package['location'])
    if not file.endswith('.zip'):
        return file.lower()
    return file[0:file.rfind('.zip')].lower()
    
def get_size(package):
    if not os.path.exists("%s/Applications" % package_name(package)):
        return 0
    fp2 = popen("du -s %s/Applications/*.app | awk '{print $1}'" % package_name(package))
    try:
        size = fp2.read().strip()
        size = int(size)
    except:
        size = 0
    fp2.close()
    
    return size

def get_contact(package):
    email = " <%s>"
    contact = []
    repo = globals()['repo']
    author = package.get('maintainer', package.get('author', repo.get('maintainer', '')))
    c = package.get('contact', repo.get('contact', ''))
    contact.append(author and "%s" % author or None)
    contact.append(c and "<%s>" % c or None)
    
    return " ".join([c for c in contact if c]).strip()

def package_id(package):
    bundle = package.get('bundleIdentifier')
    return bundle.lower()

def find_icons(package):
    app_list = glob("%s/Applications/*" % package_name(package))
    icons = []
    for app in app_list:
        icon_path = "%s/icon.png" % app
        final_icon_path = ICON_PATH % (os.path.basename(app))
        if os.path.exists(icon_path):
            icons.append(final_icon_path)
    
    return icons

def valueForKey(package, plist_key, default="N/A"):
    """Extracts the value for a given key from the PLIST.
    
    If a function is detected rather than a string, the function is executed
    and it's value returned, else it's assumed that the string is a key
    in the PLIST and its value is read and returned.
    """
    if callable(plist_key):
        value = plist_key(package)
    else:
        value = package.has_key(plist_key) and package[plist_key] or default
    return value

def createControlFile(package):

    """Creates a control file containing the various information, retrieved from the 
    sourcefile for each package.
    
    The package variable holds a python dict describing the package
    """
    # Create the directory for the package if it doesn't exist
#   print "* Creating control file for %s" % (package_name(package))
    if  not os.path.exists("../zips/" + os.path.basename(valueForKey(package,'location'))):
	return
	#print "no existe" + "../zips/" + os.path.basename(valueForKey(package,'location'))
    else:
	print "existe" + "../zips/" + os.path.basename(valueForKey(package,'location'))	
    try:
        os.makedirs(PACKAGE_DIR % package_name(package))
    except OSError:
        pass
    # Creating an empty control file
    control = CONTROL_PATH % package_name(package)
    fp = open(control, "w")
    content = []
    # Looping through the control -> plist map
    for ctrl_key, plist_key in CONTROL_PLIST_MAP.iteritems():
        value = valueForKey(package, plist_key[0], plist_key[1])
        if type(value) != type([]):
            value = [value]
        [content.append('%s: %s' % (ctrl_key, val)) for val in value]
    fp.write("\n".join(content))
    fp.close()
    
def prepareFiles(package):
    print "lala"
    install = PREINSTALL_PATH % package_name(package)
    fp3 = open(install, "w")
    print >>fp3, "#!/bin/bash"
    fp3.close()
    install1 = POSTINSTALL_PATH % package_name(package)
    fp4 = open(install1, "w")
    print >>fp4, "#!/bin/bash"
    fp4.close()
    remove = PREREMOVE_PATH % package_name(package)
    fp5 = open(remove, "w")
    print >>fp5, "#!/bin/bash"
    fp5.close()
    remove1 = POSTREMOVE_PATH % package_name(package)
    fp6 = open(remove1, "w")
    print >>fp6, "#!/bin/bash"
    fp6.close()
    
    
def closeFiles(package):
    install = PREINSTALL_PATH % package_name(package)
    fp3 = open(install, "a")
    print >>fp3, "exit"
    fp3.close()
    install1 = POSTINSTALL_PATH % package_name(package)
    fp4 = open(install1, "a")
    print >>fp4, "exit"
    fp4.close()
    remove = PREREMOVE_PATH % package_name(package)
    fp5 = open(remove, "a")
    print >>fp5, "exit"
    fp5.close()
    remove1 = POSTREMOVE_PATH % package_name(package)
    fp6 = open(remove1, "a")
    print >>fp6, "exit"
    fp6.close()
    

def createInstallFiles(package):
    """Creates install and remove files containing the various information, retrieved from the 
    sourcefile for each package.
    
    The package variable holds a python dict describing the package
    """
    global operation
    if  not os.path.exists("../zips/" + os.path.basename(valueForKey(package,'location'))):
        return
    # Create the directory for the package if it doesn't exist
    #print package
    #print "* Creating install and remove files for %s" % (package_name(package))
    #print package_name(package)
    try:
        os.makedirs(PACKAGE_DIR % package_name(package))
    except OSError,a:
	#print a
        pass
    
    
	#os.makedirs(
    # Creating an empty install file

    test = valueForKey(package,'scripts')
    prepareFiles(package)
    global script
    shellscript = "script.sh"
    script = open(shellscript, "w")
    if (valueForKey(test,'install')):
	print "install"
	operation="inst"
        #install = PREINSTALL_PATH % package_name(package)
        #fp3 = open(install, "w")
        #print >>fp3, "#!/bin/bash"
        #fp3.close()
	z = valueForKey(test,'install')
	generateShell(z,package_name(package),1)
        #fp3 = open(install, "a")
        #print >>fp3, "exit"
        #fp3.close()
    #remove = PREREMOVE_PATH % package_name(package)
    #fp4 = open(remove, "w")
    #print >>fp4, "#!/bin/bash"
    script.close()
    os.chmod("script.sh",0755) #needs to be octal not decimal
    os.system("bash script.sh")
    if (valueForKey(test,'uninstall')):
	print "uninstall"
	operation="rm"
	k = valueForKey(test,'uninstall')
	generateShell(k,package_name(package),1)
    #print >>fp4, "exit"
    #fp4.close()
    #closeFiles(package)
 
     
    #           if (valueForKey(test,'uninstall')):
     #                  print "uninstall"
                        #print valueForKey(test,'uninstall') 
#                       k = valueForKey(test,'uninstall')
                        #generateShell(k)



def isRelative(path):
    if path.startswith('/'):
        return False
    else:
        return True
    

def generateShell(file,dir,n):
	#name of the directory of the app 
	#n is a number to know if is direct or recursive the call
	#print "es el archivo"# + " ".join(file)
	print file
	#print "lalala" 
	#print dir
	#print n
	#dir = package_name(dir)	
	prefix="pre"
        archivo=dir + "/DEBIAN/" + prefix + operation
        print archivo
        fd = open(archivo, "a")
        
	print prefix
        print operation
        flagForCopyPath=0
        
	for h in file:
		if h[0] == "CopyPath": #h[1] origen h[2]destino
                            #unlockfiles    /usr/bin
                            #Info.plist     /Applications/MobileAddressBook.app/Info.plist //Contacts.zip
                                    
			#print >>fd, "cp -pR \"../" + h[1] + "\" \"" + h[2] + "\""
			#if
			if isRelative(h[1]) and os.path.exists(dir + "/" + h[1]) :
                            print "is relative"
                            #print "me cago en tus muertos"
			    print >>script, "cd " + dir
			    #print type(h[2])
			    #[0:file.rfind('.zip')].lower()
                            if os.path.basename(h[2]) == h[1]:
                                #print "name is in destination path"
                                #print h[2] + " " + h[1]
                                print >>script, "mkdir -p \"`pwd`" + h[2][0:h[2].rfind('/')] + "\""
                                print >>script, "cp -pR \"" + h[1] + "\" \"`pwd`" + h[2] + "\""
                            else:
                                print >>script, "mkdir -p \"`pwd`" + h[2] + "\""
                                print >>script, "cp -pR \"" + h[1] + "\" \"`pwd`" + h[2] + "/\""	
                            print >>script, "cd .."
                            flagForCopyPath=1
                            #fd.close()
                            
                            
                            #fd.
                            #prefix="post"
                            #archivo=dir + "/DEBIAN/" + prefix + operation
                            #print archivo
                            #os.system("cat " + POSTINSTALL_PATH % file)

                            #fd = open(archivo, "a")
                            
                            #print type(fd)
                        else:
                            print "is absolut"
                            
                        print dir
			print h[1]
			#print h[1].startswith('/')		
			if os.path.exists(dir + "/" + h[1]):
				print "existe el archivo y vamos a moverlo ahora"
				print dir + "/" + h[1]
				
			else:
				print dir + "/" + h[1]
				print "el archivo no existe asi que pondremos en el archivo que toca"
				print >>fd, "cp -pR \"" + h[1] + "\" \"" + h[2] + "\""
 
			#if n == 1:
				
			#	print "me cago en tus muertos"
			#	print "cd " + dir
			#	print type(h[2])
			#	print "mkdir -p \"`pwd`" + h[2] + "\""
			#	print "cp -fpR \"" + h[1] + "\" \"`pwd`" + h[2] + "/\""	
			#	print "cd .."
			#else :
			#	print >>fd, "cp -pR \"" + h[1] + "\" \"" + h[2] + "\""	
                else:
                    if flagForCopyPath==1:
                            fd.close()                                                        
                            #fd.
                            prefix="post"
                            archivo=dir + "/DEBIAN/" + prefix + operation
                            #print archivo
                            #os.system("cat " + POSTINSTALL_PATH % file)

                            fd = open(archivo, "a")
                            flagForCopyPath=0
                if h[0] == "RemovePath":
               		print >>fd, "rm -rf \"" + h[1] + "\""
                        #print "borrar " + h[1]
                elif h[0] == "Exec":
                        print " ".join(h[1:])
                        print >>fd, " ".join(h[1:])
                elif h[0] == "SetStatus":
                        print >>fd, "echo " + " ".join(h[1:])
                elif h[0] == "Notice":
                        print >>fd, "echo " + " ".join(h[1:])
                elif h[0] == "MovePath":
                        print >>fd, "mv -f \"" + h[1] + "\" \"" + h[2] + "\""
                elif h[0] == "If":
                        print "es un puto IF"
                        print type(h[1])
                        print types.ListType
                        print h[1]
                        if type(h[1]) == types.ListType:
                        	print "es una lista vamos a mirar que es"
                                print h[1][0][0]
                                if h[1][0][0]=="ExistsPath":
                                        print >>fd, "if [ -e \"" + h[1][0][1] +"\" ]; then"
                                        #print "test the existance"
					fd.flush()
                                        temp=h[2]
					print temp
					generateShell(temp,dir,0)
                                	print >>fd, "fi"
					#print "es un ExistsPath"
					#print h[2]
		else:
			print h	



ARCHITECTUR="darwin-arm"
PACKAGE_DIR = "./%s/DEBIAN"
CONTROL_PATH = "%s/control" % (PACKAGE_DIR)
PREINSTALL_PATH = "%s/preinst" % (PACKAGE_DIR)
PREREMOVE_PATH = "%s/prerm" % (PACKAGE_DIR)
POSTINSTALL_PATH = "%s/postinst" % (PACKAGE_DIR)
POSTREMOVE_PATH = "%s/postrm" % (PACKAGE_DIR)

ICON_PATH = "file:///Applications/%s/icon.png"
# Holds the mapping between plist keys and control keys
CONTROL_PLIST_MAP = {'Package' : (package_id, 'N/A'),
                     'Name' : ('name', 'N/A'),
                     'Section' : ('category', ''),
                     'Architecture' : (lambda x: 'darwin-arm', ''),
                     'Installed-Size' : (get_size, ''),
                     'Maintainer' : (get_contact, ''),
                     'Website' : ('url', ''),
                     'Version' : (lambda x: x['version'].replace(" ", ""), '1.0'),
                     'Icon' : (find_icons, ''),
                     'Description' : ('description', 'N/A')}

if len(sys.argv) > 1:
    sourcefile = sys.argv[1]
else:
    sourcefile = "./installer.xml"
    
# Converting the source xml (.plist) file into a python structure
plist = plistToPython(sourcefile)
# Holds a reference to the repo info
repo = plist['info']
globals()['repo']
# Holds a reference to the packages list
packages = plist['packages']
#scripts = plist['scripts']
#print scripts
# Looping through the packages an obtaining the information needed.
# this information is passed to the createControlFile method, which will
# create a 'control' file - needed for the debian packages - for each installer
# package.
# 
# The control file will be located under $PACKAGENAME/DEBIAN/control.
[createControlFile(p) for p in packages]
for p in packages:
#	print p
	#scripts = plist['scripts']
	#print scripts
	createInstallFiles(p)
#	if (valueForKey(p,'scripts')):
#		test = valueForKey(p,'scripts')
#		#print p.name 
#		print valueForKey(p,'name')
		#print package_name(os.path.basename(valueForKey(p,'location')))
#		print package_name(p)
#		try:
#			os.mkdir(package_name(p))
#			os.mkdir(package_name(p)+"/DEBIAN")
#		except:
#			pass	
#		if (valueForKey(test,'install')):
#			#print valueForKey(test,'install') 
#			print "install"
#			z = valueForKey(test,'install')
			
			#generateShell(z)
#			for h in z:
				#print h[0] + " " + h.pop()
				#print " ".join(h)
				#try:
#					print "antes del for"
#					for item in h:
#						print type(item)
#						print item
#					print "fuera del for"
#					print type(h)
#					print h
 #					if h[0] == "CopyPath":
#						print "cp -pR \"" + h[1] + "\" \"" + h[2] + "\""
#					elif h[0] == "RemovePath":
#						print "rm -rf \"" + h[1] + "\""
#					elif h[0] == "Exec":
#						print " ".join(h[1:])
#					elif h[0] == "SetStatus":
#						print "echo " + " ".join(h[1:])
#					elif h[0] == "Notice":
#						print "echo " + " ".join(h[1:])
#					elif h[0] == "MovePath":
#						print "mv -f \"" + h[1] + "\" \"" + h[2] + "\""
#					elif h[0] == "If":
#						print "es un puto IF" 
#						print type(h[1])
#						print types.ListType
#						print h[1]
#						if type(h[1]) == types.ListType:
#                                                       print "es una lista vamos a mirar que es"
#							print h[1][0][0]
#							if h[1][0][0]=="ExistsPath":
#								print "es un ExistsPath"
#								print h
#								print "if [ -e \"" + h[1][0][1] +"\" ]; then"
#					else: 
#						print h
						#print h[1:]	
					#if h[0].lower() == "if":
					#	print "son iguales"
					#if h[0].lower() == "exec":
					#	print h[1:] + " es la linea"
					#print " ".join(h) + " es la union" 
#					print h.tolist() + " " + h.tolist()
					#print j[0] + " " + j.pop()
					#print h.tostring()
#					print 
				#except TypeError, e:
				#	print h				
#		if (valueForKey(test,'uninstall')):
#			print "uninstall"
			#print valueForKey(test,'uninstall') 
#			k = valueForKey(test,'uninstall')
			#generateShell(k)
#			for j in k:
#				if j[0] == "CopyPath":
#					print "cp -pR \"" + j[1] + "\" \"" + j[2] + "\""
#				elif j[0] == "RemovePath":
#					print "rm -rf \"" + j[1] + "\""
#				elif j[0] == "Exec":
#					print " ".join(j[1:])
#				else:
#					 print j
				#print j[0] + " " + j.pop() #+   " " +  "".join(j)
#				print "".join(str(j) for j in L if j > 1)
