from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import json
import os

app = Flask(__name__, static_folder='static')
JSON_FILE = 'bookings.json'

# 1. Σερβίρισμα της αρχικής σελίδας (index.html) από τον φάκελο static
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# 2. GET API: Επιστροφή όλων των κρατήσεων
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    if not os.path.exists(JSON_FILE):
        return jsonify([])
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    return jsonify(data)

# 3. POST API: Δημιουργία νέας κράτησης με έλεγχο ημερομηνιών
@app.route('/api/bookings', methods=['POST'])
def add_booking():
    req_data = request.get_json()
    name = req_data.get('name')
    start_date_str = req_data.get('startDate')
    end_date_str = req_data.get('endDate')

    # Έλεγχος αν λείπουν πεδία
    if not name or not start_date_str or not end_date_str:
        return jsonify({"error": "Όλα τα πεδία είναι υποχρεωτικά!"}), 400

    # Μετατροπή των strings σε αντικείμενα ημερομηνίας (date objects) για σύγκριση
    try:
        start_new = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_new = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Λανθασμένη μορφή ημερομηνίας!"}), 400

    # Ανάγνωση υπαρχουσών κρατήσεων
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            try:
                bookings = json.load(f)
            except json.JSONDecodeError:
                bookings = []
    else:
        bookings = []

    # Έλεγχος για επικάλυψη ημερομηνιών
    for b in bookings:
        start_existing = datetime.strptime(b['startDate'], '%Y-%m-%d').date()
        end_existing = datetime.strptime(b['endDate'], '%Y-%m-%d').date()
        
        # Λογική επικάλυψης: (ΝέαΈναρξη <= ΥπάρχουσαΛήξη) ΚΑΙ (ΝέαΛήξη >= ΥπάρχουσαΈναρξη)
        if start_new <= end_existing and end_new >= start_existing:
            return jsonify({"error": "Το αυτοκίνητο είναι ήδη κλεισμένο για αυτές τις ημερομηνίες!"}), 400

    # Προσθήκη της νέας κράτησης
    bookings.append({
        "name": name,
        "startDate": start_date_str,
        "endDate": end_date_str
    })

    # Αποθήκευση πίσω στο αρχείο JSON
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookings, f, indent=2, ensure_ascii=False)

    return jsonify({"message": "Η κράτηση έγινε με επιτυχία!"})

if __name__ == '__main__':
    # Τοπικό τρέξιμο στη θύρα 3000
    app.run(host='0.0.0.0', port=3000, debug=True)
