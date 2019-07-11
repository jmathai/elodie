#!/usr/bin/env python

import nose
import os
import shutil
import sys
import tempfile

if __name__ == "__main__":
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = tempfile.mkdtemp('-elodie-test')
    os.environ['ELODIE_MAPQUEST_KEY'] = 'x8wQLqGhW7qK3sFpjYtVTogVtoMK0S8s'
    print('Application Directory: {}'.format(os.environ['ELODIE_APPLICATION_DIRECTORY']))

    project_root = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
    shutil.copy2(
        '{}/config.ini-sample'.format(project_root),
        '{}/config.ini'.format(os.environ['ELODIE_APPLICATION_DIRECTORY'])
    )
    test_directory = os.path.dirname(os.path.abspath(__file__))
    test_argv = sys.argv
    test_argv.append('--verbosity=2')
    result = nose.run(argv=test_argv)
    if(result):
        sys.exit(0)
    else:
        sys.exit(1)
