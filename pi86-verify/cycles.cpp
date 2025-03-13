#include <stdio.h>
#include <fstream> 
#include <unistd.h>
#include <thread>
#include "x86.h"


extern unsigned char RAM[];
extern unsigned char IO[];

int main(int argc, char* argv[])
{
	Load_Bios(argv[1]);

	RAM[0x0805] = 9;
	RAM[0x0807] = 17;

	auto rc = Start(V20);
	if (std::get<1>(rc))
		printf("%s %d\n", argv[1], std::get<2>(rc));
	else
		printf("failed\n");

	return 0;
}
