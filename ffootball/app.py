from flask import Flask, jsonify
import traceback
import os
import shutil
from ffootball.make_dashboard import main

app = Flask(__name__)
if os.path.exists('secrets/token.json'):
    shutil.copy('secrets/token.json', 'token.json')

@app.route('/', methods=['GET'])
def create_sheets():
    try:
        main()
        return jsonify({"status": "healthy"})
    except Exception as e:
        msg = traceback.format_exc()
        return jsonify({
            "status": "failed",
            "msg": msg,
            }, 500)


@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
