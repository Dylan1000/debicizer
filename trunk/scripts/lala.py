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
import copy



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

ARCHITECTUR="darwin-arm"

PACKAGE_DIR = "./%s/DEBIAN"

CONTROL_PATH = "%s/control" % (PACKAGE_DIR)

PREINSTALL_PATH = "%s/preinst" % (PACKAGE_DIR)

PREREMOVE_PATH = "%s/prerm" % (PACKAGE_DIR)

POSTINSTALL_PATH = "%s/postinst" % (PACKAGE_DIR)

POSTREMOVE_PATH = "%s/postrm" % (PACKAGE_DIR)



ICON_PATH = "file:///Applications/%s/icon.png"

# Holds the mapping between plist keys and control keys


                    # 'Description' : ('description', 'N/A')}



if len(sys.argv) > 1:

    sourcefile = sys.argv[1]

else:

    sourcefile = "modmyifone.com/installer.xml"
os.system("rm -rf " + os.path.basename(sourcefile) )
os.system("curl -o \"" + os.path.basename(sourcefile) + "\" " + sourcefile )
url = copy.deepcopy(sourcefile)
sourcefile=os.path.basename(sourcefile)
#print url

#print sourcefile + " is the file"


CONTROL_PLIST_MAP = {'Package' : ('N/A'),

                     'Name' : ('name', 'N/A'),

                     'Section' : ('category', ''),

                     'Architecture' : (lambda x: 'darwin-arm', ''),

                     #'Installed-Size' : (get_size, ''),

                     #'Maintainer' : (get_contact, ''),

                     'Website' : ('url', ''),

                     'Version' : (lambda x: x['version'].replace(" ", ""), '1.0'),

                     #'Icon' : (find_icons, ''),

                    'Description' : ('description', 'N/A')}


# Converting the source xml (.plist) file into a python structure

plist = plistToPython(sourcefile)

# Holds a reference to the repo info

def createControlFile(package):

    """Creates a control file containing the various information, retrieved from the 
    sourcefile for each package.
    
    The package variable holds a python dict describing the package
    """
    # Create the directory for the package if it doesn't exist
#   print "* Creating control file for %s" % (package_name(package))
    if  not os.path.exists("../../zips/" + os.path.basename(valueForKey(package,'location'))):
    	print "no existe" + "../../zips/" + os.path.basename(valueForKey(package,'location'))
        return
    if  os.path.exists("../../zips/" + os.path.basename(valueForKey(package,'location'))+".done"):
        return
    
    else:
	print "entrando en controlfile"
        print "existe" + "../../zips/" + os.path.basename(valueForKey(package,'location'))

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
    fp.write("\n")
    fp.flush()
    fp.close()
    print "saliendo del controlfile"
    d = os.open("../../zips/" + os.path.basename(valueForKey(package,'location'))+".done", os.O_WRONLY | os.O_CREAT, 0666)
    os.close(d)

def package_id(package):
    bundle = package.get('bundleIdentifier')
    bundle=bundle.replace('_', '-' )
    return bundle.lower()+"-down"


def get_size(package):
    if not os.path.exists("%s" % package_name(package)):
        return 0
    print "du -s %s/* | awk '{print $1}'" % package_name(package)
    fp2 = popen("echo $(du -s ../../zips/" + os.path.basename(valueForKey(package,'location')) + "|awk '{print $1}')*3|bc") #% package_name(package)
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

def find_icons(package):
    app_list = glob("%s/Applications/*" % package_name(package))
    icons = []
    for app in app_list:
        icon_path = "%s/icon.png" % app
        final_icon_path = ICON_PATH % (os.path.basename(app))
        if os.path.exists(icon_path):
            icons.append(final_icon_path)
    
    return icons


def get_depends(package):
    #global depends
    #print "/////////////////////////////////////////////////////////////////////////"
    #print depends
#require firmware
#require subversion
#require python
#require wget
    depends=["firmware","subversion","python","wget"]
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

#print plist

#print "this is plist"

repo = plist['info']

globals()['repo']

# Holds a reference to the packages list


packages = plist['packages']


for p in packages:
#require firmware
#require subversion
#require python
#require wget
        #print p
	if  not os.path.exists("../../zips/" + os.path.basename(valueForKey(p,'location'))+".done"):
		if os.path.exists("../../zips/" + os.path.basename(valueForKey(p,'location'))):
                    os.system("mkdir -p \"" + package_name(p) + "/User/debicizer\"")
                    #os.system("mkdir -p \"" + package_name(p) + "/User/zips\"")
                    archivo=package_name(p) + "/User/debicizer/" + package_name(p) + ".sh"
                    
                    fd = open(archivo, "w")
                    print >>fd, "#!/bin/bash"
                    #print >>fd, "instalar () "
                    #print >>fd, "{ dpkg -i " + package_name(p) + ".deb"
                    #print >>fd, "while [ $? != 0 ]; do"
                    #print >>fd, "sleep 5; dpkg -i " + package_name(p) + ".deb"
                    #print >>fd, "done"
                    #print >>fd, "rm " + os.path.basename(valueForKey(p,'location'))
                    #print >>fd, "rm nohup.out"
                    #print >>fd, "}"
                    print >>fd, "cd zips"
                    print >>fd, "wget -nc " + valueForKey(p,'location')
                    print >>fd, "cd ../scripts/test/"
                    print >>fd, "wget -nc \"" + url + "\""
                    print >>fd, "python limpiar.py " + sourcefile
                    print >>fd, "python metadata.py " + sourcefile
                    print >>fd, "echo \"\" >> " + package_name(p) + "/DEBIAN/control"
                    print >>fd, "chmod a+x " + package_name(p) + "/DEBIAN/*"
                    print >>fd, "dpkg -b " +  package_name(p)
                    print >>fd, "rm ../../\"" + os.path.basename(valueForKey(p,'location'))+ "\""
                    print >>fd, "rm ../../\"" + os.path.basename(valueForKey(p,'location'))+ ".done\""
                    print >>fd, "echo going to backgroup to install package"
                    print >>fd, "rm nohup.out"
                    #print >>fd, "ln -s /dev/null nohup.out"
                    print >>fd, "rm " + sourcefile 
                    print >>fd, "rm " + os.path.basename(valueForKey(p,'location'))
                    print >>fd, "rm -rf " + package_name(p) + "/"
                    print >>fd, "echo #!/bin/bash > " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"SLEEP=1\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"for i in [ 1 2 3 4 5 6 7 8 9 ]; do \">> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"dpkg -i " + package_name(p) + ".deb \">> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"if [ $? -ne \\\"0\\\" ]\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"then\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"        let \\\"SLEEP *= 2\\\"\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"        sleep \$SLEEP\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"        false\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"else\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"        break\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"fi\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"done\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"if [ \$? -ne \\\"0\\\" ]\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"then\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \" echo failed installing\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"fi\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "echo \"rm \$0\" >> " + package_name(p) + "-script.sh"
                    print >>fd, "chmod a+x " + package_name(p) + "-script.sh"                    
                    print >>fd, "nohup ./" + package_name(p) + "-script.sh &"
                    
                    os.system("chmod a+x \"" + package_name(p) + "/User/debicizer/" + package_name(p) + ".sh\"")
                    os.system("mkdir -p \"" + package_name(p) + "/DEBIAN\"")
                    control=open(package_name(p) + "/DEBIAN/postinst","w")
                    print >>control, "#!/bin/bash"
                    print >>control,"cd /User"
                    print >>control,"svn co http://debicizer.googlecode.com/svn/trunk/ debicizer"
                    print >>control,"cd debicizer"
                    print >>control,"./\"" + package_name(p) + ".sh\""
                    control.close();
                    createControlFile(p)
                    os.system("chmod a+x */DEBIAN/*")
                else:
                    print "no existe el fichero ../../zips/" + os.path.basename(valueForKey(p,'location'))
        else:
            print "ignoring " + os.path.basename(valueForKey(p,'location'))
		
		#print >>control,"svn co http://debicizer.googlecode.com/svn/trunk/"
		
 		
		#os.system("unzip -o -qq ../zips/" + os.path.basename(p['location']) + " -d " + package_name(p)) 		
