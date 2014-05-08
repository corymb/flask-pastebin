# -*- coding:utf-8 -*-

import unittest
from datetime import datetime

import fakeredis
from mock import patch

from pastebin import add_suffix, format_date, Paste, save_paste


class DateTestCase(unittest.TestCase):

    def setUp(self):
        self.NON_TH_DATES = [1, 2, 3, 21, 22, 23, 31]

    # Helper functions:
    def create_date(self, date, hour=12):
        """ Takes an integer and returns a date object """
        return datetime(2014, 12, date, hour, 00, 00)

    def generate_th_dates(self):
        """ Returns all dates that should have a 'th' suffix. """
        date_list = range(1, 31)
        return [date for date in date_list if date not in self.NON_TH_DATES]

    def test_add_suffixes_th(self):
        """
        The following dates should have a 'th' suffix:
            ...
            - 4th
            - 5th
            - 6th
            - 7th
            - 8th
            - 9th
            - 10th
            - 11th
            - 12th
            - 13th
            - 14th
            - 15th
            - 16th
            - 17th
            - 18th
            - 19th
            - 20th
            ...
            - 24th
            - 25th
            - 26th
            - 27th
            - 28th
            - 29th
            - 30th
            ...
        """
        for date in self.generate_th_dates():
            assert add_suffix(date) == 'th'

    def test_incorrect_add_suffixes(self):
        """ Tests that 'th' suffix isn't applied to incorrect dates. """
        for date in self.NON_TH_DATES:
            assert add_suffix(date) != 'th'

    def test_th_format_date_object(self):
        for date in self.generate_th_dates():
            assert 'th' in format_date(self.create_date(date))

    def test_non_th_format_date(self):
        for date in self.NON_TH_DATES:
            assert 'th' not in format_date(self.create_date(date))

    def test_time_am(self):
        """ Tests that the string 'AM' is in formatted date when the time is
        before 12PM """
        date = self.create_date(date=1, hour=11)
        assert 'AM' in format_date(date)

    def test_time_pm(self):
        """ Tests that the string 'AM' is in formatted date when the time is
        after 12PM """
        date = self.create_date(date=1, hour=12)
        assert 'PM' in format_date(date)


@patch('pastebin.r', fakeredis.FakeStrictRedis())
class PasteClassTestCase(unittest.TestCase):
    """
    Battery of tests to check the functions surrounding the paste class
    """

    def setUp(self):
        self.paste = Paste(content='test')

    def test_generate_digest(self):
        """ Tests that Paste.generate_digest generates an 8 character string.
        """
        assert type(self.paste.generate_digest()) is str
        assert len(self.paste.generate_digest()) == 8

    def test_pickle_object(self):
        """ Tests that pickle_object returns a pickled object. """
        assert type(self.paste.pickle_object()) is str

    def test_pickle_object_content(self):
        """ Tests that pickle_object returns the correct data. """
        assert 'test' in self.paste.pickle_object()
        # assert  self.paste.generate_digest() in self.paste.pickle_object()

    def test_paste_hash(self):
        """ Tests that the paste's hash doesn't change when looked up. """
        pass


class RedisTestCase(unittest.TestCase):
    """ Tests Redis CRUD """
    def test_generate_unique_digest(self):
        """ Tests that an existing digest cannot be added into Redis. """
        digest = paste.generate_digest()


class PasteBinTestClass(unittest.TestCase):
    """ Tests for the Paste object. """


    def test_save_paste(self):
        """ Tests that a paste is saved in the DB """
        pass


class BrowserTestCase(unittest.TestCase):
    """ Tests browser interaction """
    pass

if __name__ == '__main__':
        unittest.main()
