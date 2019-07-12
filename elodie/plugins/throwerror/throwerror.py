"""
ThrowError plugin object used for tests.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function

from elodie.plugins.plugins import PluginBase, ElodiePluginError

class ThrowError(PluginBase):

    __name__ = 'ThrowError'

    """A dummy class to execute plugin actions for tests."""
    def __init__(self):
        pass

    def after(self, file_path, destination_folder, final_file_path, metadata):
        raise ElodiePluginError('Sample plugin error for after')

    def batch(self):
        raise ElodiePluginError('Sample plugin error for batch')

    def before(self, file_path, destination_folder):
        raise ElodiePluginError('Sample plugin error for before')
