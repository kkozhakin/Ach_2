import os

import flask
from flask import Flask, render_template, request

template_dir = os.path.abspath('static')
app = Flask(__name__, template_folder=template_dir)

port = os.environ.get('PORT_FRONT')
url_back = os.environ.get('URL_BACK')
port_back = os.environ.get('PORT_BACK')


@app.route('/', methods=['GET'])
def main():
    error_code = request.args.get('err')
    number = request.args.get('number')

    if error_code == '' or number == '' or error_code is None or number is None:
        return render_template('index.html',
                               url_back=url_back + ':' + port_back,
                               error='',
                               success='')
    error_code = int(error_code)
    number = int(number)
    success_str = ''

    error_strs = {
        0: '',
        1: 'Your number: ' + str(number) + '. This number exists',
        2: 'Your number: ' + str(number) + '. This number lower',
        3: 'Error with DB'
    }

    if error_code == 0:
        success_str = 'Success! Answer: ' + str(number + 1)

    return render_template('index.html',
                           url_back=url_back + ':' + port_back,
                           error=error_strs[int(error_code)],
                           success=success_str)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
