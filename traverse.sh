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

INSERT_CMD_START="db.files.insert({"
INSERT_CMD_END="});"

IFS=$(echo -e "\n\b")

firmcount=0
for item in `find "$folder"`
do
	if [ -f "$item" ];then
		((firmcount++))
	fi
done

firmid=0
elfid=0
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
				if [ -n "`file "$item"|grep ELF`" ] ;then
					((elfid++))		
					FileName="${item##*/}"
					FileSize=$(ls -l "$item"|cut -d " " -f 5)
					FileMd5=$(md5sum "$item"|cut -d " " -f 1)
					Manufacturer=$(echo "$filepath"|cut -d "/" -f $manufacturer_path_level)
					FirmName="$filepath"
					strings --bytes=10 "$item" > "./output/"${elfid}"_"${FileName}".tmp"
					[ -s "./output/${elfid}_${FileName}.tmp" ] && ./a.out "./output/${elfid}_${FileName}.tmp" > "./output/${elfid}_${FileName}" && records="${INSERT_CMD_START}Manufacturer:\"${Manufacturer}\",FirmName:\"${FirmName}\",FileName:\"${FileName}\",FileSize:${FileSize},FileMd5:\"${FileMd5}\",StrFileName:\"${elfid}_${FileName}\"${INSERT_CMD_END}" && echo "$records"|mongo --quiet --shell
					rm "./output/${elfid}_${FileName}.tmp"
					
					echo "        ${elfid}:${FileName}"
				fi
			done
			rm -rf "/tmp/_${filename}.extracted"
		else
			echo "binwalk can't extracted any file!!!"
		fi
	fi
done

