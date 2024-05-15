from app import app
from flask import render_template

@app.route('/')

@app.route('/index')
def index():
    return render_template('index.html.jinja')



@app.route('/about')
def about():
    return render_template('about.html.jinja')
@app.route('/home')
def home():
    return render_template('base.html.jinja')
@app.route('/extract')
def extract():
    return render_template('extract.html.jinja')
@app.route('/list')
def list():
    return render_template('list.html.jinja')