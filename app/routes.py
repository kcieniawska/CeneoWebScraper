from app import app
from app import utils
from flask import render_template, request, redirect, url_for, flash, jsonify
import requests
import os
import json
import pandas as pd, numpy as np
from matplotlib import pyplot as plt
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
        url = f"https://www.ceneo.pl/{product_id}"
        response = requests.get(url)
        if response.status_code == requests.codes['ok']:
            page = BeautifulSoup(response.text, "html.parser")
            opinions_count = page.select_one("a.product-review__link > span")
            if opinions_count:
                product_name = utils.get_data(page,"h1")
                url = f"https://www.ceneo.pl/{product_id}#tab=reviews"
                all_opinions = []
                while(url):
                    print(url)
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
                        url = "https://ceneo.pl"+page.select_one("a.pagination__next")["href"]
                    except TypeError:
                        url = None
                if not os.path.exists("app/data"):
                    os.mkdir("app/data")
                if not os.path.exists("app/data/opinions"):
                    os.mkdir("app/data/opinions")
                jf = open(f"app/data/opinions/{product_id}.json", "w", encoding="UTF-8")
                json.dump(all_opinions, jf, indent=4, ensure_ascii=False)
                jf.close()
                opinions = pd.DataFrame.from_dict(all_opinions)
                opinions.stars = opinions.stars.apply(lambda s: s.split('/')[0].replace(',', '.')).astype(float)
                stats = {
                    "product_id": product_id,
                    "product_name": product_name,
                    "opinions_count": opinions.shape[0],
                    "pros_count": int(opinions.pros.astype(bool).sum()),
                    "cons_count": int(opinions.cons.astype(bool).sum()),
                    "average_stars": opinions.stars.mean(),
                    "stars_distr": opinions.stars.value_counts().reindex(np.arange(0,5.5,0.5), fill_value=0).to_dict(),
                    "recommendation_distr": opinions.recommendation.value_counts().reindex(["Polecam", "Nie polecam", None], fill_value=0).to_dict(),
                }
                if not os.path.exists("app/data/products"):
                    os.mkdir("app/data/products")
                jf = open(f"app/data/products/{product_id}.json", "w", encoding="UTF-8")
                json.dump(stats, jf, indent=4, ensure_ascii=False)
                jf.close()
                return redirect(url_for('product', product_id=product_id))
            return render_template('extract.html.jinja', error="Produkt o podanym kodzie nie posiada opinii.")
        return render_template('extract.html.jinja', error="Produkt o podanym kodzie nie istnieje.")
    return render_template('extract.html.jinja')

@app.route('/products')
def products():
    # Lista kodów produktów o których zostały pobrane opinie
    product_codes = [filename.split(".")[0] for filename in os.listdir('app/data/opinions')]

    # Jeśli nie ma opinii w ogóle
    if not product_codes:
        return render_template('products_empty.html.jinja')

    products = []

    # Dla każdego kodu produktu pobieramy dane statystyczne
    for product_code in product_codes:
        # Wczytanie danych z pliku JSON
        with open(f"app/data/products/{product_code}.json", "r", encoding="UTF-8") as jf:
            product_data = json.load(jf)
        
        # Dodanie danych do listy produktów
        products.append({
            'product_id': product_code,
            'product_name': product_data.get('product_name', ''),
            'opinions_count': product_data.get('opinions_count', 0),
            'pros_count': product_data.get('pros_count', 0),
            'cons_count': product_data.get('cons_count', 0),
            'average_stars': product_data.get('average_stars', 0),
            'stars_distr': product_data.get('stars_distr', {}),
            'recommendation_distr': product_data.get('recommendation_distr', {}),
        })

    return render_template('products.html.jinja', products=products)

    return render_template('products.html.jinja', products_list=products)

@app.route('/product/<product_id>')
def product(product_id):
    opinions_file = f"app/data/opinions/{product_id}.json"
    if os.path.exists(opinions_file):
        with open(opinions_file, "r", encoding="UTF-8") as jf:
            product_opinions = json.load(jf)
        return render_template('product.html.jinja', product=product_opinions, product_id=product_id)
    else:
        return render_template('product.html.jinja', error="Opinie dla tego produktu nie zostały znalezione!", product_id=product_id)
