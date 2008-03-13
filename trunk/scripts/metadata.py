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
import string

def plistToPython(file):
    """Creates a python structure from the passed plist file"""
    # parse the file
    reader = PListReader.PListReader()
    parser = xml.sax.make_parser()
    for key, value in reader.getRecommendedFeatures().items():
        parser.setFeature(key, value)
    parser.setContentHandler(reader)
    print file
    parser.parse(open(file, 'r'))
    
    return reader.getResult()

def package_name(package):
    """Recevies a filename and extracts the package name from it"""
    file = os.path.basename(package['location'])
    if not file.endswith('.zip'):
        return file.lower()
    return file[0:file.rfind('.zip')].lower()
    
def get_size(package):
    if not os.path.exists("%s" % package_name(package)):
        return 0
    print "du -s %s/* | awk '{print $1}'" % package_name(package)
    fp2 = popen("du -s %s/ | awk '{print $1}'" % package_name(package))
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

def get_depends(package):
    global depends
    print "/////////////////////////////////////////////////////////////////////////"
    print depends
    
    print package.has_key('requires')
    if package.has_key('requires'):
        print "tiene dependencias"
        depends.append(valueForKey(package,'requires'))
    if depends.count>1:
        checked = [] 
        for e in depends: 
            if e not in checked: 
                checked.append(e) 
        #return checked
        print "".join(checked)
        print "son las putas dependencias"
        return ", ".join(checked)
    else:
        return depends
    

def createControlFile(package):

    """Creates a control file containing the various information, retrieved from the 
    sourcefile for each package.
    
    The package variable holds a python dict describing the package
    """
    # Create the directory for the package if it doesn't exist
#   print "* Creating control file for %s" % (package_name(package))
    if  not os.path.exists("../zips/" + os.path.basename(valueForKey(package,'location'))):
    	print "no existe" + "../zips/" + os.path.basename(valueForKey(package,'location'))
        return
    if  os.path.exists("../zips/" + os.path.basename(valueForKey(package,'location'))+".done"):
        return
    
    else:
	print "entrando en controlfile"
        print "existe" + "../zips/" + os.path.basename(valueForKey(package,'location'))
        
    try:
        os.makedirs(PACKAGE_DIR % package_name(package))
    except OSError,a:
        print "esto es una mierda"
        #print a
        pass
    # Creating an empty control file
    control = CONTROL_PATH % package_name(package)
    print control
    fp = open(control, "w")
    print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    print fp
    content = []
    # Looping through the control -> plist map
    for ctrl_key, plist_key in CONTROL_PLIST_MAP.iteritems():
        value = valueForKey(package, plist_key[0], plist_key[1])
        if type(value) != type([]):
            value = [value]
        #print value
        for val in value:
            #print type(str(val))
            #print 
            print str(val)
            if len(str(val)) > 0:
                content.append('%s: %s' % (ctrl_key, val))
        #[content.append('%s: %s' % (ctrl_key, val)) for val in value]
    fp.write("\n".join(content))
    fp.flush()
    fp.close()
    print "saliendo del controlfile"
    d = os.open("../zips/" + os.path.basename(valueForKey(package,'location'))+".done", os.O_WRONLY | os.O_CREAT, 0666)
    os.close(d)
    
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
    global prefix
    global fd
    if  not os.path.exists("../zips/" + os.path.basename(valueForKey(package,'location'))):
        return
    if  os.path.exists("../zips/" + os.path.basename(valueForKey(package,'location'))+".done"):
        print "ignoring " + os.path.basename(valueForKey(package,'location'))+".done"
        return
    try:
        os.makedirs(PACKAGE_DIR % package_name(package))
    except OSError,a:
	#print a
        pass
    
    #operation="pre"
	#os.makedirs(
    # Creating an empty install file
    prefix="pre"
    test = valueForKey(package,'scripts')
    prepareFiles(package)
    global script
    global shellscript
    global directory
    shellscript = "script.sh"
    script = open(shellscript, "w")
    print package.keys()
    print type(package)
    print package
    directory=package_name(package)
    if test.has_key('preflight'):
        operation="inst"
        openFd()
        closeFd()
        openFd()
        print "tiene preflight"
        m=valueForKey(test,'preflight')
        print m
        parsepreflight(m)
        #dsdadad
    if test.has_key('install'):

    #if (valueForKey(test,'install')):
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
    script.close()
    os.chmod(shellscript,0755) #needs to be octal not decimal
    os.system("bash script.sh")
    if test.has_key('uninstall'):

    #if (valueForKey(test,'uninstall')):
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



def parsepreflight(algo):
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    print algo[0]
    print type(algo)
    print "en el preflight"
    for p in algo:
        parser(p)
        #print p
        #print p[0]
        #print p[1]
        #print p[2]
        print "----------------------------------------------------------------------------"
    print "saliendo de preflight"
    #cosa
    
def stringer(algo):
    print lala

    
def parser(IF):
    global fd
    global depends
    print IF
    temp=[]
    if IF[0]=="IfNot":
        if IF[1][0][0]=="FirmwareVersionIs":
            for k in IF[1][0][1]:
                #print k
                print "sera la version?"
                temp.append("firmware ("+ k + ")")
                #types.StringTypes.
                
                #temp.append("firmware("+ k + ")")
                #i = 0
                #while i < temp.count():
                #    
                #temp.append("firmware("+ k + ")")
                #while 
                #depends.append("".join(
                #firmware(1.1.3) | firmware(1.1.4)
                print "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"
                print depends
            depends.append(" | ".join(temp))
        elif IF[1][0][0]=="ExistsPath":
            
            #print IF[2][0][0]
            print IF[1][0][1]
            #print IF[1][0][0][1]
            print fd
            print >>fd, "if [ ! -e " + IF[1][0][1] + " ]; then"
            print >>fd, "   exit 1"
            print >>fd, "fi"
            closeFd()
            openFd()
        elif IF[1][0][0]=="InstalledPackage":
            print IF[1][0]
            print IF[1][0][1]
            print IF[1][0][0]
            if type(IF[1][0][1]) != (types.UnicodeType or types.StringType):
                for k in IF[1][0][1]:
                    print "sera el paquete instalado?"
                    print IF[1][0]
                    #h[2].find('/var/mobile')>-1
                    if IF[1][0].find('com.natetrue.iphone.iphone_binkit')==-1:
                        depends.append(k)
            else:
                if IF[1][0][1].find('com.natetrue.iphone.iphone_binkit')==-1:
                    depends.append(IF[1][0][1])
            
            
            #cosa

            
        else:
            print "mequivocau"
    
    
    
def isRelative(path):
    if path.startswith('/'):
        return False
    else:
        return True
    #/bin/mkdir -p /private/var/root/Library/LEI/TTR_Backup||/||b||i

def parseExec(line,dir):
    global fd
    global script
    global shellscript
    global prefix
    print "estamos en parseexec"
    print dir + " es el dir"
    print line + " es la linea"
    print type(line)
    splitedline=line.split()
    print splitedline
    #if splitedline[0] == "/bin/mkdir":
    if splitedline[0].endswith('/mkdir'):
        print "es un mkdir"
        print prefix + operation
        if splitedline[1][0] == "-":
            #print "es un argumento"
            #print "mkdir -p \"`pwd`/" + dir + splitedline[2] +"\""
            print >>script, "mkdir -p \"`pwd`/" + dir + splitedline[2] +"\""
            script.close()
            os.chmod(shellscript,0755) #needs to be octal not decimal
            #os.system("cat script.sh")
            os.system("bash script.sh")
            script = open(shellscript, "w")
        else:
            print >>script, "mkdir -p \"`pwd`/" + dir + splitedline[1] +"\""
            script.close()
            os.chmod(shellscript,0755) #needs to be octal not decimal
            #os.system("cat script.sh")
            os.system("bash script.sh")
            script = open(shellscript, "w") 
    elif splitedline[0].endswith('/mv'):
        if splitedline[1][0] == "-":
            test=[["MovePath",splitedline[2],splitedline[3]]]
            generateShell(test,dir,0)
        else:
            test=[[u"MovePath",splitedline[1],splitedline[2]]]
            generateShell(test,dir,0)
    elif splitedline[0].endswith('/cp'):
        if splitedline[1][0] == "-":
            test=[["CopyPath",splitedline[2],splitedline[3]]]
            generateShell(test,dir,0)
        else:
            test=[[u"CopyPath",splitedline[1],splitedline[2]]]
            generateShell(test,dir,0)
    else:
        #if line.find(' '):
        #   sys.stderr.write(line + '<----if some argument has spaces the exec statement will generated wrong\n')
        #line=line.replace( ' ', '" "' )
        #print >>fd, "/usr/libexec/cydia/exec \"" + line + "\""
        print >>fd, "/usr/libexec/cydia/exec " + line    
        
           
           
           
           
           
        
    
    print "salimos de parseexec"

def openFd():
    global prefix
    global operation
    global fd
    global directory
    print directory
    print "es el directorio"
    archivo=directory + "/DEBIAN/" + prefix + operation
    fd = open(archivo, "a")

def closeFd():
    global fd
    #print type(fd)
    fd.close()
    

def generateShell(file,dir,n):
	#name of the directory of the app 
	#n is a number to know if is direct or recursive the call
	#print "es el archivo"# + " ".join(file)
	print file
        global operation
        print dir + "es el puto directorio"
	#print "lalala" 
	#print dir
	#print n
	#dir = package_name(dir)
        global directory
        #directory=dir
	global prefix
        
        
        archivo=dir + "/DEBIAN/" + prefix + operation
        print archivo
        global fd
        global script
        global shellscript
        global depends        
        #global operation
        fd = open(archivo, "a")
        
	print prefix
        print operation
        flagForCopyPath=0
        flagForRemovePath=0
        
	for h in file:
		if h[0] == "CopyPath": #h[1] origen h[2]destino
                            #unlockfiles    /usr/bin
                            #Info.plist     /Applications/MobileAddressBook.app/Info.plist //Contacts.zip
                            #Applications/openttd.app /Applications/openttd.app
                                    
			#print >>fd, "cp -pR \"../" + h[1] + "\" \"" + h[2] + "\""
			#if
                        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

                        insidecontent=0
                        if h[1].endswith('/'):
                            h[1] = h[1][0:-1]
                            insidecontent=1
                        if h[2].endswith('/'):
                            h[2] = h[2][0:-1]
                        
                        print h[2]
                        print h[2].find('~')
                        if (h[2].find('~')>-1):    

                            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                            h[2]=h[2].replace( '~', '/User' )
                            depends.append('firmware')
                        elif (h[2].find('/var/mobile')>-1):
                            h[2]=h[2].replace( '/var/mobile', '/User' )
                            depends.append('firmware')
                        else:
                            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                            print "is sux"
                            
                            
                        

                        
			if isRelative(h[1]) and os.path.exists(dir + "/" + h[1]):# and operation == "inst":
                            print "is relative"
                            #print "me cago en tus muertos"
			    print >>script, "cd " + dir
			    #print type(h[2])
			    #[0:file.rfind('.zip')].lower()
                            print os.path.basename(h[1]) + " el basename"
#                            if os.path.basename(h[2]) == os.path.basename(h[1]):
#                            	print "name is in destination path"
#                            	print h[2] + " " + h[1]
#                                print "mkdir -p \"`pwd`" + h[2][0:h[2].rfind('/')] + "\""
#                                print "mv -f \"`pwd`/" + h[1] + "\" \"`pwd`" + h[2] + "\""
#                                print >>script, "mkdir -p \"`pwd`" + h[2][0:h[2].rfind('/')] + "\""
#                                print >>script, "mv -f \"`pwd`/" + h[1] + "\" \"`pwd`" + h[2] + "\""
#                            else:
#                            #    print "mkdir -p \"`pwd`" + h[2] + "\""
#                            #    print "cp -pR \"`pwd`/" + h[1] + "\" \"`pwd`" + h[2][0:h[2].rfind('/')] + #"\""
#                                print >>script, "mkdir -p \"`pwd`" + h[2] + "\""
#                                #print >>script, "cp -pR \"`pwd`/" + h[1] + "*\" \"`pwd`" + h[2] + "/\""
#                                print >>script, "mv -f \"`pwd`/" + h[1] + "\" \"`pwd`" + h[2] + "/\""
 
                                
                            if os.path.basename(h[2]) == os.path.basename(h[1]):
                                print >>script, "mkdir -p \"`pwd`" + h[2][0:h[2].rfind('/')] + "\""
                                print >>script, "mv -f \"`pwd`/" + h[1] + "\" \"`pwd`" + h[2][0:h[2].rfind('/')]  + "\""
                            else:    
                                if insidecontent==0:
                                    print >>script, "mkdir -p \"`pwd`" + h[2] + "\""
				#print >>script, "mv -f \"`pwd`/" + h[1] + "/\" \"`pwd`" + h[2] + "/\""
 

                                    print >>script, "cp -pR \"`pwd`/" + h[1] + "\" \"`pwd`" + h[2] + "/\""
                                    print >>script, "rm -rf \"`pwd`/" + h[1] + "\""
                                else:
                                    print >>script, "mkdir -p \"`pwd`" + h[2] + "\""
                                    print >>script, "cp -pR \"`pwd`/" + h[1] + "/\"* \"`pwd`" + h[2] + "/\""
                                    print >>script, "rm -rf \"`pwd`/" + h[1] + "/\""
                            print >>script, "cd .."
                            if operation == "inst":
                                flagForCopyPath=1
                            #fd.close()
                            
                            script.close()
                            os.chmod(shellscript,0755) #needs to be octal not decimal
                            
                            #os.system("cp script.sh cosa.sh");
                            #if h[2]=="/User/Media/MooCowMusic/Pianist":
                            #	csfddsfsfs
                            os.system("bash script.sh")
                            script = open(shellscript, "w")
                            #fd.
                            #prefix="post"
                            #archivo=dir + "/DEBIAN/" + prefix + operation
                            #print archivo
                            #os.system("cat " + POSTINSTALL_PATH % file)

                            #fd = open(archivo, "a")
                            
                            #print type(fd)
                        else:
                            
                            print "is absolut or doesn't exist"
                            print >>fd, "cp -pR \"" + h[1] + "\" \"" + h[2] + "\""
                            
                            
                        #print dir
			#print h[1]
			#print h[1].startswith('/')		
			##if os.path.exists(dir + "/" + h[1]):
			#	print "existe el archivo y vamos a moverlo ahora"
			#	print dir + "/" + h[1]
			#	
			#else:
			#	print dir + "/" + h[1]
			#	print "el archivo no existe asi que pondremos en el archivo que toca"
			##	print >>fd, "cp -pR \"" + h[1] + "\" \"" + h[2] + "\""
 
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
                            #global prefix
                            prefix="post"
                            archivo=dir + "/DEBIAN/" + prefix + operation
                            #print archivo
                            #os.system("cat " + POSTINSTALL_PATH % file)
                            fd = open(archivo, "a")
                            flagForCopyPath=0

                if h[0] == "RemovePath":
                    for j in h:
                        if j != "RemovePath":
                            j=j.replace( '~', '/var/mobile' )
                            if not os.path.exists(dir + j):
                               print >>fd, "rm -rf \"" + j + "\""
                            else:
                                if operation == "rm":
                                  flagForRemovePath=1
                                else:
                                    print >>fd, "rm -rf \"" + j + "\""
                else:
                    if flagForRemovePath==1:
                            fd.close()                                                        
                            #fd.
                            prefix="post"
                            archivo=dir + "/DEBIAN/" + prefix + operation
                            #print archivo
                            #os.system("cat " + POSTINSTALL_PATH % file)
                            fd = open(archivo, "a")
                            flagForRemovePath=0
                        
                        #print "borrar " + h[1]
                if h[0] == "Exec":
                    #print "vamos a ver el exec"
                    #print type(h[1])
                    #print h
                    #print "\\-".join(h[1:]) + " es un exec "
                    parseExec(h[1],dir)
                    #works
                    #test
                    #parseExec("\\".join(h[1:]),dir)
                    #if h[1].startswith('/bin/mkdir'):
                    #    print "es un mkdir"
                    #print " ".join(h[1:]) + "||" + "".join(h[1][0]) + "||" + "".join(h[1][1])+ "||" + "".join(h[1][2])
                    #print >>fd, " ".join(h[1:])
                elif h[0] == "ExecNoError":
                    #print "vamos a ver el execnoerror"
                    #print type(h[1])
                    #print h
                    #print "".join(h[1]) + " es un execnoerror "
                    parseExec(h[1],dir)
                    print >>fd, "true"
                elif h[0] == "SetStatus":
                        print >>fd, "echo " + " ".join(h[1:])
                #elif h[0] == "Notice":
                        #replace the ' with \' before printing in file or it will break
                        #print >>fd, "echo \'" + " ".join(h[1:]) + "\'"
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
		elif h[0] == "InstallApp":
                    test=[[u"CopyPath",h[1],"/Applications"]]
                    generateShell(test,dir,0)
                elif h[0] == "UninstallApp":
                    #one="/Applications/"+str(h[1])
                    test=[[u"RemovePath",u"/Applications/"+h[1]]]
                    generateShell(test,dir,0)
                else:
			print h
                        print " es que no es nada de todo eso"




#print "im running currently"
ARCHITECTUR="darwin-arm"
PACKAGE_DIR = "./%s/DEBIAN"
CONTROL_PATH = "%s/control" % (PACKAGE_DIR)
PREINSTALL_PATH = "%s/preinst" % (PACKAGE_DIR)
PREREMOVE_PATH = "%s/prerm" % (PACKAGE_DIR)
POSTINSTALL_PATH = "%s/postinst" % (PACKAGE_DIR)
POSTREMOVE_PATH = "%s/postrm" % (PACKAGE_DIR)
global operation

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
                     'Description' : ('description', 'N/A'),
                     'Depends' : (get_depends ,'')}

if len(sys.argv) > 1:
    sourcefile = sys.argv[1]
else:
    sourcefile = "./installer.xml"

#print sourcefile + " is the file"
# Converting the source xml (.plist) file into a python structure
plist = plistToPython(sourcefile)
# Holds a reference to the repo info

#print plist
#print "this is plist"
repo = plist['info']
globals()['repo']
# Holds a reference to the packages list
packages = plist['packages']
#print packages
#print "these are packages"
global j

#scripts = plist['scripts']
#print scripts
# Looping through the packages an obtaining the information needed.
# this information is passed to the createControlFile method, which will
# create a 'control' file - needed for the debian packages - for each installer
# package.
# 
# The control file will be located under $PACKAGENAME/DEBIAN/control.


#[createControlFile(p) for p in packages]

for j in packages:
	#print p
	#print "asasasaa"
        #scripts = plist['scripts']
	#print scripts
        global depends
        global prefix
        global operation
        depends=[]
	createInstallFiles(j)
        createControlFile(j)
#plist = plistToPython(sourcefile)
#repo = plist['info']
#globals()['repo']
#packages = plist['packages']
#[createControlFile(p) for p in packages]
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
