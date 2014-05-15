# -*- coding:utf-8 -*-

import unittest
from datetime import datetime

import fakeredis
from mock import patch

import pastebin


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
            assert pastebin.add_suffix(date) == 'th'

    def test_incorrect_add_suffixes(self):
        """ Tests that 'th' suffix isn't applied to incorrect dates. """
        for date in self.NON_TH_DATES:
            assert pastebin.add_suffix(date) != 'th'

    def test_th_format_date_object(self):
        for date in self.generate_th_dates():
            assert 'th' in pastebin.format_date(self.create_date(date))

    def test_non_th_format_date(self):
        for date in self.NON_TH_DATES:
            assert 'th' not in pastebin.format_date(self.create_date(date))

    def test_time_am(self):
        """ Tests that the string 'AM' is in formatted date when the time is
        before 12PM """
        date = self.create_date(date=1, hour=11)
        assert 'AM' in pastebin.format_date(date)

    def test_time_pm(self):
        """ Tests that the string 'AM' is in formatted date when the time is
        after 12PM """
        date = self.create_date(date=1, hour=12)
        assert 'PM' in pastebin.format_date(date)

    def test_12_hour_clock(self):
        """ Tests that the modified time is in 12 hour format. """
        date = self.create_date(date=1, hour=13)
        assert '13' not in pastebin.format_date(date)

    def test_am_pm_spacing(self):
        """ Tests that there is no space between the time and AM/PM """
        date = self.create_date(date=1, hour=11)
        assert pastebin.format_date(date).endswith('00AM')
        date = self.create_date(date=1, hour=13)
        assert pastebin.format_date(date).endswith('00PM')


# This patches the Redis DB to use fakeredis:
@patch('pastebin.r', fakeredis.FakeStrictRedis())
class PasteClassTestCase(unittest.TestCase):
    """
    Battery of tests to check the functions surrounding the paste class
    """

    def test_generate_digest(self):
        """ Tests that Paste.generate_digest generates an 8 character string.
        """
        paste = pastebin.Paste(content='test')
        assert type(paste.generate_digest()) is str
        assert len(paste.generate_digest()) == 8

    def test_pickle_object(self):
        """ Tests that pickle_object returns a pickled object. """
        paste = pastebin.Paste(content='test')
        assert type(paste.pickle_object()) is str

    def test_pickle_object_content(self):
        """ Tests that pickle_object returns the correct data. """
        paste = pastebin.Paste(content='test')
        assert 'test' in paste.pickle_object()
        assert paste.id in paste.pickle_object()

    def test_paste_hash(self):
        """ Tests that the paste's id doesn't change when looked up.
        Don't ask. """
        paste = pastebin.Paste(content='test')
        paste_id = paste.id
        assert paste_id == paste.id


@patch('pastebin.r', fakeredis.FakeStrictRedis())
class RedisTestCase(unittest.TestCase):
    """ Tests Redis CRUD """

    def test_generate_unique_digest(self):
        """ Tests that if a randomly generated digest is already present in
        redis, a new one is generated. """

        # First, patch to return the same value each time:
        p = patch('pastebin.Paste.get_digest', new=lambda x: 'ANzC4eGQ')
        p.start()

        paste_1 = pastebin.Paste(content='test')
        pastebin.save_paste(paste_1)

        # Recursive function call should exceed stack limit:
        try:
            paste_2 = pastebin.Paste(content='test 2')
        except RuntimeError, e:
            assert 'maximum recursion depth exceeded' in e.message

        # Check that the paste will save if the patch is stopped:
        p.stop()
        paste_2 = pastebin.Paste(content='test 2')
        pastebin.save_paste(paste_2)


@patch('pastebin.r', fakeredis.FakeStrictRedis())
class PasteBinTestClass(unittest.TestCase):
    """ Tests for the Paste object. """

    def test_save_paste(self):
        """ Tests that a paste is saved in the DB """
        pass

    def test_repr(self):
        """ Checks that the id and the upload date are present in __repr__()
        """
        paste = pastebin.Paste(content='test')
        assert paste.id in paste.__repr__()
        assert pastebin.format_date(paste.upload_date) in paste.__repr__()


@patch('pastebin.r', fakeredis.FakeStrictRedis())
class HttpTestCase(unittest.TestCase):
    """ Tests http interaction """

    def setUp(self):
        pastebin.app.config['TESTING'] = True
        self.app = pastebin.app.test_client()
        self.paste = 'Test Paste'
        self.updated_paste = 'Updated test paste'

    def test_get_upload(self):
        resp = self.app.get('/')
        # assert False, resp.data
        self.assertEqual(resp.status_code, 200)

    def test_post_redirect(self):
        """ Tests that posting a paste redirects to that paste """
        resp = self.app.post('/', {'paste': self.paste})
        self.assertEqual(resp.status_code, 302)
        resp = self.app.post('/', data={'paste': self.paste},
                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_post_paste(self):
        """ Tests that the content posted is the content that shows up """
        resp = self.app.post('/', data={'paste': self.paste},
                follow_redirects=True)
        self.assertIn(self.paste, resp.data)

    def test_edit_paste(self):
        """ Tests that an existing paste can be edited. """

        # First, check that self.post and self.updated_post aren't the same:
        self.assertNotEqual(self.paste, self.updated_paste)

        # Create initial post:
        resp = self.app.post('/', data={'paste': self.paste})

        # Flask doesn't set the location if you pass follow_redirects=True:
        url = resp.location

        # Load the page with the paste on it:
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.paste, resp.data)

        # Update initial post:
        resp = self.app.post(url, data={'paste': self.updated_paste},
                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.updated_paste, resp.data)


if __name__ == '__main__':
        unittest.main()
