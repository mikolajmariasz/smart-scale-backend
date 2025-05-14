import requests

def send_barcode_to_backend(barcode):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/assign_barcode/",
            json={"barcode": barcode}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch data: {response.status_code}, {response.text}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    barcode = "5900334006257"  # Przykładowy kod kreskowy
    result = send_barcode_to_backend(barcode)
    print(result)
