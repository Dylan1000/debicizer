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

for p in packages:

	if  not os.path.exists("../../zips/" + os.path.basename(valueForKey(p,'location'))+".done"):
            if  not os.path.exists("../../zips/" + os.path.basename(valueForKey(package,'location'))):
                print "no existe" + "../../zips/" + os.path.basename(valueForKey(package,'location'))
            else:
		os.system("mkdir " + package_name(p))

		os.system("unzip -o -qq ../../zips/" + os.path.basename(p['location']) + " -d " + package_name(p)) 		
