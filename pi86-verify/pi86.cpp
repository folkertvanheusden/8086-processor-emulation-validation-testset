#include <stdio.h>
#include <fstream> 
#include <unistd.h>
#include <thread>
#include "x86.h"


int main(int argc, char* argv[])
{
	Load_Bios(argv[1]);

	///////////////////////////////////////////////////////////////////
	//Change this Start(V30); 8086 or Start(V20); 8088 to set the processor
	///////////////////////////////////////////////////////////////////
	auto history = Start(V20);

	if (argc == 3) {
		FILE *fh = fopen(argv[2], "w");

		for(auto & record : history.first) {
			if (record.write)
				fprintf(fh, "WRITE %04x %02x\n", record.address, record.value);
			else
				fprintf(fh, "READ %04x %02x\n", record.address, record.value);
		}

		fclose(fh);
	}
	
	return history.second ? 0 : 1;
}
