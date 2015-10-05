"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Video package that handles all video operations
"""
import os
import time

"""
General file system methods
"""
class FileSystem:
    """
    Recursively get all files which match a path and extension.

    @param, path, string, Path to start recursive file listing
    @param, extensions, tuple, File extensions to include (whitelist)
    """
    def get_all_files(self, path, extensions=None):
        files = []
        for dirname, dirnames, filenames in os.walk(path):
            # print path to all filenames.
            for filename in filenames:
                if(extensions == None or filename.lower().endswith(extensions)):
                    files.append('%s/%s' % (dirname, filename))
        return files

    """
    Get the current working directory

    @returns, string
    """
    def get_current_directory(self):
        return os.getcwd()

    """
    Generate file name for a video using its metadata.

    @param, video, Video, A Video instance
    @returns, string or None for non-videos
    """
    def get_file_name_for_video(self, video):
        if(not video.is_valid()):
            return None

        metadata = video.get_metadata()
        if(metadata == None):
            return None

        file_name = '%s-%s.%s' % (time.strftime('%Y-%m-%d-%H-%M', metadata['date_taken']), metadata['base_name'], metadata['extension'])
        return file_name

    """
    Get date based folder name.

    @param, time_obj, time, Time object to be used to determine folder name.
    @returns, string
    """
    def get_folder_name_by_date(self, time_obj):
        return time.strftime('%Y-%m-%b', time_obj)

    """
    Create a directory if it does not already exist..

    @param, directory_name, string, A fully qualified path of the directory to create.
    """
    def create_directory(self, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(dest_directory)
