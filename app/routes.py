from app import app
from app import utils
from flask import render_template, request, redirect, url_for, flash, jsonify
import requests
import os
import json
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

@app.route('/extract', methods=['POST', 'GET'])
def extract():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        # Walidacja
        url = f"https://www.ceneo.pl/{product_id}"
        response = requests.get(url)
        if response.status_code == requests.codes.ok: 
            page = BeautifulSoup(response.text, "html.parser")
            opinions_count = page.select_one("a.product-review__link > span")
            if opinions_count:
                url = f"https://www.ceneo.pl/{product_id}#tab=reviews"
                all_opinions = []
                while url:
                    response = requests.get(url)
                    page = BeautifulSoup(response.text, "html.parser")
                    opinions = page.select("div.js_product-review")
                    for opinion in opinions:
                        single_opinion = {
                            key: utils.get_data(opinion, *value)
                            for key, value in utils.selectors.items()
                        }
                        all_opinions.append(single_opinion)
                    try:
                        url = "https://ceneo.pl" + page.select_one("a.pagination__next")["href"]
                    except TypeError:
                        url = None

                if not os.path.exists("app/data"):
                    os.mkdir("app/data")
                if not os.path.exists("app/data/opinions"):
                    os.mkdir("app/data/opinions")

                with open(f"app/data/opinions/{product_id}.json", "w", encoding="UTF-8") as jf:
                    json.dump(all_opinions, jf, indent=4, ensure_ascii=False)

                return redirect(url_for('product', product_id=product_id))
            else:
                return render_template('extract.html.jinja', error="Produkt nie posiada opinii!")
        else:
            return render_template('extract.html.jinja', error="Produkt o podanym kodzie nie istnieje!")
    else:
        return render_template('extract.html.jinja')

@app.route('/list')
def list():
    return render_template('list.html.jinja')

@app.route('/product/<product_id>')
def product(product_id):
    opinions_file = f"app/data/opinions/{product_id}.json"
    if os.path.exists(opinions_file):
        with open(opinions_file, "r", encoding="UTF-8") as jf:
            product_opinions = json.load(jf)
        return render_template('product.html.jinja', product=product_opinions, product_id=product_id)
    else:
        return render_template('product.html.jinja', error="Opinie dla tego produktu nie zostały znalezione!", product_id=product_id)
