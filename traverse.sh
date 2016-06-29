#!/bin/bash
if [ $# -ne 3 ];then
cat <<!HELP!         
$0 -- traverse a firmware folder with timeout

USAGE:   $0 folder manufacturer_path_level timeout
EXAMPLE: $0 /home/cy/Desktop/router 6 30
!HELP!
	exit 0
fi

folder=$1
manufacturer_path_level=$2
timeout=$3

IFS=$(echo -e "\n\b")

firmcount=0
for item in `find "$folder"`
do
	if [ -f "$item" ];then
		((firmcount++))
	fi
done

firmid=0
for item in `find "$folder"`
do
	if [ -f "$item" ];then
		((firmid++))
		echo "decompressed ${firmid}/${firmcount}:${item}"

		filepath="${item}"
		filename="${filepath##*/}"
		
		export timeout_flag
		binwalk  -e -M -q --depth=15 "$filepath" -C /tmp &
		commandpid=$!
		(sleep $timeout;kill -9 $commandpid >/dev/null 2>&1;echo binwalk take too much time!!!) &
		watchdogpid=$!
		sleeppid=`ps $PPID $watchdogpid | awk '{print $1}'`
		wait $commandpid
		kill $sleeppid >/dev/null 2>&1
		
		if [ -d /tmp/_${filename}.extracted ];then
			for item in `find "/tmp/_${filename}.extracted"`
			do			
				if [  "`file "$item"|grep ELF`" ] ;then	
					FirmName="${item##*/}"
					FileSize="'`ls -l "$item"|cut -d " " -f 5`'"
					FileMd5="'`md5sum "$item"|cut -d " " -f 1`'"
					Manufacturer="'`echo "$filepath"|cut -d "/" -f $manufacturer_path_level`'"
					echo "	$FirmName $FileSize $FileMd5 $Manufacturer" 
				fi
			done
			rm -rf "/tmp/_${filename}.extracted"
		else
			echo "binwalk can't extracted any file!!!"
		fi
	fi
done









#old_IFS=$IFS
#IFS=$(echo -e "\n\b")
#traverse_dir(){
#	for item in `ls "$1"`
#	do
#		if [ -d "$1""/""$item" ] && [ ! -L "$1""/""$item" ];then
#			traverse_dir "$1""/""$item"
#		elif [ -f "$1""/""$item" ];then
#			filepath="$1""/""$item"
#			filename="${filepath##*/}"
#			binwalk -q -e -M --depth=15 "$filepath" -C /tmp
#			for item in `find "/tmp/_${filename}.extracted"`
#			do
#				file $item
#			done
#			rm -rf "/tmp/_${filename}.extracted"
#		fi	
#	done
#}

#traverse_dir "$1"
#IFS=$old_IFS

