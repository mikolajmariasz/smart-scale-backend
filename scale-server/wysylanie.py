from flask import Flask, jsonify
import requests

app = Flask(__name__)

def send_barcode_to_first_server(barcode):
    try:
        response = requests.post("http://127.0.0.1:5000/get_food_data", json={"barcode": barcode})
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch data: {response.status_code}, {response.text}"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/send_barcode', methods=['GET'])
def send_barcode():
    barcode = "5900334006257"  # Kod kreskowy do wysłania

    data = send_barcode_to_first_server(barcode)

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5002)  # Trzeci serwer działa na porcie 5002
