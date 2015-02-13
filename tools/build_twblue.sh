#!/bin/bash
# Define paths for a regular use, if there are not paths for python32 or 64, these commands will be taken.
pythonpath32="/C/python27x86"
pythonpath64="/C/python27"
nsyspath=$PROGRAMFILES/NSIS

help () {
	echo -e "$0 | usage:"
	echo -e "$0 | \t./build_twblue.sh [-py32path <path to python for 32 bits> | -py64path <path for python on 64 bits> | -nsyspath <path to nsys> | -h]"
}

# parsing options from the command line
while [[ $# > 1 ]]
	do
	key="$1"
	shift

case $key in
	-py32path)
		pythonpath32="$1"
		shift
	;;
	-py64path)
		pythonpath64="$1"
		shift
	;;
	-nsispath)
		nsispath="$1"
		shift
	;;
		-help)
		help
	;;
	*)
	help
esac
done

cd ../src
if [ -d build/ ];
	then
	rm -rf build
fi
if [ -d dist/ ];
	then
	rm -rf dist
fi
$pythonpath32/python.exe "setup.py" "py2exe" "--quiet"
mv -f dist ../scripts/TWBlue
rm -rf build
$pythonpath64/python.exe "setup.py" "py2exe" "--quiet"
mv -f dist ../scripts/TWBlue64
rm -rf build
cd ../scripts
$nsispath/Unicode/makensis.exe "twblue.nsi"
rm -rf TWBlue
rm -rf TWBlue64