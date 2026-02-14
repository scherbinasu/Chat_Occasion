from crypto import *
import ssl
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
import db.db as db
def crypto_html(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return render_template('crypto_base.html', data=encrypt_with_symmetric_key(symmetric_key, result))
    return wrapper

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

symmetric_key = generate_symmetric_key()

@app.route('/crypto', methods=['POST'])
def crypto():
    publicKey = request.json.get('publicKey')
    data = encrypt_with_public_key(publicKey, symmetric_key)
    return jsonify({'data': data})

@app.route('/', methods=['GET'])
@crypto_html
def index():
    return render_template('index.html')

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(r"C:\Users\user\Desktop\localhost+2.pem",
                            r"C:\Users\user\Desktop\localhost+2-key.pem")
    app.run(host='0.0.0.0', debug=True, port=443, ssl_context=context)
