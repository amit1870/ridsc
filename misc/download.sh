#!/bin/bash

function download_url {

	# checking for dir
	dir=/home/pi/videos
	if [ -d "$dir" ]; then
		cd $dir
	else
		mkdir $dir && cd $dir
	fi

	arg=$1
	URL_ARR=(${arg//^/ })

	# getting pid of running youtube-dl
	pids=`ps aux | grep '[y]outube-dl'`
	pids=(${pids// / })

	# if no instance of youtube-dl 
	if [ "${#pids[1]}" -eq 0 ];then

		echo "Status		url"
		for URL in "${URL_ARR[@]}"; do

			# for unique name 
			file=(${URL//?v=/ })
			filename=${file[1]}

			skip=false

			# checking if the $URL is already downloaded
			res="best"
			if [ -f "$filename$res.mp4" ]; then 
				skip=true
				echo "Downloaded 	$URL"
			fi


			# If not downloaded, then download
			if [ $skip == false ];then

				format=`youtube-dl -F $URL | grep $res`
		       	arrIN=(${format// / })
		       	code=${arrIN[0]}

				# downloading $URL
				echo "Downloading 	$URL"
				sudo youtube-dl -f $code $URL >> /dev/null
				
				# moving downloaded $URL into unique name
				tmp=`ls | grep $filename`
				sudo mv "${tmp}" "$filename$res.mp4"
			fi
		done
	else
		echo "youtube-dl already running"
	fi
}


download_url $1


