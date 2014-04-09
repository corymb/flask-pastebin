import pickle
from datetime import datetime
from base64 import urlsafe_b64encode
from os import urandom
from flask import Flask, redirect, render_template, request, url_for
from flask_redis import Redis

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

r = Redis(app)


def add_suffix(date):
    # Function to add suffixes to dates:
    return 'th' if 11 <= date <= 13 else {
            1: 'st', 2: 'nd', 3: 'rd'}.get(date % 10, 'th')


# Jinja2 doesn't come with a date filter as standard:
@app.template_filter('format_date')
def format_date(date):
    return date.strftime('%A, {S} %B %Y | %H:%M %p').replace(
            '{S}', str(date.day) + add_suffix(date.day))


class Paste(object):
    def __init__(self, content, private=False):
        self.id = self.get_id()
        self.content = content
        self.upload_date = datetime.now()
        self.private = private

    def get_id(self):
        # TODO: Check id isn't already present in redis!
        return urlsafe_b64encode(urandom(10))[:8]

    def pickle_object(self):
        return pickle.dumps(self)

    def __repr__(self):
        return '<%s - %s>' % (self.id, format_date(self.upload_date))


def save_paste(paste):
    r.set(paste.id, paste.pickle_object())
    return paste.id


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        paste = Paste(request.form.get('paste'))
        paste_id = save_paste(paste)
        return redirect(url_for('view_paste', id=paste_id))
    return render_template('home.html')


@app.route('/<id>/')
def view_paste(id):
    paste = pickle.loads(r.get(id))
    assert False, paste
    return render_template('home.html', paste=paste)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
