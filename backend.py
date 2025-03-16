from flask import Flask, request, redirect, jsonify, render_template, send_from_directory
import json
import os
import re

app = Flask(__name__, static_folder='.')

# File to store phone numbers
NUMBERS_FILE = "phone_numbers.json"

def load_numbers():
    """Load existing phone numbers from JSON file"""
    if os.path.exists(NUMBERS_FILE):
        try:
            with open(NUMBERS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"numbers": []}
    return {"numbers": []}

def save_number(phone_number):
    """Save a new phone number to the JSON file"""
    data = load_numbers()
    
    # Check if number already exists to avoid duplicates
    if phone_number not in data["numbers"]:
        data["numbers"].append(phone_number)
        
        with open(NUMBERS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    return False

def validate_phone(phone):
    """Basic phone number validation"""
    # Remove any non-digit characters for validation
    digits_only = re.sub(r'\D', '', phone)
    # Check if it's a reasonable length for a phone number (adjust as needed)
    return len(digits_only) >= 7 and len(digits_only) <= 15

@app.route('/')
def index():
    """Serve the index.html file"""
    return send_from_directory('.', 'index.html')

@app.route('/login.html')
def login():
    """Serve the login.html file"""
    return send_from_directory('.', 'login.html')

@app.route('/thank_you.html')
def thank_you():
    """Serve the thank you page"""
    # If thank_you.html doesn't exist yet, we'll create a simple response
    if not os.path.exists('thank_you.html'):
        return "<h1>Thank You!</h1><p>Your phone number has been registered. We'll contact you soon.</p>"
    return send_from_directory('.', 'thank_you.html')

@app.route('/submit_phone', methods=['POST'])
def submit_phone():
    phone = request.form.get('number', '')
    
    if not phone:
        return jsonify({"success": False, "message": "No phone number provided"}), 400
    
    if not validate_phone(phone):
        return jsonify({"success": False, "message": "Invalid phone number format"}), 400
    
    if save_number(phone):
        return redirect('/thank_you.html')  # Redirect to a thank you page
    else:
        return jsonify({"success": False, "message": "Phone number already registered"}), 409

@app.route('/view_numbers', methods=['GET'])
def view_numbers():
    # Optional admin endpoint to view all numbers
    # In a real app, this should be password protected
    data = load_numbers()
    return jsonify(data)

# Serve static files (CSS, JS, etc.)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)
