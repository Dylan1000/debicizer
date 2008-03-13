#echo -n "Enter your name and press [ENTER]: " 
#read var_name
#echo "Your name is: $var_name"
until [ -n "$var_name" ]; do 
	echo -n "Enter the path to the xml file [ENTER]: "
	read var_name
#	echo "Your name is: $var_name"

	if expr "$var_name" : '^\/'; then
#		echo empiza con \/
#		echo es un path absoluto
		if [[ ! -e "$var_name" ]]; then
			echo no existe el archivo
			unset var_name
#		else
#			echo wtf
		fi
	else
		echo $(pwd)/$var_name
		if [[ ! -e "$(pwd)/$var_name" ]]; then
			echo no existe el archivo
			unset var_name
#		else
#			echo el archivo va bien
		fi
		#echo es un path relativo
	fi

	#do echo lala; 
	#read var_name; 
done

until [ -n "$zip_folder" ]; do
	echo -n "Enter the folder containing the zips [ENTER]: "
	read zip_folder
	if expr "$zip_folder" : '^\/'; then
 #               echo empiza con \/
 #               echo es un path absoluto
                if [[ ! -d "$zip_folder" ]]; then
			unset zip_folder
		fi
	else
		if [[ ! -d "$(pwd)/$zip_folder" ]]; then
			unset zip_folder
		else
			zip_folder="$(pwd)/$zip_folder"
#			echo $zip_folder
		fi
	fi
done

mkdir -p cache/unzipped
mkdir -p cache/zips
mkdir repo
ln -s $(pwd)/repo cache/unzipped/repo
for i in $(find $zip_folder -name '*.zip'); do 
#	echo $i ; 
	ln -s $i cache/zips/$(basename $i)
done

echo "cd cache > run.sh"
echo "cd zips > run.sh"

#if expr "$var_name" : '^\/'; then 
#echo empiza con \/
#echo es un path absoluto
#
#else
#echo es un path relativo
#fi
