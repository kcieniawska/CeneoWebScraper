from app import app
from flask import render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup
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

@app.route('/extract', methods=['POST','GET'])
def extract():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        # walidacja
        url = f"https://www.ceneo.pl/{product_id}"
        response = requests.get(url)
        if response.status_code == requests.codes['ok']: 
            page = BeautifulSoup(response.text, "html.parser")
            opinions_count = page.select_one("a.product-review__link > span")
            if opinions_count:
                return redirect(url_for('product',product_id=product_id))
            return render_template('extract.html.jinja', error="Produkt nie posiada opinii!")
        return render_template('extract.html.jinja', error="Produkt o podanym kodzie nie istnieje!")
    return render_template('extract.html.jinja')

@app.route('/list')
def list():
    return render_template('list.html.jinja')
@app.route('/product/<product_id>')
def product(product_id):
    return render_template('product.html.jinja', product_id=product_id)