#! /bin/bash

function assemble_one() {
	BASE=`echo $1 | sed -e 's/.asm$//g'`

	as86 -0 -l ${BASE}.list -m -b ${BASE}.bin $1
}

function function_generate() {
	./generate.sh

	export -f assemble_one
	parallel assemble_one ::: test/*.asm
}

function_generate

cd pi86-verify
mkdir build
(cd build && cmake .. && make -j)

for i in ../test/*.bin
do
	echo -n "$i - "

	BASE=`echo $i | sed -e 's/.bin$//g'`

	./build/verify-with-pi86 $i ${BASE}.log
done
