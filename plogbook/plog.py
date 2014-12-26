from datetime import datetime
import os

from plogbook import utils



class Plog:
    """
    Storage and management class for a plog item.
    plog - is an .html file that is a table and contains title, date, category and log message
    """

    def __init__(self, location, category=None, title=None):
        """
        :param location: location of the plog on the hard-drive
        :param category: plog category, if not provided will be extracted from location
        :param title: name of the plog file
        """
        self.location = location
        self.title = title or os.path.split(self.location)[-1]
        self.category = category or os.path.split(os.path.split(self.location)[0])[-1]
        self.date = self.get_date()

    def __str__(self, pretty=False):
        if pretty:
            # location = '...' + self.location.ljust(80, ' ')[-77::] \
            #     if len(self.location) > 80 else self.location.ljust(80, ' ')
            # category = self.category.center(20, ' ')[:17] + '...' \
            #     if len(self.category) > 20 else self.category.center(20, ' ')
            # title = self.title.center(20, ' ')[:17] + '...' \
            #     if len(self.title) > 20 else self.title.center(20, ' ')
            # date = self.date.center(20, ' ')
            location = utils.truncate(self.location, 80, reverse=True)
            category = utils.truncate(self.category, 20)
            title = utils.truncate(self.title, 20)
            date = utils.truncate(self.date, 20)
            return u'{:<80}|{:^20}|{:^20}|{:^20}'.format(location, category, title, date)
        else:
            return u'{};{};{};{}'.format(self.location, self.category, self.title, self.date)

    def get_date(self):
        """finds the date when plog was created"""
        meta = os.stat(self.location)
        date = meta.st_ctime
        date = datetime.fromtimestamp(date)
        date = date.strftime('%x %X')
        return date


