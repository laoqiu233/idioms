from flask import Flask, request, make_response, render_template
import json, mysql.connector, pypinyin, os, time

def dbConnect():
    return mysql.connector.connect(host='localhost', port='3306', user='root', password='yourpwhere', db='idioms')

app = Flask(__name__)

getTail = lambda idiom: pypinyin.pinyin(idiom, style=pypinyin.Style.TONE3)[-1][0][0:-1]

def jsonResponse(data, status):
    resp = make_response(json.dumps(data, ensure_ascii=False))
    resp.mimetype = 'application/json'
    resp.status_code = status
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

def is_all_chinese(strs):
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True

# Front-end
@app.route('/')
def index():
    return render_template('index.html')

# API
@app.route('/get')
def getPaths():
    conn = dbConnect()
    c = conn.cursor()
    # Retrieve the data
    idiom = request.args.get('idiom')
    depth = request.args.get('depth')
    # Verify data
    try:
        # Check if the data is correct
        assert len(idiom) == 4
        assert is_all_chinese(idiom)
        assert 1 <= int(depth) <= 5
    except:
        # Bad request
        data = {
            'desc': 'Bad reqeust, request arguments are in an incorrect format.'
        }
        return jsonResponse(data, 400)
    # Get data from db
    c.execute('SELECT `Path` FROM `connections` WHERE `Head`="{}" AND `Depth`={} LIMIT 100'.format(idiom, depth))
    data = c.fetchall()
    not_exact = False
    if not data:
        c.execute('SELECT `Path` FROM `connections` WHERE `Initial`="{}" AND `Depth`={} LIMIT 100'.format(getTail(idiom), int(depth) - 1))
        data = c.fetchall()
        not_exact = True
    conn.close()
    # Make response in json format
    result = {
        'data': [('{}->'.format(idiom) if not_exact else '') + i[0] for i in data],
    }
    return jsonResponse(result, 200)

if __name__ == '__main__':
    app.run()