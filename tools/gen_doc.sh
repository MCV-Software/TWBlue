#!/bin/bash
mkdir ../src/documentation
for i in `ls ../documentation`
do
	if test -d ../documentation/$i
then
		mkdir ../src/documentation/$i
		pandoc -s ../documentation/$i/changes.md -o ../src/documentation/$i/changes.html
		pandoc -s ../documentation/$i/manual.md -o ../src/documentation/$i/manual.html
  cp ../documentation/license.txt ../src/documentation/license.txt
	fi
done
exit
