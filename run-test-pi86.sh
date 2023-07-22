#! /bin/bash

function assemble_one() {
	BASE=`echo $1 | sed -e 's/.asm$//g'`

	as86 -0 -l ${BASE}.list -m -b ${BASE}.bin $1
}

function function_generate() {
	echo Generate test set assembly code...
	./generate.sh

	echo Translating assembly code to binary...
	export -f assemble_one
	parallel assemble_one ::: test/*.asm
}

#function_generate

echo Compiling validation tool...
cd pi86-verify
mkdir build
(cd build && cmake .. && make -j)

echo Running test set...
for i in ../test/*.bin
do
	BASE=`echo $i | sed -e 's/.bin$//g'`

	echo -n "$i - "

	./build/verify-with-pi86 $i ${BASE}.log
done
