# Test for pyexiftool non-ASCII filename handling
import os
import sys
import tempfile
import shutil
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import helper
from elodie.external.pyexiftool import ExifTool, fsencode

def test_fsencode_with_non_ascii_characters():
    """Test that fsencode properly handles non-ASCII characters in filenames.
    
    This test reproduces issue #379 where Elodie crashes when encountering
    files with non-ASCII characters in their paths on systems with limited
    filesystem encodings (like Windows with cp1252).
    """
    test_filename = "/tmp/test_фото_сад/тест_файл.jpg"
    
    # Test 1: Should work fine with UTF-8 encoding (current behavior on macOS/Linux)
    encoded = fsencode(test_filename)
    assert isinstance(encoded, bytes)
    assert len(encoded) > 0
    
    # Test 2: Simulate problematic encoding scenario (Windows with cp1252)
    # This simulates the conditions that cause issue #379
    with patch('sys.getfilesystemencoding', return_value='cp1252'):
        with patch('codecs.lookup_error') as mock_lookup:
            # Simulate that surrogateescape is not available (old Python versions)
            mock_lookup.side_effect = LookupError("surrogateescape not available")
            
            # Re-import to pick up the mocked encoding
            import importlib
            from elodie.external import pyexiftool
            importlib.reload(pyexiftool)
            
            # This should raise UnicodeEncodeError with the original code
            # but should work with the fix
            try:
                encoded = pyexiftool.fsencode(test_filename)
                # If we get here, the fix is working
                assert isinstance(encoded, bytes)
                assert len(encoded) > 0
                print("✓ Fix is working - non-ASCII encoding successful")
            except UnicodeEncodeError as e:
                # This is the expected failure with the original code
                pytest.fail(f"fsencode failed with non-ASCII characters: {e}")

def test_exiftool_with_non_ascii_file():
    """Test that ExifTool can process files with non-ASCII characters in paths.
    
    This is an integration test that reproduces the specific JSON parsing error
    from issue #379.
    """
    # Create a temporary file with non-ASCII characters in the path
    test_dir = "/tmp/test_фото_сад"
    test_file = os.path.join(test_dir, "тест_файл.jpg")
    
    # Get a real test image using helper function
    source_file = helper.get_file('with-album.jpg')
    
    assert source_file, "Test image file not found - helper.get_file('with-album.jpg') returned None"
    
    try:
        os.makedirs(test_dir, exist_ok=True)
        shutil.copy2(source_file, test_file)
        
        # Use the test-session ExifTool process from conftest.py.
        result = ExifTool().execute_json(test_file)
        assert isinstance(result, list)
        assert len(result) > 0
        assert "SourceFile" in result[0]
            
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(test_dir):
            os.rmdir(test_dir)

def test_get_metadata_returns_none_when_execute_json_fails():
    """get_metadata() should not crash when execute_json returns None."""
    et = ExifTool()
    with patch.object(et, 'execute_json', return_value=None):
        result = et.get_metadata("/tmp/test.jpg")
        assert result is None

def test_get_metadata_returns_none_when_execute_json_is_empty():
    """get_metadata() should not crash when execute_json returns an empty list."""
    et = ExifTool()
    with patch.object(et, 'execute_json', return_value=[]):
        result = et.get_metadata("/tmp/test.jpg")
        assert result is None

def test_terminate_handles_broken_stdin_pipe():
    class FakeStdin(object):
        def write(self, data):
            return len(data)

        def flush(self):
            raise OSError(22, "Invalid argument")

    class FakeProcess(object):
        def __init__(self):
            self.stdin = FakeStdin()
            self.stdout = None
            self.stderr = None

        def poll(self):
            return None

        def terminate(self):
            return None

        def communicate(self):
            return (b"", b"")

    class FakeExifTool(object):
        def __init__(self):
            self.running = True
            self._process = FakeProcess()

        def _is_pipe_io_error(self, error):
            return ExifTool._is_pipe_io_error(self, error)

        def _cleanup_process(self):
            return ExifTool._cleanup_process(self)

    fake = FakeExifTool()
    ExifTool.terminate(fake)

    assert fake.running is False

def test_execute_returns_empty_when_stdin_pipe_is_invalid():
    class FakeStdin(object):
        def write(self, data):
            return len(data)

        def flush(self):
            raise OSError(22, "Invalid argument")

    class FakeStdout(object):
        def fileno(self):
            return 0

    class FakeProcess(object):
        def __init__(self):
            self.stdin = FakeStdin()
            self.stdout = FakeStdout()
            self.stderr = None

        def poll(self):
            return None

    class FakeExifTool(object):
        def __init__(self):
            self.running = True
            self._process = FakeProcess()

        def _is_pipe_io_error(self, error):
            return ExifTool._is_pipe_io_error(self, error)

        def start(self):
            self._process = FakeProcess()
            self.running = True

        def _cleanup_process(self):
            return ExifTool._cleanup_process(self)

        def _ensure_running(self):
            return ExifTool._ensure_running(self)

    fake = FakeExifTool()
    result = ExifTool.execute(fake, b"-ver")

    assert result == b""
    assert fake.running is False

def test_execute_restarts_after_pipe_error():
    class FakeStdinBroken(object):
        def write(self, data):
            return len(data)

        def flush(self):
            raise OSError(22, "Invalid argument")

        def close(self):
            return None

    class FakeStdinOk(object):
        def write(self, data):
            return len(data)

        def flush(self):
            return None

        def close(self):
            return None

    class FakeStdout(object):
        def __init__(self, fd_value):
            self.fd_value = fd_value

        def fileno(self):
            return self.fd_value

        def close(self):
            return None

    class FakeProcess(object):
        def __init__(self, stdin, stdout):
            self.stdin = stdin
            self.stdout = stdout
            self.stderr = None

        def poll(self):
            return None

    class FakeExifTool(object):
        def __init__(self):
            self.running = False
            self._start_calls = 0
            self._processes = [
                FakeProcess(FakeStdinBroken(), FakeStdout(1001)),
                FakeProcess(FakeStdinOk(), FakeStdout(1002)),
            ]

        def start(self):
            self._process = self._processes[self._start_calls]
            self._start_calls += 1
            self.running = True

        def _is_pipe_io_error(self, error):
            return ExifTool._is_pipe_io_error(self, error)

        def _cleanup_process(self):
            return ExifTool._cleanup_process(self)

        def _ensure_running(self):
            return ExifTool._ensure_running(self)

    fake = FakeExifTool()

    def fake_read(fd, blocksize):
        assert fd == 1002
        return b'ok\n{ready}'

    with patch('elodie.external.pyexiftool.os.read', side_effect=fake_read):
        result = ExifTool.execute(fake, b'-ver')

    assert result == b'ok\n'
    assert fake._start_calls == 2
    assert fake.running is True
