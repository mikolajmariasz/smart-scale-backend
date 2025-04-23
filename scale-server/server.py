from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

def login_to_django():
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/login/",
            json={"username": "username1", "password": "password1"}
        )
        if response.status_code == 200:
            print("Login successful")
            return response.cookies
        else:
            print(f"Login failed: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def send_to_django_backend(data, cookies):
    try:
        print(f"Sending data to Django backend: {data}")
        response = requests.post(
            "http://127.0.0.1:8000/api/assign_barcode/",
            json=data,
            cookies=cookies
        )
        if response.status_code == 200:
            print("Data sent successfully to Django backend")
        else:
            print(f"Failed to send data: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error sending data to Django backend: {e}")

@app.route('/get_food_data', methods=['POST'])
def get_food_data():
    try:
        data = request.json
        barcode = data.get('barcode')

        if not barcode:
            return jsonify({"error": "Missing barcode"}), 400

        FOOD_PRODUCT_API_URL = "https://world.openfoodfacts.org/api/v0/product"
        response = requests.get(f"{FOOD_PRODUCT_API_URL}/{barcode}.json")

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data from Open Food Facts"}), response.status_code

        food_data = response.json()

        if food_data.get('status') == 0:
            return jsonify({"error": "Product not found"}), 404

        product = food_data.get('product', {})
        nutriments = product.get('nutriments', {})

        macros = {
            "barcode": barcode,
            "macros": {
                "product_name": product.get('product_name', 'Unknown'),
                "energy_kcal": nutriments.get('energy-kcal', 'Unknown'),
                "proteins": nutriments.get('proteins', 'Unknown'),
                "fat": nutriments.get('fat', 'Unknown'),
                "carbohydrates": nutriments.get('carbohydrates', 'Unknown'),
                "sugars": nutriments.get('sugars', 'Unknown'),
                "salt": nutriments.get('salt', 'Unknown')
            }
        }

        cookies = login_to_django()
        if not cookies:
            return jsonify({"error": "Failed to log in to Django backend"}), 401

        send_to_django_backend(macros, cookies)

        return jsonify(macros), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
