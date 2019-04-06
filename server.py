import base64
import io
import re
from io import BytesIO
import logging

from flask import Flask, render_template, request, json, jsonify
from PIL import Image

from google.cloud import vision
from google.cloud.vision import types

client = vision.ImageAnnotatorClient()


app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('hello.html')


def get_fake_json():
    content = {
        'id': 1,
        'company': 'SC DEDEMAN SRL',
        'address': 'Calea Aradului NR 87A JUD BIHOR',
        'items': [
            {
                'name': 'CABLU MYYM',
                'qty': '30 M',
                'unit_price': 4.09,
                'price': 122.7
            },
            {
                'name': 'FISA 2P+T',
                'qty': '1 BUC',
                'unit_price': 9.59,
                'price': 9.59
            },
            {
                'name': 'PRIZA MOBILA',
                'qty': '1 BUC',
                'unit_price': 16.99,
                'price': 16.99
            }
        ],
        'total': 149.28,
        'date': '02-04-2019T14:51:47'
    }

    return jsonify(content)


def get_error(message):
    return jsonify({
        'error_message': message
    })


@app.route('/upload', methods=['POST'])
def upload_photo():
    if request.method == 'POST':
        image_data = re.sub('^data:image/.+;base64', '', request.form['image'])

        buffer = BytesIO(base64.b64decode(image_data))

        im = Image.open(buffer, 'r')
        b = BytesIO()
        im.save(open("image.jpeg", "wb"))

        with io.open("image.jpeg", 'rb') as image_file:
            content = image_file.read()

        # im.verify()
        image = types.Image(content=content)
        #context = types.ImageContext(language_hints="ro")
        # Performs label detection on the image file
        response = client.text_detection(image=image)
        if len(response.text_annotations):
            print(response.text_annotations[0].description)
        return get_fake_json(), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
