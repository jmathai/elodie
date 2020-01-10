"""
The media module provides a base :class:`Media` class for media objects that
are tracked by Elodie. The Media class provides some base functionality used
by all the media types, but isn't itself used to represent anything. Its
sub-classes (:class:`~elodie.media.audio.Audio`,
:class:`~elodie.media.photo.Photo`, and :class:`~elodie.media.video.Video`)
are used to represent the actual files.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function

import os

# load modules
from elodie.external.pyexiftool import ExifTool
from elodie.media.base import Base

class Media(Base):

    """The base class for all media objects.

    :param str source: The fully qualified path to the video file.
    """

    __name__ = 'Media'

    d_coordinates = {
        'latitude': 'latitude_ref',
        'longitude': 'longitude_ref'
    }

    def __init__(self, source=None):
        super(Media, self).__init__(source)
        self.exif_map = {
            'date_taken': [
                'EXIF:DateTimeOriginal',
                'EXIF:CreateDate',
                'EXIF:ModifyDate'
            ]
        }
        self.camera_make_keys = ['EXIF:Make', 'QuickTime:Make']
        self.camera_model_keys = ['EXIF:Model', 'QuickTime:Model']
        self.album_keys = ['XMP-xmpDM:Album', 'XMP:Album']
        self.title_key = 'XMP:Title'
        self.latitude_keys = ['EXIF:GPSLatitude']
        self.longitude_keys = ['EXIF:GPSLongitude']
        self.latitude_ref_key = 'EXIF:GPSLatitudeRef'
        self.longitude_ref_key = 'EXIF:GPSLongitudeRef'
        self.original_name_key = 'XMP:OriginalFileName'
        self.set_gps_ref = True

    def get_album(self):
        """Get album from EXIF

        :returns: None or string
        """
        if(not self.is_valid()):
            return None

        exiftool_attributes = self.get_exiftool_attributes()
        if exiftool_attributes is None:
            return None

        for album_key in self.album_keys:
            if album_key in exiftool_attributes:
                return exiftool_attributes[album_key]

        return None

    def get_coordinate(self, type='latitude'):
        """Get latitude or longitude of media from EXIF

        :param str type: Type of coordinate to get. Either "latitude" or
            "longitude".
        :returns: float or None if not present in EXIF or a non-photo file
        """

        exif = self.get_exiftool_attributes()
        if not exif:
            return None

        # The lat/lon _keys array has an order of precedence.
        # The first key is writable and we will give the writable
        #   key precence when reading.
        direction_multiplier = 1.0
        for key in self.latitude_keys + self.longitude_keys:
            if key not in exif:
                continue

            # Cast coordinate to a float due to a bug in exiftool's
            #   -json output format.
            # https://github.com/jmathai/elodie/issues/171
            # http://u88.n24.queensu.ca/exiftool/forum/index.php/topic,7952.0.html  # noqa
            # Exception handling reason:
            #   If there is EXIF data with null values for lat/long, python gets angry
            #   that it cannot convert nothing to a float. Here, we cast the value to 0.0
            try:
                this_coordinate = float(exif[key])
            except ValueError:
                return None

            # TODO: verify that we need to check ref key
            #   when self.set_gps_ref != True
            if type == 'latitude' and key in self.latitude_keys:
                if self.latitude_ref_key in exif and \
                        exif[self.latitude_ref_key] == 'S':
                    direction_multiplier = -1.0
                return this_coordinate * direction_multiplier
            elif type == 'longitude' and key in self.longitude_keys:
                if self.longitude_ref_key in exif and \
                        exif[self.longitude_ref_key] == 'W':
                    direction_multiplier = -1.0
                return this_coordinate * direction_multiplier

        return None

    def get_exiftool_attributes(self):
        """Get attributes for the media object from exiftool.

        :returns: dict, or False if exiftool was not available.
        """
        source = self.source

        #Cache metadata results and use if already exists for media
        if(self.metadata is None):
            metadata = ExifTool().get_metadata(source)
            self.metadata = metadata
        else:
            metadata = self.metadata

        if not metadata:
            return False

        return metadata

    def get_camera_make(self):
        """Get the camera make stored in EXIF.

        :returns: str
        """
        if(not self.is_valid()):
            return None

        exiftool_attributes = self.get_exiftool_attributes()

        if exiftool_attributes is None:
            return None

        for camera_make_key in self.camera_make_keys:
            if camera_make_key in exiftool_attributes:
                return exiftool_attributes[camera_make_key]

        return None

    def get_camera_model(self):
        """Get the camera make stored in EXIF.

        :returns: str
        """
        if(not self.is_valid()):
            return None

        exiftool_attributes = self.get_exiftool_attributes()

        if exiftool_attributes is None:
            return None

        for camera_model_key in self.camera_model_keys:
            if camera_model_key in exiftool_attributes:
                return exiftool_attributes[camera_model_key]

        return None

    def get_original_name(self):
        """Get the original name stored in EXIF.

        :returns: str
        """
        if(not self.is_valid()):
            return None

        exiftool_attributes = self.get_exiftool_attributes()

        if exiftool_attributes is None:
            return None

        if(self.original_name_key not in exiftool_attributes):
            return None

        return exiftool_attributes[self.original_name_key]

    def get_title(self):
        """Get the title for a photo of video

        :returns: str or None if no title is set or not a valid media type
        """
        if(not self.is_valid()):
            return None

        exiftool_attributes = self.get_exiftool_attributes()

        if exiftool_attributes is None:
            return None

        if(self.title_key not in exiftool_attributes):
            return None

        return exiftool_attributes[self.title_key]

    def reset_cache(self):
        """Resets any internal cache
        """
        self.exiftool_attributes = None
        super(Media, self).reset_cache()

    def set_album(self, album):
        """Set album for a photo

        :param str name: Name of album
        :returns: bool
        """
        if(not self.is_valid()):
            return None

        tags = {self.album_keys[0]: album}
        status = self.__set_tags(tags)
        self.reset_cache()

        return status

    def set_date_taken(self, time):
        """Set the date/time a photo was taken.

        :param datetime time: datetime object of when the photo was taken
        :returns: bool
        """
        if(time is None):
            return False

        tags = {}
        formatted_time = time.strftime('%Y:%m:%d %H:%M:%S')
        for key in self.exif_map['date_taken']:
            tags[key] = formatted_time

        status = self.__set_tags(tags)
        self.reset_cache()
        return status

    def set_location(self, latitude, longitude):
        if(not self.is_valid()):
            return None

        # The lat/lon _keys array has an order of precedence.
        # The first key is writable and we will give the writable
        #   key precence when reading.
        tags = {
            self.latitude_keys[0]: latitude,
            self.longitude_keys[0]: longitude,
        }

        # If self.set_gps_ref == True then it means we are writing an EXIF
        #   GPS tag which requires us to set the reference key.
        # That's because the lat/lon are absolute values.
        if self.set_gps_ref:
            if latitude < 0:
                tags[self.latitude_ref_key] = 'S'

            if longitude < 0:
                tags[self.longitude_ref_key] = 'W'

        status = self.__set_tags(tags)
        self.reset_cache()

        return status

    def set_original_name(self, name=None):
        """Sets the original name EXIF tag if not already set.

        :returns: True, False, None
        """
        if(not self.is_valid()):
            return None

        # If EXIF original name tag is set then we return.
        if self.get_original_name() is not None:
            return None

        source = self.source

        if not name:
            name = os.path.basename(source)

        tags = {self.original_name_key: name}
        status = self.__set_tags(tags)
        self.reset_cache()
        return status

    def set_title(self, title):
        """Set title for a photo.

        :param str title: Title of the photo.
        :returns: bool
        """
        if(not self.is_valid()):
            return None

        if(title is None):
            return None

        tags = {self.title_key: title}
        status = self.__set_tags(tags)
        self.reset_cache()

        return status

    def __set_tags(self, tags):
        if(not self.is_valid()):
            return None

        source = self.source

        status = ''
        ExifTool().set_tags(tags,source)

        return status != ''
