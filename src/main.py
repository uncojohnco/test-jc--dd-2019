#!/usr/bin/env python3

import os
import sys
import doctest

import lss.lsseq


def main():

    if len(sys.argv) == 1:
        # Current dir if no arg is specified
        arg = '.'
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
    else:
        print('Usage:', __file__, '/path/to/dir')

    # TODO: implement optparse...

    if arg == '--test':
        # Test the module function using the inline example of the comments.

        doctest.testmod()
        print('Finished testing!')
    else:

        arg = os.path.abspath(arg)

        if os.path.isdir(arg):
            result = lss.lsseq.run(arg)
            print(result)
        else:
            print('Not a directory', arg)
            sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
