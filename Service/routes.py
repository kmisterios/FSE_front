# -*- coding: utf-8 -*-
import os
from Service import app
from flask import render_template, flash, redirect, request, url_for, \
    session, send_from_directory, current_app, send_file
from werkzeug.utils import secure_filename
from Service.forms import LinkForm, GetSchemasForm, results_page_form

import requests
import numpy as np
import os
import time
import traceback


def allowed_file(filename):
    global ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def res_giver(query):
    res = {'query': query,
               'is_filter': 0,
               'total': 3,
               'hits': [
                   {'title': 'Title1', 'year': '1998', 'id': 1, 'abstract': 'text1',
                    'article_piece': 'Hello world, You\'re rock sucker.'},
                   {'title': 'Title2', 'year': '2005', 'id': 2, 'abstract': 'text1',
                    'article_piece': 'Hello world, You\'re sock sucker.'},
                   {'title': 'Title3', 'year': '2005', 'id': 3, 'abstract': 'text1',
                    'article_piece': 'Hello world, You\'re wok sucker.'}]}
    return res


def redirect_to_article(id_a, data):
    return redirect(url_for('/search/results/'+ str(id_a), data=data))


@app.route('/')
def route():
    return redirect('/search')


@app.route('/search')
def search():
    if request.method == 'POST':
        search_text = request.form.get('search_text')
        #session['search_text'] = search_text
        session['data'] = res_giver(search_text)
        return redirect(url_for('results'))#search_text=search_text))
    return render_template('search.html', title="Search")


@app.route('/search/results', methods=['GET', 'POST'])
def search_request(): #when we searching again from results page

    #search_text = request.args.get('search_text', None)
    res = session.get('data', None)
    print(res['query'])
    #print(search_text)
    # if search_text is not None:
    #     print('lol')
    #     res = res_giver(search_text)
    #     session['data'] = res
    # else:
    #     print('lolol')
    #     if 'data' in session.keys():
    #         res = session['data']
    #     else:
    #         res = res_giver(search_text)
    #         session['data'] = res
    #if request.method == 'POST':
        #search_text = request.form.get('search_text')
    search_text = request.form.get('search_text')
    print(search_text)
    if search_text != res['query'] and search_text is not None and search_text != '':
        res = res_giver(search_text)
        session['data'] = res
    return render_template('results.html', res=res)


@app.route('/search/results/<int:article_id>', methods=['GET'])
def show_article_info(article_id):
    data = session.get('data', None)
    article = [x for x in data['hits'] if x['id'] == article_id][0]
    return render_template('article_info.html', title="Article info", article=article)


@app.route('/search/results/<int:article_id>', methods=['POST'])
def download(article_id):
    uploads = os.path.join(current_app.root_path, 'Files', str(article_id)+'.pdf')
    print(uploads)
    return send_file(uploads)


# for rendering
@app.route('/schemas', methods=['GET', 'POST'])
def schemas():
    form = GetSchemasForm()
    if request.method == 'POST':
        if request.form['action'] == 'Read':
            return redirect('/schemas/schemas')
        elif request.form['action'] == 'Get':
            ids = form.id.data
            if len(ids) == 0:
                flash('YOU\'VE FORGOTTEN TO WRITE THE  ID OF THE SCHEMA')
                return redirect('/schemas')
            else:
                try:
                    int(ids)
                except:
                    flash('WRONG DATA')
                    return redirect('/schemas')
                return redirect('/schemas/schemas/' + ids)
        elif request.form['action'] == 'Upload':
            schema = form.newSchema.data
            if len(schema) == 0:
                flash('YOU\'VE FORGOTTEN TO WRITE THE SCHEMA')
                return redirect('/schemas')
            else:
                try:
                    schema = json.loads(schema)
                except:
                    flash('WRONG DATA')
                    return redirect('/schemas')
                path = 'Service/schemas.json'
                with open(path, 'w') as f:
                    json.dump(schemas, f)
                flash('YOUR SCHEMA IS SUCCESSFULLY WRITTEN')
                return redirect('/schemas')
        elif request.form['action'] == 'Delete':
            ids = form.idDelete.data
            if len(ids) == 0:
                flash('YOU\'VE FORGOTTEN TO WRITE THE  ID OF THE SCHEMA')
                return redirect('/schemas')
            else:
                try:
                    int(ids)
                except:
                    flash('WRONG DATA')
                    return redirect('/schemas')
                return redirect('/schemas/delete/' + ids)
    return render_template('schemas_base.html', title="Schemas_base", form=form)


@app.route('/requests/schemas', methods=['POST'])
def upload_schema():
    data = request.data
    return data


# for rendering
@app.route('/schemas/schemas', methods=['GET'])
def get_schemas():
    flash('dick')
    return render_template('schemas.html', title="Schemas")


# for rendering
@app.route('/schemas/delete/<int:schema_id>', methods=['GET'])
def delete_schema(schema_id):
    flash("id = " + str(schema_id))
    return render_template('article_info.html', title="Schema")


# for rendering
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = LinkForm()
    if request.method == 'POST':
        variant = int(form.link.data)
        flash(str(variant+8))
        return redirect('/verify')
    return render_template('home.html', title='Home', form=form)


@app.route('/go')
def go():
    return redirect('/verify')


# for rendering
@app.route('/verify', methods=['GET', 'POST'])
def link():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            redirect('/verify')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect('/verify')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
        text = json.loads(file.read())
        flash(text)
        return redirect('/index')
    return render_template('verify.html', title='Enter your json:')


# for rendering
@app.route('/index')
def index():
    return render_template('index.html', title='Results')
