import glob
import os
import time

class FileSystem:
    def get_current_directory(self):
        return os.getcwd()

    def get_file_name_for_video(self, video):
        if(not video.is_valid()):
            return None

        metadata = video.get_metadata()
        if(metadata == None):
            return None

        file_name = '%s-%s-%s.%s' % (time.strftime('%d-%H-%M', metadata['date_taken']), metadata['base_name'], metadata['length'].replace(':', '-'), metadata['extension'])
        return file_name

    def get_folder_name_by_date(self, time_obj):
        return time.strftime('%Y-%m', time_obj)


    def create_directory(self, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(dest_directory)



