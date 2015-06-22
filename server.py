from flask import Flask, send_from_directory
app = Flask(__name__)
app.debug = False

@app.route('/')
def hello_world():
    #assert(False)
    return 'YOLO'

if __name__ == '__main__':
    app.run(host='localhost', port=80)
