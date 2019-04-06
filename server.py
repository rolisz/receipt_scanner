import base64
import os
import io
import re
import sqlite3
from io import BytesIO

from PIL import Image
from flask import Flask, render_template, request, g, jsonify
from google.cloud import vision
from google.cloud.vision import types

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

    company = receipt_data['company']
    address = receipt_data['address']
    total = receipt_data['total']
    date = receipt_data['date']

    cursor = db.cursor()
    cursor.execute('INSERT INTO Receipts(company, address, total, date) VALUES(?,?,?,?)',
                   (company, address, total, date))

    receipt_id = cursor.lastrowid

    for item in receipt_data['items']:
        name = item['name']
        qty = item['qty']
        price = item['price']
        unit_price = item['unit_price']

        cursor.execute('INSERT INTO Items(name, qty, unit_price, price) VALUES(?,?,?,?)',
                       (name, qty, unit_price, price))
        item_id = cursor.lastrowid

        cursor.execute('INSERT INTO ReceiptItems(receipt_id, item_id) VALUES(?,?)', (receipt_id, item_id))

    db.commit()


@app.route('/')
def hello_world():
    return render_template('hello.html')


@app.route('/upload', methods=['POST'])
def upload_photo():
    if request.method == 'POST':
        image_data = re.sub('^data:image/.+;base64', '', request.form['image'])

        buffer = BytesIO(base64.b64decode(image_data))

        try:
            im = Image.open(buffer, 'r')

            filename = get_random_filename() + '.jpeg'
            app.logger.info('saving image to ' + filename)
            im.save('pictures/' + filename)

            # here we make a call to google vision API
            data = get_fake_json()

            # insert into DB
            persist_results(data)

            with io.open(filename, 'rb') as image_file:
                content = image_file.read()

            image = types.Image(content=content)

            # Performs label detection on the image file
            response = client.text_detection(image=image)
            print(response.text_annotations[0].description)

            return jsonify(data), 200
        except Exception as e:
            app.logger.error(e)
            return jsonify(get_error('invalid image')), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
