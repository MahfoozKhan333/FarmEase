from flask import Flask, jsonify, render_template, request, redirect, url_for
import bcrypt
import connectDB
from pymongo import MongoClient
import matplotlib.pyplot as plt
import io
import base64


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

@app.route('/register', methods=['GET','POST'])
def register():
    auth_header = request.headers.get('Authorization')
    # if auth_header != VALID_TOKEN:
    #     return jsonify({"error": "Unauthorized"}), 401
    
    if request.method == 'POST':
    
        farm_name = request.form.get('farm_name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        mobile_number = request.form.get('mobile_number')

        if(password != confirm_password):
            return jsonify({"error": "Password and confirm Passowrd does not match"}), 409


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

    return render_template('register/register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

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
    return render_template('dashboard/dashboard.html')

# @app.route('/dashboard/addAnimal')
# def addAnimal():
#     # Dashboard content here
#     return render_template('addAnimal/addAnimal.html')


@app.route('/dashboard/addAnimal', methods=['GET', 'POST'])
def addAnimal():
    if request.method == 'POST':
        try:
            # Retrieve data from the form
            animal_id = request.form.get('animalid')
            date_of_birth = request.form.get('dateOfBirth')
            breed = request.form.get('breed')
            weight = request.form.get('weight')
            food = request.form.get('food')
            milk_production = request.form.get('milkProduction')
            growth = request.form.get('growth')  # Retrieve the growth value

            # Validate required fields
            required_fields = [animal_id, date_of_birth, breed, weight, food, milk_production, growth]
            if not all(required_fields):
                return jsonify({"error": "All fields are required."}), 400

            # Connect to the database
            client = connectDB.connect_to_mongodb()
            db = client['cattle_farm']

            # Check if the animal_id already exists
            if db.animals.find_one({'animal_id': animal_id}):
                return jsonify({"error": "Animal with this ID already exists."}), 409

            # Insert animal details into the 'animals' collection
            db.animals.insert_one({
                'animal_id': animal_id,
                'date_of_birth': date_of_birth,
                'breed': breed,
                'weight': float(weight),  # Convert weight to float
                'food': food,
                'milk_production': float(milk_production),  # Convert milk production to float
                'growth': growth
            })
            print(f"Animal added successfully: {animal_id}")

            return redirect(url_for('dashboard'))  # Redirect to the dashboard after successful addition

        except Exception as e:
            print(f"Error adding animal: {e}")
            return jsonify({"error": "An error occurred while adding the animal."}), 500

    return render_template('addAnimal/addAnimal.html')


def create_chart_image(chart_type, data, labels=None, xlabel=None, ylabel=None):
    """Creates a chart image using Matplotlib and returns it as a base64 encoded string."""
    plt.figure()  # Create a new figure for each chart

    if chart_type == 'box':
        plt.boxplot(data.values())  # Assuming data is a dictionary like {'Category1': [values], ...}
        plt.xticks(range(1, len(data) + 1), data.keys())  # Set x-axis labels
    elif chart_type == 'scatter':
        x, y = zip(*data)  # Unpacking tuples into two separate lists
        plt.scatter(x, y)
    elif chart_type == 'bar':
        plt.bar(labels, data) # Assuming data is a list of values
        plt.xticks(rotation=45, ha='right') # Rotate x-axis labels for better readability if needed

    plt.xlabel(xlabel or "X-axis")
    plt.ylabel(ylabel or "Y-axis")
    plt.title(f"{xlabel} vs. {ylabel}") # Set title based on labels

    img = io.BytesIO()
    plt.savefig(img, format='png')  # Save chart to in-memory buffer
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()  # Encode to base64
    plt.close() # Close the figure to free memory
    return plot_url

@app.route('/dashboard/analysis')
def analysis():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["cattle_farm"]
    animals = list(db.animals.find())
    print("Animals: ", animals)

    valid_animals = [
        a for a in animals if a.get('_id') and a.get('weight') and a.get('milk_production')
    ]

    weight_growth_data = {}
    weight_milk_data = []
    food_milk_data = {}

    for animal in valid_animals:
        # 1. Weight vs. Growth
        growth = animal.get("growth", "Unknown")
        if growth not in weight_growth_data:
            weight_growth_data[growth] = []
        weight_growth_data[growth].append(animal["weight"])

        # 2. Weight vs. Milk Production (Scatter Plot)
        weight_milk_data.append((animal["weight"], animal["milk_production"]))

        # 3. Food Type vs. Milk Production
        food_str = animal.get("food", "")
        if food_str:
            foods = food_str.split(", ")  # Split multiple food types
            for food in foods:
                if food not in food_milk_data:
                    food_milk_data[food] = []
                food_milk_data[food].append(animal["milk_production"])

    # Create charts as images
    weight_growth_chart = create_chart_image('box', weight_growth_data, xlabel='Growth', ylabel='Weight')
    weight_milk_chart = create_chart_image('scatter', weight_milk_data, xlabel='Weight', ylabel='Milk Production')
    food_milk_chart = create_chart_image('box', food_milk_data, xlabel='Food', ylabel='Milk Production')

    client.close()

    return render_template('analysis/analysis.html', 
                           weight_growth_chart=weight_growth_chart,
                           weight_milk_chart=weight_milk_chart,
                           food_milk_chart=food_milk_chart)


# @app.route('/analysis')
# def view_analysis():
#     return render_template('analysis.html')

# def create_chart_image(chart_type, data, labels=None, xlabel=None, ylabel=None):
#     """Creates a chart image using Matplotlib and returns it as a base64 encoded string."""
#     plt.figure()  # Create a new figure for each chart

#     if chart_type == 'box':
#         plt.boxplot(data.values())  # Assuming data is a dictionary like {'Category1': [values], ...}
#         plt.xticks(range(1, len(data) + 1), data.keys())  # Set x-axis labels
#     elif chart_type == 'scatter':
#         x = [point['x'] for point in data]
#         y = [point['y'] for point in data]
#         plt.scatter(x, y)
#     elif chart_type == 'bar':
#         plt.bar(labels, data) # Assuming data is a list of values
#         plt.xticks(rotation=45, ha='right') # Rotate x-axis labels for better readability if needed

#     plt.xlabel(xlabel or "X-axis")
#     plt.ylabel(ylabel or "Y-axis")
#     plt.title(f"{xlabel} vs. {ylabel}") # Set title based on labels

#     img = io.BytesIO()
#     plt.savefig(img, format='png')  # Save chart to in-memory buffer
#     img.seek(0)
#     plot_url = base64.b64encode(img.getvalue()).decode()  # Encode to base64
#     plt.close() # Close the figure to free memory
#     return plot_url

# @app.route('/dashboard/analysis')
# def analysis():
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["cattle_farm"]
#     animals = list(db.animals.find())
#     print("Animals: ", animals)

#     valid_animals = [
#             a for a in animals if a.get('_id') and a.get('weight') and a.get('milk_production')
#         ]

#     weight_growth_data = {}
#     weight_milk_data = []
#     food_milk_data = {}

#     for animal in valid_animals:
#             # 1. Weight vs. Growth
#             growth = animal.get("growth", "Unknown")
#             if growth not in weight_growth_data:
#                 weight_growth_data[growth] = []
#             weight_growth_data[growth].append(animal["weight"])

#             # 2. Weight vs. Milk Production (Scatter Plot)
#             weight_milk_data.append((animal["weight"], animal["milk_production"]))

#             # 3. Food Type vs. Milk Production
#             food_str = animal.get("food", "")
#             if food_str:
#                 foods = food_str.split(", ")  # Split multiple food types
#                 for food in foods:
#                     if food not in food_milk_data:
#                         food_milk_data[food] = []
#                     food_milk_data[food].append(animal["milk_production"])

#     # Create charts as images
#     weight_growth_chart = create_chart_image('box', weight_growth_data, xlabel='Growth', ylabel='Weight')
#     weight_milk_chart = create_chart_image('scatter', weight_milk_data, xlabel='Weight', ylabel='Milk Production')
#     food_milk_chart = create_chart_image('box', food_milk_data, xlabel='Food', ylabel='Milk Production')

#     client.close()

#     return render_template('analysis/analysis.html', 
#                            weight_growth_chart=weight_growth_chart,
#                            weight_milk_chart=weight_milk_chart,
#                            food_milk_chart=food_milk_chart)

if __name__ == "__main__":
    app.run(debug=True)