import base64
import os
import io
import re
import sqlite3
from datetime import datetime
from io import BytesIO

from PIL import Image
from flask import Flask, render_template, request, g, jsonify
from google.cloud import vision
from google.cloud.vision import types

from image_processing import pipeline, get_word_items
from utils import get_fake_json, get_error, get_random_filename

DATABASE = './receipts.db'

client = vision.ImageAnnotatorClient()

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# init db
if not os.path.exists(DATABASE):
    app.logger.info("initializing DB...")
    with app.app_context():
        db = get_db()
        try:
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
        except sqlite3.DatabaseError as dbe:
            app.logger.error(dbe)


def persist_results(receipt_data):
    db = get_db()

    company = receipt_data.get('company', '')
    address = receipt_data.get('address', '')

    total = 0
    if 'total' in receipt_data:
        total = receipt_data['total']
    else:
        if len(receipt_data['items']):
            total = sum([x["price"] for x in receipt_data['items']])
    date = receipt_data.get('date', datetime.now())

    cursor = db.cursor()
    cursor.execute('INSERT INTO Receipts(company, address, total, date) VALUES(?,?,?,?)',
                   (company, address, total, date))

    receipt_id = cursor.lastrowid

    for item in receipt_data['items']:
        name = item["name"]
        price = item["price"]

        cursor.execute('INSERT INTO Items(name, price, receipt_id) VALUES(?,?,?)',
                       (name, price, receipt_id))
        item_id = cursor.lastrowid

    db.commit()


@app.route('/')
def hello_world():
    return render_template('hello.html')


def get_error(message):
    return {
        'error_message': message
    }


@app.route('/upload', methods=['POST'])
def upload_photo():
    image_data = re.sub('^data:image/.+;base64', '', request.form['image'])

    buffer = BytesIO(base64.b64decode(image_data))

    im = Image.open(buffer, 'r')

    filename = get_random_filename() + '.jpeg'
    app.logger.info('saving image to ' + filename)
    path = os.path.join("pictures", filename)
    im.save(path)
    words = pipeline(path)

    data = get_word_items(words)
    # insert into DB
    persist_results(data)

    return jsonify(data), 200

@app.route("/get_receipts")
def get_data():
    db = get_db()

    cursor = db.cursor()
    cursor.execute('SELECT id, company, address, total, date FROM Receipts')

    receipts = cursor.fetchall()
    print(receipts)
    cursor2 = db.cursor()
    cursor2.execute('SELECT id, receipt_id, name, price  FROM Items')
    items = cursor2.fetchall()
    data = []
    for receipt in receipts:
        d = {"id": receipt[0], "company": receipt[1], "address": receipt[2], "total": receipt[3], "date": receipt[4]}
        its = []
        for i in items:
            if i[1] == receipt[0]:
                its.append({"name": i[2], "price": i[3]})
        d["items"] = its
        data.append(d)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
