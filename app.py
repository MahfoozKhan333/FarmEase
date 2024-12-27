
from flask import Flask, render_template, request, redirect, url_for

import connectDB

app = Flask(__name__)

@app.route('/')
def index():
    
    client = connectDB.connect_to_mongodb()

    databases = client.list_database_names()
    if 'cattle_farm' in databases:
        print("Database 'cattle_farm' exists.")
    else:
        print("Database 'cattle_farm' does not exist.")
        
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template('login/login.html')

    

if __name__ == "__main__":
    app.run(debug=True)
