#include <stdio.h>
#include <fstream> 
#include <unistd.h>
#include <thread>
#include "x86.h"


int main(int argc, char* argv[])
{
	Load_Bios(argv[1]);

	bool verbose = argc == 3;
	
	///////////////////////////////////////////////////////////////////
	//Change this Start(V30); 8086 or Start(V20); 8088 to set the processor
	///////////////////////////////////////////////////////////////////
	Start(V20, verbose);
	
	return 0;
}

