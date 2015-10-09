#Start deving

mkdir example

cd example

svn co http://debicizer.googlecode.com/svn/trunk/

cd trunk/zips

in debian file:

add exit before "python metadata.py $repofile" line


cd ../scripts

wget http://xml_file

cd ../zips

download all zips from this xml file (ask in irc.saurik.com #debicize)

./debian firstrun installer.xml "Repo Description"

cd ../../unzipped

python metadata.py file.xml

NOTE: metadata.py and limpiar.py will ignore zip files if exist file.zip.done for start from the begining you can use

sudo find -maxdepth 1 -type d -exec rm -rf {} \; ; rm ../../zips/(an asterisk here).done ; python limpiar.py este.xml ; python metadata.py este.xml