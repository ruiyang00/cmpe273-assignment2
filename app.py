from flask import Flask, escape, request
from flask import make_response



app = Flask(__name__)


@app.route('api/tests',methods=['POST'])
def create_test():
    subjname = request.json.get('subject')
    anskeys = request.json.get('answer_keys')
    subm = []

    '''
        need to store this into local SQLite DB
        write some codes here to store them 
    '''
    
    return {'test_id': ,'subject':subjname, 'answer_keys':anskeys,
            'submissions':subm}, 201

@app.route('api/tests/<testid>/scantrons', methods=['POST'])
def upload_scantron(testid):
    


    return 202



@app.route('api/tests/<testid>',methods=['GET'])
def get_test_info(id):
    #return the test info by the testid in url
