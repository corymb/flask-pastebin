import pickle
from datetime import datetime
from base64 import urlsafe_b64encode
from os import urandom
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_redis import Redis

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'i\xd4z\x05\x88k&\xf8r\x93-Q\x07&\x16\xdf\xc4gw\xb1\x96\xa2%m'

r = Redis(app)


def add_suffix(date):
    """ Takes a number (string) and returns it with the correct suffix. """
    return 'th' if 11 <= date <= 13 else {
            1: 'st', 2: 'nd', 3: 'rd'}.get(date % 10, 'th')


# Jinja2 doesn't come with a date filter as standard:
@app.template_filter('format_date')
def format_date(date):
    """ Takes a date object; returns a formatted string (
    complete with suffixes, yo!) """
    return date.strftime('%A, {S} %B %Y at %I:%M%p').replace(
            '{S}', str(date.day) + add_suffix(date.day))


class Paste(object):
    def __init__(self, content, id=None, private=False):
        self.id = id if id else self.generate_digest()
        self.content = content
        self.upload_date = datetime.now()
        self.private = private

    def get_digest(self):
        """ Generates an 8 character, base 64, alphanumeric and url-safe
        digest. """
        return urlsafe_b64encode(urandom(10))[:8]

    def generate_digest(self):
        """ Checks it isn't already being stored in Redis. """
        digest = self.get_digest()
        while r.exists(digest):
            digest = self.generate_digest()
        return digest

    def pickle_object(self):
        return pickle.dumps(self)

    def __repr__(self):
        return '<%s - %s>' % (self.id, format_date(self.upload_date))


def save_paste(paste):
    # TODO: Add error handling for when Redis is down. Use
    # redis.exceptions.ConnectionError
    if not r.set(paste.id, paste.pickle_object()):
        flash('Something went wrong while saving - please try again later.')
    r.set(paste.id, paste.pickle_object())
    return paste


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        paste = Paste(request.form.get('paste'))
        paste = save_paste(paste)
        return redirect(url_for('view_paste', id=paste.id))
    return render_template('home.html', paste=None)


@app.route('/<id>/', methods=['GET', 'POST'])
def view_paste(id):
    paste = pickle.loads(r.get(id))
    if request.method == 'POST':
        paste = Paste(request.form.get('paste'), paste.id)
        paste = save_paste(paste)
    return render_template('home.html', paste=paste)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
