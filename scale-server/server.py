from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

db_config = {
    "host": "localhost",
    "user": "admin",
    "password": "admin",
    "database": "your_database"
}

@app.route('/save', methods=['POST'])
def save_data():
    try:
        data = request.json
        value1 = data.get('value1')
        value2 = data.get('value2')

        if value1 is None or value2 is None:
            return jsonify({"error": "Missing value1 or value2"}), 400

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = "INSERT INTO your_table (column1, column2) VALUES (%s, %s)"
        cursor.execute(query, (value1, value2))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Data saved successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
