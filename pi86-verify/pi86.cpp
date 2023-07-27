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
			const char *action = "?";

			if (record.action == history_t::m_read)
				action = "MREAD";
			else if (record.action == history_t::io_read)
				action = "IOREAD";
			else if (record.action == history_t::m_write)
				action = "MWRITE";
			else if (record.action == history_t::io_write)
				action = "IOWRITE";

			fprintf(fh, "%s %04x %02x\n", action, record.address, record.value);
		}

		fclose(fh);
	}
	
	return history.second ? 0 : 1;
}
