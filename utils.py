from flask import jsonify
from datetime import datetime, time
import random


def get_error(message):
    return {
        'error_message': message
    }


def get_fake_json():
    return {
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


def get_random_filename():
    now = datetime.now()

    return str(now.year) + '_' + str(now.month) + '_' + str(now.day) + '_' + str(random.randint(1, 1e10))
