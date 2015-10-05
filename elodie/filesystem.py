import os
import time

class FileSystem:
    def get_all_files(self, pattern, extensions=None):
        files = []
        for dirname, dirnames, filenames in os.walk(pattern):
            # print path to all filenames.
            for filename in filenames:
                if(extensions == None or filename.lower().endswith(extensions)):
                    files.append('%s/%s' % (dirname, filename))
        return files

    def get_current_directory(self):
        return os.getcwd()

    def get_file_name_for_video(self, video):
        if(not video.is_valid()):
            return None

        metadata = video.get_metadata()
        if(metadata == None):
            return None

        file_name = '%s-%s.%s' % (time.strftime('%Y-%m-%d-%H-%M', metadata['date_taken']), metadata['base_name'], metadata['extension'])
        return file_name

    def get_folder_name_by_date(self, time_obj):
        return time.strftime('%Y-%m-%b', time_obj)

    def create_directory(self, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(dest_directory)
