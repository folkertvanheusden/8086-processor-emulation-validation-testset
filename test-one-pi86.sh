#! /bin/bash

BASE=`echo $1 | sed -e 's/.asm$//g'`

as86 -0 -l ${BASE}.list -m -b ${BASE}.bin $1

echo Compiling validation tool...
(cd pi86-verify
mkdir build
cd build && cmake .. && make -j)

echo -n "$1 - "
./pi86-verify/build/verify-with-pi86 ${BASE}.bin ${BASE}.log

if [ $? -ne 0 ] ; then
	echo $i ${BASE}.log FAILED
fi
