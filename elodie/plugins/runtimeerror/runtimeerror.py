"""
RuntimeError plugin object used for tests.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function

from elodie.plugins.plugins import PluginBase

class RuntimeError(PluginBase):

    __name__ = 'ThrowError'

    """A dummy class to execute plugin actions for tests."""
    def __init__(self):
        pass

    def before(self, file_path, destination_folder, media):
        print(does_not_exist)

