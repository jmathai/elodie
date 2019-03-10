from __future__ import print_function


import os
import sys

import zerorpc

import elodie_cli

class ElodieApi(object):
    @zerorpc.stream
    def import_files(self, destination, source):
        """about any text"""
        # def _import(destination, source, file, album_from_folder, trash, allow_duplicates, debug, paths):
        return elodie_cli._import(
            destination,
            source, 
            False,
            False,
            False,
            True,
            True,
            []
        )


def parse_port():
    port = 4242
    try:
        port = int(sys.argv[1])
    except Exception as e:
        pass
    return '{}'.format(port)

def main():
    addr = 'tcp://127.0.0.1:' + parse_port()
    s = zerorpc.Server(ElodieApi())
    s.bind(addr)
    print('start running on {}'.format(addr))
    s.run()

if __name__ == '__main__':
    main()
