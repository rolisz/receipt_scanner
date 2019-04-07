import datetime
import json
import re

import dateparser
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from google.cloud import vision
from google.cloud.vision import types
import io
from IPython.display import display # to display images
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict
import os
import math
client = vision.ImageAnnotatorClient()
import itertools

def get_ocr(image):
    image = types.Image(content=image)
    res = client.text_detection(image)
    return MessageToDict(res)

def get_paths_for_folder(folder):
    for f in os.listdir(folder):
        yield os.path.join(folder, f)

def read_image(path):
    with open(path, 'rb') as image_file:
        return image_file.read()

def draw_receipt_bbox(path, results):
    data = results[path]
    img = Image.open(path)
    draw = ImageDraw.Draw(img)
    vertices = data['textAnnotations'][0]['boundingPoly']['vertices']
    x1, y1 = vertices[0]["x"], vertices[0]["y"]
    x2, y2 = vertices[1]["x"], vertices[1]["y"]
    x3, y3 = vertices[2]["x"], vertices[2]["y"]
    x4, y4 = vertices[3]["x"], vertices[3]["y"]
    draw.polygon([x1 ,y2, x2 ,y2, x3 ,y3, x4, y4], outline="red")
    return img


def draw_word_bbox(path, results):
    img = Image.open(path)
    data = results[path]
    return draw_word_bbox2(img, data)


def draw_word_bbox2(img, data):
    draw = ImageDraw.Draw(img)
    words = data['textAnnotations'][1:]
    for word in words:
        vertices = word['boundingPoly']['vertices']
        x1, y1 = vertices[0].get('x', 0), vertices[0].get('y', 0)
        x2, y2 = vertices[1].get('x', 0), vertices[1].get('y', 0)
        x3, y3 = vertices[2].get('x', 0), vertices[2].get('y', 0)
        x4, y4 = vertices[3].get('x', 0), vertices[3].get('y', 0)
        draw.polygon([x1 ,y2, x2 ,y2, x3 ,y3, x4, y4], outline="red")
    return img


def crop_image(path, data):
    img = Image.open(path)
    draw = ImageDraw.Draw(img)
    vertices = data['textAnnotations'][0]['boundingPoly']['vertices']
    x1, y1 = vertices[0]["x"], vertices[0]["y"]
    x2, y2 = vertices[1]["x"], vertices[1]["y"]
    x3, y3 = vertices[2]["x"], vertices[2]["y"]
    x4, y4 = vertices[3]["x"], vertices[3]["y"]
    top = min(y1, y2, y3, y4)
    left = min(x1, x2, x3, x4)
    bottom = max(y1, y2, y3, y4)
    right = max(x1, x2, x3, x4)
    img = img.crop((left, top, right, bottom))
    return img


def search_nearest_sum(i, polys):
    coords = polys[i]
    print(coords)


# search_nearest_sum(15, polys)

def search_nearest(j, polys, excepts=[]):
    """Get poly which has the nearest corner to a corner of this poly"""
    coords = get_coords(polys[j])
    closest = None
    closest_dist = 10000000
    closest_idx = -1
    for i, p in enumerate(polys):
        d = get_distance(coords, get_coords(p))
        if d < closest_dist and i != j and i not in excepts:
            closest = p
            closest_dist = d
            closest_idx = i
    print(closest)
    return closest_idx


def get_distance(poly1, poly2):
    dist = 1000000
    for x1, y1 in poly1:
        for x2, y2 in poly2:
            d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if d < dist:
                dist = d
    return dist


def get_coords(poly):
    vertices = poly['boundingPoly']['vertices']
    x1, y1 = vertices[0].get('x', 0), vertices[0].get('y', 0)
    x2, y2 = vertices[1].get('x', 0), vertices[1].get('y', 0)
    x3, y3 = vertices[2].get('x', 0), vertices[2].get('y', 0)
    x4, y4 = vertices[3].get('x', 0), vertices[3].get('y', 0)
    return [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]


def get_center(poly):
    vertices = poly['boundingPoly']['vertices']
    x1, y1 = vertices[0].get('x', 0), vertices[0].get('y', 0)
    x2, y2 = vertices[1].get('x', 0), vertices[1].get('y', 0)
    x3, y3 = vertices[2].get('x', 0), vertices[2].get('y', 0)
    x4, y4 = vertices[3].get('x', 0), vertices[3].get('y', 0)

    return (x1 + x3) / 2, (y1 + y3) / 2


def get_line(poly1, poly2):
    xc1, yc1 = get_center(poly1)
    xc2, yc2 = get_center(poly2)

    if xc2 - xc1 == 0:
        return 0, yc1
    m = (yc2 - yc1) / (xc2 - xc1)
    b = yc1 - m * xc1
    return m, b


def get_all_lines(polys):
    lines = {}
    angle_min = math.tan(-0.15) # Roughly 15 degrees
    angle_max = math.tan(0.15)
    for i, p1 in enumerate(polys):
        for j, p2 in enumerate(polys):
            if i == j:
                continue
            line = get_line(p1, p2)
            dist = get_distance(get_coords(p1), get_coords(p2))
            if angle_min < line[0] < angle_max and dist < 100:
                lines[(i, j)] = line
    return lines


def group_lines(lines):
    groups = []
    group = []
    last_y = 0
    for i, line in enumerate(sorted(lines.values(), key=lambda x:x[1])):
        m, b = line
        if abs(b - last_y) > 15:
            groups.append(group)
            last_y = b
            group = []
        group.append((m,b))
    groups.append(group)
    return groups


def get_main_lines(groups):
    main_lines = []
    for g in groups:
        if len(g):
            avg_m = sum(x[0] for x in g)/len(g)
            avg_b = sum(x[1] for x in g)/len(g)
            main_lines.append((avg_m, avg_b))
    return main_lines


def distance_from_line(point, line):
    return abs(line[1] + line[0]*point[0] - point[1])/math.sqrt(1+line[0]**2)


def get_words(polys, main_lines):
    words = []
    remaining_polys = polys.copy()
    for line in main_lines:
        current_line = []
        new_polys = []
        for p in remaining_polys:
            if distance_from_line(get_center(p), line) < 10:
                current_line.append(p)
            else:
                new_polys.append(p)
        remaining_polys = new_polys
        # Assumption: the words are sorted by x
        if not current_line:
            continue
        line_group = [current_line[0]]
        for word in current_line[1:]:
            if get_distance(get_coords(line_group[-1]), get_coords(word)) < 80:
                line_group.append(word)
            else:
                words.append([x['description'] for x in line_group])
                line_group = [word]

        words.append([x['description'] for x in line_group])
    return words


def pipeline(path):
    img = read_image(path)
    results = get_ocr(img)
    crop = crop_image(path, results)
    imgByteArr = io.BytesIO()
    crop.save(imgByteArr, format='jpeg')
    imgByteArr = imgByteArr.getvalue()
    crop_results = get_ocr(imgByteArr)
    polys = crop_results['textAnnotations'][1:]
    lines = get_all_lines(polys)
    average_slope = sum(x[0] for x in lines.values())/len(lines)
    filtered_lines = {k: v for k, v in lines.items() if abs(v[0] - average_slope) < 0.05}
    grouped_lines = group_lines(filtered_lines)
    main_lines = get_main_lines(grouped_lines)
    words = get_words(polys, main_lines)
    return words


def get_word_items(words):
    is_header = True
    items = []
    prices = []

    header_max = 0
    for i, word in enumerate(words[:9]):
        joined = " ".join(word).lower()
        if "c.i.f" in joined or "bon" in joined or "fiscal" in joined or "str " in joined or\
            "bine ati venit" in joined:
            header_max = max(header_max, i)

    company = ""
    address = ""
    for word in words[:header_max]:
        joined = " ".join(word).lower()
        if re.search('S\.?C\.?(.+?)(S.?R.?L.?)|(S[:.,]?A[:.,]?)', joined, re.IGNORECASE):
            company = " ".join(word)
        if "str" in joined or "calea" in joined or "b-dul" in joined or "nr" in joined:
            address = " ".join(word)

    end_min = len(words)
    for i, word in enumerate(words):
        joined = " ".join(word).lower()
        if "total" in joined or "poziti" in joined or "tva" in joined or "numerar" in joined:
            end_min = min(end_min, i)

    data = datetime.date.today().strftime("%Y/%m/%d")
    time = "00:00"
    for word in words[end_min:]:
        joined = " ".join(word).lower()
        match = re.search('\d{2,4}[.\\-/]\w{3}[.\\-/]\d{2,4}', joined, re.IGNORECASE)
        if match:
            data = match.group()
        match = re.search('\d{2,4}[.\\-/]\d{2,4}[.\\-/]\d{2,4}', joined, re.IGNORECASE)
        if match:
            data = match.group()
        match = re.search('\d{2}:\d{2}(:\d{2})?', joined, re.IGNORECASE)
        if match:
            time = match.group()

    date = dateparser.parse(data + " " + time)
    if date:
        date = date.strftime("%Y/%m/%d %H:%M")
    else:
        date = ""
    for i, word in enumerate(words[header_max + 1:end_min]):
        joined = " ".join(word).lower()
        numbers = sum(c.isdigit() for c in joined)
        chars = sum(c.isalpha() for c in joined)
        spaces = sum(c.isspace() for c in joined)
        others = len(joined) - numbers - chars - spaces
        if chars > numbers and len(joined) > 2:
            if "kg" in joined and len(joined) < 4:
                continue
            items.append(joined)
            next_rows = sum(words[i + 1 + header_max + 1:i + 3 + header_max + 1], [])
            print(joined, next_rows)
            nrs = [float(x) for x in next_rows if is_float(x)]
            if nrs:
                price = max(nrs)
            else:
                price = -1
            prices.append({"name": " ".join(word), "price": price})
    return {"company": company, "address": address, "items": prices, "date": date}


def is_float(string):
    try:
        float(string)
        return True
    except Exception:
        return False