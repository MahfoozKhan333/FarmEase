from flask import Flask, jsonify, render_template, request, redirect, url_for
import bcrypt
import connectDB

app = Flask(__name__)

# Mock token for demonstration
VALID_TOKEN = "Bearer YOUR_TOKEN"

@app.route('/')
def index():
    client = connectDB.connect_to_mongodb() 
    db = client['cattle_farm']  # Access the 'cattle_farm' database

    databases = client.list_database_names()
    if 'cattle_farm' in databases:
        print("Database 'cattle_farm' exists.")
    else:
        print("Database 'cattle_farm' does not exist.")

    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    auth_header = request.headers.get('Authorization')
    if auth_header != VALID_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            farm_name = data['farm_name']
            username = data['username']
            password = data['password']
            email = data['email']
            first_name = data['first_name']
            last_name = data['last_name']
            mobile_number = data['mobile_number']
        except (TypeError, KeyError):
            return jsonify({"error": "Invalid JSON payload"}), 400
    
        # farm_name = request.form['farm_name']
        # username = request.form['username']
        # password = request.form['password']
        # email = request.form['email']
        # first_name = request.form['first_name']
        # last_name = request.form['last_name']
        # mobile_number = request.form['mobile_number']

        # Hash the password for security
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Get the database object
        client = connectDB.connect_to_mongodb() 
        db = client['cattle_farm'] 

        if db.users.find_one({'username': username}) or db.users.find_one({'email': email}):
            return jsonify({"error": "Username or email already exists"}), 409

        try:
            # Insert user data into the collection
            db.users.insert_one({
                'farm_name': farm_name,
                'username': username,
                'password': hashed_password,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'mobile_number': mobile_number
            })
            # return jsonify({"message": "Registration successful"}), 201
            return redirect(url_for('login'))  # Redirect to login after successful registration
        except Exception as e:
            print(f"Error inserting user: {e}")
        return jsonify({"error": "An error occurred during registration"}), 500
        
        # Insert user data into the collection
        # db.users.insert_one({
        #     'farm_name': farm_name,
        #     'username': username,
        #     'password': hashed_password,
        #     'email': email,
        #     'first_name': first_name,
        #     'last_name': last_name,
        #     'mobile_number': mobile_number
        # })
        # print("I am in register")
        # return redirect(url_for('login'))

    return render_template('register/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Get the database object
        client = connectDB.connect_to_mongodb() 
        db = client['cattle_farm'] 

        # Find the user in the database
        user = db.users.find_one({'username': username})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Successful login, redirect to dashboard
            return redirect(url_for('dashboard')) 
        else:
            return "Invalid username or password"

    return render_template('login/login.html')

@app.route('/dashboard')
def dashboard():
    # Dashboard content here
    return "Welcome to the dashboard!"

if __name__ == "__main__":
    app.run(debug=True)