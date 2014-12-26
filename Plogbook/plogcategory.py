from datetime import datetime
import os


class PlogCategory:
    """
    Storage and management class for plog category.
    """

    def __init__(self, name, location, plog_files=None):
        """
        :param name: category name.
        :param location: location of the category on the hard-drive.
        :param plog_files: list of plog_file the category contains. If None will find plogs itself in "location".
        :return:
        """
        self.name = name
        self.location = location
        self.plog_files = plog_files or PlogBook.find_plogs(location)
        self.plog_count = len(self.plog_files)
        self.creation_date = self.get_date()

    def get_date(self):
        """finds the date when category was created"""
        meta = os.stat(self.location)
        date = meta.st_ctime
        date = datetime.fromtimestamp(date)
        date = date.strftime('%x %X')
        return date

    def __str__(self, pretty=False):
        if pretty:
            name = self.name.center(30, ' ')
            plog_count = str(self.plog_count).center(15, ' ')
            date = self.creation_date.center(30, ' ')
            return u'{}|{}|{}'.format(name, plog_count, date)
        else:
            return u'{};{};{}'.format(self.name, self.plog_count, self.creation_date)
