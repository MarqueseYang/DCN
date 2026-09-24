# Author: Qikai Yang - DCN (CSCI-GA.2662-001) Lab 2
# Sample Flask app that returns the current time on the /time path.
from datetime import datetime, timezone

from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello world!'


@app.route('/time')
def current_time():
    now = datetime.now(timezone.utc).astimezone()
    return now.strftime('%Y-%m-%d %H:%M:%S %Z') + '\n'


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=8080,
            debug=True)
