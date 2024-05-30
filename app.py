from flask import Flask, jsonify
import requests
import threading
import time
from collections import deque

app = Flask(__name__)

# Configuration
WINDOW_SIZE = 10
TIMEOUT = 0.5  # 500 milliseconds

# Store numbers in a deque with a maximum size
numbers_store = deque(maxlen=WINDOW_SIZE)

# Function to fetch number from third-party API
def fetch_number(number_type):
    try:
        # Simulating a third-party API endpoint, replace with actual API endpoint
        url = f"http://third-party-api.com/numbers/{number_type}"
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            number = response.json().get("number")
            return number
    except (requests.RequestException, ValueError):
        return None

# Function to handle fetching and storing the number
def handle_request(number_type):
    new_number = fetch_number(number_type)
    if new_number is not None and new_number not in numbers_store:
        numbers_store.append(new_number)

# Endpoint to handle number requests
@app.route('/numbers/<string:numberid>', methods=['GET'])
def get_numbers(numberid):
    if numberid not in ['p', 'f', 'e', 'r']:
        return jsonify({"error": "Invalid number ID"}), 400
    
    # Copy the current state of the store before the new fetch
    before_numbers = list(numbers_store)

    # Start a thread to fetch and store the new number
    thread = threading.Thread(target=handle_request, args=(numberid,))
    thread.start()
    thread.join(timeout=TIMEOUT)

    # Copy the updated state of the store
    after_numbers = list(numbers_store)
    
    # Calculate the average
    if after_numbers:
        average = sum(after_numbers) / len(after_numbers)
    else:
        average = 0

    response = {
        "before": before_numbers,
        "after": after_numbers,
        "average": average
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
