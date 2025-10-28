#!/usr/bin/env python

import os
import shutil
import sys
import tempfile
import pytest

# Add the parent directories to sys.path so we can import elodie modules and test helpers
test_dir = os.path.dirname(os.path.abspath(__file__))
elodie_root = os.path.dirname(os.path.dirname(test_dir))
sys.path.insert(0, elodie_root)
sys.path.insert(0, test_dir)

from elodie.external.pyexiftool import ExifTool
from elodie.dependencies import get_exiftool
from elodie import constants


@pytest.fixture(scope="session", autouse=True)
def setup_exiftool():
    """Start ExifTool once for the entire test session."""
    exiftool_addedargs = [
        u'-config',
        u'"{}"'.format(constants.exiftool_config)
    ]
    exiftool = ExifTool(executable_=get_exiftool(), addedargs=exiftool_addedargs)
    exiftool.start()
    
    yield
    
    # Stop ExifTool after all tests complete
    try:
        exiftool.terminate()
    except:
        pass

@pytest.fixture(scope="function", autouse=True)
def setup_test_environment():
    """
    Set up the test environment before each test function.
    This creates a fresh temporary application directory and config file for each test.
    """
    # Get the test directory
    test_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Create a temporary directory to use for the application directory while running tests
    temporary_application_directory = tempfile.mkdtemp('-elodie-tests')
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = temporary_application_directory
    
    # Copy config.ini-sample over to the test application directory
    temporary_config_file_sample = '{}/config.ini-sample'.format(
        os.path.dirname(os.path.dirname(test_directory))
    )
    temporary_config_file = '{}/config.ini'.format(temporary_application_directory)
    shutil.copy2(
        temporary_config_file_sample,
        temporary_config_file,
    )
    
    # Read the sample config file and store contents to be replaced
    with open(temporary_config_file_sample, 'r') as f:
        config_contents = f.read()
    
    # Set the mapquest key in the temporary config file and write it to the temporary application directory
    # Check if MAPQUEST_KEY environment variable is set
    if 'MAPQUEST_KEY' in os.environ:
        config_contents = config_contents.replace('your-api-key-goes-here', os.environ['MAPQUEST_KEY'])
    else:
        # If not set, tests that require it will fail with a clear message
        config_contents = config_contents.replace('your-api-key-goes-here', 'test-key-not-set')
    
    with open(temporary_config_file, 'w+') as f:
        f.write(config_contents)
    
    # Yield control to tests
    yield
    
    # Cleanup after each test
    try:
        shutil.rmtree(temporary_application_directory)
    except OSError:
        pass  # Directory might already be cleaned up