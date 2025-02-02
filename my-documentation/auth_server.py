from functools import wraps
from flask import Flask, Response, request, send_from_directory
import os
import subprocess

app = Flask(__name__)

# Configure these values
USERS = {
    'admin': 'test',
    'user': 'test'
}

def check_auth(username, password):
    return username in USERS and USERS[username] == password

def authenticate():
    return Response(
        'Please login to access the documentation.',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def index():
    return send_from_directory('site', 'index.html')

@app.route('/<path:path>')
@requires_auth
def serve_docs(path):
    return send_from_directory('site', path)

if __name__ == '__main__':
    # Build the site first
    subprocess.run(['mkdocs', 'build'], check=True)
    
    # Run the server
    app.run(host='0.0.0.0', port=8000, debug=False)