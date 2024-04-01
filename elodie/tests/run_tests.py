#!/usr/bin/env python

import nose
import os
import shutil
import sys
import tempfile

if __name__ == "__main__":
    # test_directory is what we pass nose.run for where to find tests
    test_directory = os.path.dirname(os.path.abspath(__file__))

    # create a temporary directory to use for the application directory while running tests
    temporary_application_directory = tempfile.mkdtemp('-elodie-tests')
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = temporary_application_directory

    # copy config.ini-sample over to the test application directory
    temporary_config_file_sample = '{}/config.ini-sample'.format(os.path.dirname(os.path.dirname(test_directory)))
    temporary_config_file = '{}/config.ini'.format(temporary_application_directory)
    shutil.copy2(
        temporary_config_file_sample,
        temporary_config_file,
    )

    # read the sample config file and store contents to be replaced
    with open(temporary_config_file_sample, 'r') as f:
        config_contents = f.read()

    # set the mapquest key in the temporary config file and write it to the temporary application directory
    config_contents = config_contents.replace('your-api-key-goes-here', os.environ['MAPQUEST_KEY'])
    with open(temporary_config_file, 'w+') as f:
        f.write(config_contents)

    test_argv = sys.argv
    test_argv.append('--verbosity=2')
    result = nose.run(argv=test_argv)
    if(result):
        sys.exit(0)
    else:
        sys.exit(1)
