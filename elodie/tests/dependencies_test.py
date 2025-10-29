import unittest.mock as mock

from elodie.dependencies import get_exiftool


@mock.patch('elodie.dependencies.shutil')
@mock.patch('elodie.dependencies.os')
def test_exiftool(mock_os, mock_shutil):
    mock_shutil.which.return_value = '/path/to/exiftool'
    assert get_exiftool() == '/path/to/exiftool'

    mock_shutil.which.return_value = None
    mock_os.path.isfile.return_value = True
    mock_os.path.access.return_value = True
    assert get_exiftool() == '/usr/local/bin/exiftool'

    mock_os.path.isfile.return_value = False
    assert get_exiftool() is None
