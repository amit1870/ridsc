#!/bin/bash
PATH=/bin/sh.distrib /bin/sh /usr/share/man/man1/sh.1.gz

videos=`ls ~/rids_assets/ | grep '.mp4'`
arrIN=(${videos// / })
len=${#arrIN[@]}
# echo $len
i=0
while [[ $i -le $len-1 ]]; do
	file=${arrIN[$i]}
	# echo $file
	filearr=(${file//.mp4/ })
	name=${filearr[0]}
	# echo $name
	if [[ -e ~/rids_files/"$name.jpeg" ]]; then
		echo "File exists"
	else
		# avconv -loglevel "quiet" -i ~/rids_assets/$file -s uxga ~/rids_files/"$name.jpeg"
		avconv  -loglevel "quiet"  -ss `avconv -i ~/rids_assets/$file 2>&1 | grep 'Duration' | awk '{print $2}' | sed s/,//` -vframes 1 -i ~/rids_assets/$file -s uxga ~/rids_files/"$name.jpeg"
	fi
	(( i++ ))
done
