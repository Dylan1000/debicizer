#Here we put all the specs of the script/program

# Introduction #

Our objective is to make a installer-> cydia repository conversor and automated repository manager for cydia repositories

# Usage #

svn co http://debicizer.googlecode.com/svn/trunk/

go to scripts and put the xml file of your repo, call it installer.xml

place all your repo zip files inside zips/

cd zips

./debian firstrun installer.xml "Repo Description" (note the quotes)

Currently paths are hardcoded


---

in scripts/test you can found a lala.py ( use this not scripts for the hardcoded paths)

lala.py execution:

it need the zip files of the repo in the same place zips/


python lala.py url\_of\_the\_xml\_repo\_file

it generates the folders to send to dpkg -b command



---




Command Lines
needs to be executed from unzipped dir and it cleans the unzipped folder and reunzip only zip files from the xml and after makes the metadata

sudo find -maxdepth 1 -type d -exec rm -rf {} \; ; python limpiar.py repo.xml ; python metadata.py repo.xml

show all the metadata files before and its name (works before deleting them)

for i in $(ls -1 iradiofix/DEBIAN/(an asterik here)); do echo $i ; cat $i ; done