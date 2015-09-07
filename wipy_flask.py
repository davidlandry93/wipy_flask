#!/usr/bin/env python

import argparse
import mimetypes
from flask import Flask,  redirect, render_template, g,  request
import wipy


def guess_type(path):
    guess = mimetypes.guess_type(path)
    if guess is None:
        guess = ('application/octet-stream', None)
    return guess[0]

app = Flask(__name__)

@app.before_request
def before_request():
    g.repo = wipy.WipyRepository(app.config['WIPY_CONFIG'])

@app.after_request
def after_request(response):
    return response

@app.teardown_request
def teardown_request(exception):
    pass

@app.route('/')
def domain_index():
    return redirect('/w/index')

@app.route('/w/')
def wiki_index():
    return redirect('/w/index')

@app.route('/w/<path:page_name>')
def wiki_page(page_name):
    return render_template('page.html', **g.repo.dictionaries[page_name])

@app.route('/w/<path:page_name>/edit', methods=['GET', 'POST'])
def edit_wiki_page(page_name):
    if request.method == 'GET':
        return render_template('edit.html', **g.repo.dictionaries[page_name])
    elif request.method == 'POST':
        text = request.form['raw']
        g.repo.update(page_name, text)

        dictionary = g.repo.dictionaries[page_name]
        dictionary.update(save_success=True)
        return render_template('edit.html', **dictionary)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', type=bool, default=False)
    parser.add_argument('config', type=str)
    ns = parser.parse_args()

    app.config['WIPY_CONFIG'] = ns.config
    app.config['DEBUG'] = ns.debug
    app.run()
