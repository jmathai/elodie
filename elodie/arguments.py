"""
"""
import sys, getopt
from re import sub

def parse(argv, options, long_options, usage):
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
