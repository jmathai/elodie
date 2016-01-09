"""
Command line argument parsing for helper scripts.
"""

import getopt
import sys
from re import sub


def parse(argv, options, long_options, usage):
    """Parse command line arguments.

    :param list(str) argv: Arguments passed to the program.
    :param str options: String of characters for allowed short options.
    :param list(str) long_options: List of strings of allowed long options.
    :param str usage: Help text, to print in the case of an error or when
        the user asks for it.
    :returns: dict
    """
    try:
        opts, args = getopt.getopt(argv, options, long_options)
    except getopt.GetoptError:
        print usage
        sys.exit(2)

    return_arguments = {}
    for opt, arg in opts:
        if opt == '-h':
            print usage
            sys.exit()
        else:
            return_arguments[sub('^-+', '', opt)] = arg

    return return_arguments
