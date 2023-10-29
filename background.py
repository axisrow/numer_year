from flask import Flask, Response
import os

app = Flask('')

@app.route('/')
def home():
    if os.path.exists('app.log'):
        with open('app.log', 'r') as f:
            return Response(f.read(), mimetype='text/plain')
    else:
        return "Log file not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)