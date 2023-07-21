8088/8086 emulation validation
------------------------------

what it is
----------
This software tries to verify the emulation of an Intel 8086/8088 processor.
It does this by producing a few gigabytes of assembly-code. This assembly-
code shall then be runned on the emulator under test.


how it works
------------
Each assembly file is a self-contained group of tests. If you assemble each
assembly-file with a listing, then you should be able to pinpoint where it
went wrong.


how to generate
---------------
Run:

    ./generate.sh

This creates a directory 'tests' with all the assembly files in it.

Note that there are also 2 bin-files in the current (!) directory if all
went well. That's because far-jmp/calls need special handling. For these
to be produced successfully, you need 'as86' in the path (on Debian and
Ubuntu linux as86 can be found in the bin86 package).


how to run
----------
After you've assembled a .bin-file, load it into memory at 0x0000 and
start running at 0x0800. They should all finish in a fraction of a second.
Assembling should be done with 'as86 -0' to make sure it uses 8086
instructions.

When successfully executed, 0xa5ee in the SI register and then HLT is
invoked. A failed test only runs HLT at some point.


bugs
----
If you find any bugs or any other problems with this test-set, please
contact me at mail@vanheusden.com


notes
-----
This test set is not entirely complete yet (July 20, 2023).

Also this version ignores the upper 4 bit of the flags-register: they are
specified to undefined (in practice they're 1). On the other hand bit 1
and 5 *are* checked. This inconsistency must (will) be fixed.

run\_tests.py is a convenience script for testing the DotXT emulator.

BCD testing (bcd.py) is not finished.


license
-------
This testset is released in the public domain.

(C) 2023 by Folkert van Heusden.
