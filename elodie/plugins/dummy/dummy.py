"""
Dummy plugin object used for tests.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function
from builtins import object


class Dummy(object):
    """A dummy class to execute plugin actions for tests."""
    def __init__(self):
        self.before_ran = False

    def before(self, file_path, destination_path, media):
        self.before_ran = True

