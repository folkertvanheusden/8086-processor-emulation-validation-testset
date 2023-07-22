#! /bin/bash

function function_generate() {
	echo Generate test set assembly code...
	./generate.sh

	echo Translating assembly code to binary...
	for i in test/*.asm
	do
		BASE=`echo $i | sed -e 's/.asm$//g'`

		as86 -0 -l ${BASE}.list -m -b ${BASE}.bin $i
	done
}

# function_generate

echo Compiling validation tool...
cd pi86-verify
mkdir build
(cd build && cmake .. && make -j)

echo Running test set...
for i in ../test/*.bin
do
	echo -n "$i - "

	./build/verify-with-pi86 $i
done
