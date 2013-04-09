#!/bin/bash
FD=./faces

recConvert(){
	for e in "$1"/*;do
		if [ -d "$e" ];then
			"Entering in dir: $e"
			recConvert "$e"
		elif [ -f "$e" ];then
			"Converting the file: $e"
			convert "$e" -resize 64x64 "$e"
		fi
	done
}

recConvert $FD
