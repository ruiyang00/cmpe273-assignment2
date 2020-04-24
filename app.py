from flask import Flask, escape, request, send_from_directory
from flask import make_response
from marshmallow import Schema, fields, pprint, ValidationError
import json
import sqlite3
import os


class TeseSchema(Schema):
    subject = fields.String(required=True)
    answer_keys = fields.Dict(keys=fields.Str(), values=fields.Str())


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config["UPLOAD_FOLDER"] = "/user_upload_files"


@app.route('/api/tests', methods=['POST'])
def create_test():

    TeseSchema().load(request.json)
    subjname = request.json.get('subject')
    anskeys_json = request.json.get('answer_keys')
    anskeys = ",".join(list(anskeys_json.values()))

    conn = sqlite3.connect('cmpe273.db')
    c = conn.cursor()

    c.execute("INSERT INTO tests (subject, anskeys) VALUES (?,?)",
              (subjname, anskeys))

    t = (subjname,)
    c.execute("SELECT id FROM tests WHERE subject=?", t)
    conn.commit()
    tid = c.fetchone()[0]
    conn.close()

    return {'test_id': tid, "subject": subjname, "answer_keys": anskeys_json,
            'submissions': []}, 201


@app.route('/api/tests/<testid>/scantrons', methods=['POST'])
def upload_scantron(testid):

    file = request.files['file']

    file_content = file.read()
    data = json.loads(file_content)

    si = data['answers']
    input_str = ",".join(list(si.values()))
    sject = data['subject']
    stu_name = data['name']

    s_url = "http://localhost:5000/user_upload_files/"+file.filename

    file.save(os.getcwd()+app.config["UPLOAD_FOLDER"]+"/" + file.filename)
    with open('./user_upload_files/' + file.filename, "w") as writefile:
        writefile.write(json.dumps(data))

    res_score = getscore(si, testid)
    conn = sqlite3.connect('cmpe273.db')
    c = conn.cursor()
    c.execute("SELECT anskeys FROM tests WHERE id=?", testid)
    conn.commit()
    testkeys = c.fetchone()
    keys_inlist = testkeys[0].split(",")
    res = getres(si, keys_inlist)

    conn = sqlite3.connect('cmpe273.db')
    c = conn.cursor()

    c.execute("INSERT INTO submissions (scantron_url, subject,student_name, score, ques_answers,test_id) VALUES (?,?,?,?,?,?)",
              (s_url, sject, stu_name, res_score, input_str, testid))

    t = (stu_name,)
    c.execute("SELECT scantron_id FROM submissions WHERE student_name=?", t)
    conn.commit()
    s_id = c.fetchone()[0]

    return {"scantron_id": s_id, "scantron_url": s_url, "name": stu_name, "subject": sject, "score": res_score, "result": res}, 201


@app.route('/user_upload_files/<file_name>', methods=['GET'])
def download_scantron(file_name):
    return send_from_directory(os.getcwd()+"/user_upload_files", file_name, as_attachment=True)


@app.route('/api/tests/<testid>', methods=['GET'])
def get_test_info(testid):
    conn = sqlite3.connect('cmpe273.db')
    c = conn.cursor()

    t = (testid,)
    c.execute("SELECT * FROM tests WHERE id=?", t)

    test = c.fetchone()
    test_id = test[0]
    test_name = test[1]
    keys_str = test[2]  # "A,B,C,D,E"
    test_ans_keys_json = dict(enumerate(keys_str.split(",")))

    # res = getres(keys_str, test_id)

    cursor = c.execute(
        "SELECT scantron_id, scantron_url, student_name,subject,score,ques_answers   FROM submissions WHERE test_id=?", t)
    names = list(map(lambda x: x[0], cursor.description))
    # row = c.fetchone()
    # col = row.keys()
    rows = c.fetchall()
    submissions = []

    print(names)
    print(rows)

    for x in range(len(rows)):
        temp = {}
        for y in range(len(rows[0])):

            if y == 5:
                print("I am here")
                temp["result"] = getres(
                    dict(enumerate((rows[x][y].split(",")))), keys_str.split(","))
            else:
                temp[names[y]] = rows[x][y]

        submissions.append(temp)

    pprint(submissions)

    # submissions =
    # print(test)
    # # print(submis)
    # print(len(row))

    conn.commit()
    conn.close()

    return {"test_id": test_id, "subject": test_name, "answer_keys": test_ans_keys_json, "submissions": submissions}, 200


@app.before_first_request
def ini_db_table():
    conn = sqlite3.connect('cmpe273.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS tests (
                        id integer PRIMARY KEY,
                        subject text,
                        anskeys text)''')

    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
                        scantron_id integer PRIMARY KEY NOT NULL,
                        scantron_url text NOT NULL,
                        student_name text NOT NULL,
                        subject text NOT NULL,
                        score integer,
                        ques_answers text,
                        test_id interger NOT NULL,
                        FOREIGN KEY (test_id) REFERENCES tests (id))''')

    conn.commit()
    print("database table initia scussfully")
    conn.close()


def getres(si, keys_inlist):
    student_ans_list = list(si.values())  
    quenumber = 1
    res = {}
    for expected, actual in zip(keys_inlist, student_ans_list):
        res[str(quenumber)] = {
            "actual": actual,
            "expected": expected
        }
        quenumber += 1

    return res


def getscore(si, testid):

    student_ans_list = list(si.values())
    conn = sqlite3.connect('cmpe273.db')
    c = conn.cursor()
    c.execute("SELECT anskeys FROM tests WHERE id=?", testid)
    conn.commit()
    testkeys = c.fetchone()
    keys_inlist = testkeys[0].split(",")

    print("length of si", len(si))
    print("si", si)
    print("student_ans_list", student_ans_list)
    print("keys_inlist", keys_inlist)

    conn.close()

    totalpoints = 0
    print("length of keys_inlist: ", len(keys_inlist))
    print("length of keys_inlist: ", len(student_ans_list))

    for expected, actual in zip(keys_inlist, student_ans_list):
        if expected == actual:
            totalpoints += 1

    return totalpoints
