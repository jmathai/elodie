#!/usr/bin/env python

import nose
import os
import sys

if __name__ == "__main__":
    test_directory = os.path.dirname(os.path.abspath(__file__))
    test_argv = sys.argv
    test_argv.append('--verbosity=2')
    result = nose.run(argv=test_argv)
    if(result):
        sys.exit(0)
    else:
        sys.exit(1)
