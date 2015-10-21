from os import path

application_directory = '{}/.elodie'.format(path.expanduser('~'))
hash_db = '{}/hash.json'.format(application_directory)
script_directory = path.dirname(path.dirname(path.abspath(__file__)))
exiftool_config = '%s/configs/ExifTool_config' % script_directory
