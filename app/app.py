
from flask import Flask,render_template,send_from_directory,redirect
 
app = Flask(__name__,static_url_path='/static' )

@app.route('/')
def index():
     return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')
 
app.run(host = '0.0.0.0',port=80,debug=True)
