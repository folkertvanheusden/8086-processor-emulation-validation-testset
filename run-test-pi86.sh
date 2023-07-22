#! /bin/bash

function function_generate() {
	./generate

	for i in test/*.asm
	do
		BASE=`echo $i | sed -e 's/.asm$//g'`

		as86 -0 -l ${BASE}.list -m -b ${BASE}.bin $i
	done
}

# function_generate

cd pi86-verify
mkdir build
(cd build && cmake .. && make -j)

for i in ../test/*.bin
do
	echo -n "$i - "

	./build/verify-with-pi86 $i
done
