from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error, IntegrityError
from dotenv import load_dotenv
import os

load_dotenv()
mysql_password = os.getenv('mysqlpassword')

app = Flask(__name__)


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': mysql_password,
    'database': 'code_database'
}

def save_to_database(latitude, longitude, unique_code):
    """Save location data to the MySQL database."""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        insert_query = """
        INSERT INTO locations (latitude, longitude, unique_code)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (latitude, longitude, unique_code))
        connection.commit()
        return None 
    except IntegrityError as err:  
        print(f"Duplicate entry for unique_code: {unique_code}")
        return "Duplicate entry for unique_code"
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return f"Error: {err}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/')
def home():
    """Render the homepage."""
    return render_template('map_code.html')
@app.route('/generate')
def generate():
    return render_template('advanc.html')


@app.route('/get-destination', methods=['POST'])
def get_destination():
    """Retrieve destination coordinates from the database using a unique code."""
    data = request.json
    unique_code = data.get('unique_code')

    if not unique_code:
        return jsonify({'error': 'Destination code is required'}), 400

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query = "SELECT latitude, longitude FROM locations WHERE unique_code = %s"
        cursor.execute(query, (unique_code,))
        result = cursor.fetchone()

        if result:
            return jsonify({'latitude': result['latitude'], 'longitude': result['longitude']}), 200
        else:
            return jsonify({'error': 'Destination code not found'}), 404
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': f"Database error: {e}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/save-code', methods=['POST'])
def save_code():
    """Endpoint to save location details sent from the frontend."""
    data = request.json
    print("Received data:", data)  

 
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    unique_code = data.get('unique_code')

    if not latitude or not longitude or not unique_code:
        print("Invalid data received")  
        return jsonify({'error': 'Invalid data'}), 400

   
    result = save_to_database(latitude, longitude, unique_code)

    if result == "Duplicate entry for unique_code":
        return jsonify({'error': 'Location code already exists'}), 400
    elif result:
        return jsonify({'error': result}), 500

    return jsonify({'message': 'Location saved successfully'}), 200

if __name__ == '__main__':
   
    app.run(host="0.0.0.0", debug=False)
