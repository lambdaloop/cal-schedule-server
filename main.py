from flask import Flask, jsonify, request
from flask.ext.cors import CORS
from flask.ext.compress import Compress

import os
import requests
import json

app = Flask(__name__)
CORS(app)
Compress(app)

def get_param_dict():
    d = request.get_json(silent=True)
    if not d:
        d = request.args
    if not d:
        d = request.form
    return d

BERKELEYTIME_URL = 'http://www.berkeleytime.com'

def get_section_ids(class_id):
    url = BERKELEYTIME_URL + '/enrollment/sections/{}/'.format(class_id)
    print(url)
    text = requests.get(url).text
    sections = json.loads(text)
    fall_sections = [x for x in sections if (x['semester'], x['year']) == ('fall', '2016')]
    if len(fall_sections) == 0:
        return {}
    fall_sections = fall_sections[0]['sections']
    section_ids = [(s['section_number'].strip('0'), s['section_id']) for s in fall_sections]
    return dict(section_ids)

def get_enrollment_data(section_id):
    url = BERKELEYTIME_URL + '/enrollment/data/{}/'.format(section_id)
    print(url)
    text = requests.get(url).text
    data = json.loads(text)
    out = dict(data['data'][-1])
    out['enrolled_max'] = data['enrolled_max']
    return out


@app.route('/class_enrollment')
def enrollment():
    d = get_param_dict()

    try:
        bid = int(json.loads(d['course_id']))
    except KeyError, ValueError:
        return jsonify({
            'status': 'failure',
            'message': 'invalid input format'
        })

    section_ids = get_section_ids(bid)

    enroll = dict()

    for k, v in section_ids.items():
        enroll[k] = get_enrollment_data(v)

    return jsonify({
        'status': 'success',
        'data': enroll
    })


@app.route('/section_ids')
def section_ids():
    d = get_param_dict()

    try:
        bid = int(json.loads(d['course_id']))
    except KeyError, ValueError:
        return jsonify({
            'status': 'failure',
            'message': 'invalid input format'
        })

    section_ids = get_section_ids(bid)

    return jsonify({
        'status': 'success',
        'data': section_ids
    })

@app.route('/section_enrollment')
def section_enrollment():
    d = get_param_dict()

    try:
        sid = int(json.loads(d['section_id']))
    except KeyError, ValueError:
        return jsonify({
            'status': 'failure',
            'message': 'invalid input format'
        })

    data = get_enrollment_data(sid)

    return jsonify({
        'status': 'success',
        'data': data
    })


@app.route('/')
def hello():
    return "Hello, the server is running!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33507))
    app.run(host='0.0.0.0', port=port, debug=True)
