from flask import Flask, render_template, request, jsonify
import json, random, os, re
from datetime import datetime

app = Flask(__name__)

slots_data = {
    "New Delhi": list(range(1, 21)),
    "Hazrat Nizamuddin": list(range(1, 16)),
    "Anand Vihar": list(range(1, 12)),
    "ISBT Kashmere Gate": list(range(1, 10)),
    "ISBT Sarai Kale Khan": list(range(1, 10)),
    "Meerut City": list(range(1, 12)),
    "Meerut Cantt": list(range(1, 10)),
    "ISBT Meerut": list(range(1, 10)),
    "Bhainsali Bus Stand": list(range(1, 8)),
    "Charbagh": list(range(1, 16)),
    "Lucknow Junction": list(range(1, 14)),
    "Alambagh": list(range(1, 10)),
    "Kaiserbagh": list(range(1, 10)),
}

LOCKERS_FILE = 'lockers.json'

def load_bookings():
    if not os.path.exists(LOCKERS_FILE):
        return []
    with open(LOCKERS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_booking(booking):
    data = load_bookings()
    data.append(booking)
    with open(LOCKERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/get_slots', methods=['POST'])
def get_slots():
    req = request.get_json(silent=True) or {}
    station = req.get('station')
    bookings = load_bookings()
    booked = set(b.get('slot') for b in bookings if b.get('station') == station)
    station_slots = slots_data.get(station, list(range(1, 11)))
    available = [s for s in station_slots if s not in booked]
    return jsonify({"available_slots": available})

@app.route('/book', methods=['POST'])
def book():
    name = request.form.get('name')
    mobile = request.form.get('mobile')
    city = request.form.get('city')
    station_type = request.form.get('stationType')
    station = request.form.get('station')
    day = request.form.get('day')
    date = request.form.get('date')
    days_raw = request.form.get('days')
    slot_raw = request.form.get('slot')

    if not re.fullmatch(r"\d{10}", mobile or ""):
        return "Invalid mobile number", 400
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format", 400

    try:
        days = int(days_raw)
    except:
        days = 1

    try:
        slot = int(slot_raw)
    except:
        bookings = load_bookings()
        booked = set(b.get('slot') for b in bookings if b.get('station') == station)
        station_slots = slots_data.get(station, list(range(1, 11)))
        available = [s for s in station_slots if s not in booked]
        if not available:
            return render_template('confirm.html', booking={
                "name": name, "mobile": mobile, "city": city,
                "station_type": station_type, "station": station,
                "day": day, "date": date, "days": days,
                "price": 50 * days, "pin": "N/A", "slot": "No slots available"
            })
        slot = available[0]

    price = 50 * days
    pin = random.randint(1000, 9999)

    booking = {
        "name": name, "mobile": mobile, "city": city,
        "station_type": station_type, "station": station,
        "day": day, "date": date, "days": days,
        "price": price, "pin": pin, "slot": slot
    }

    save_booking(booking)
    return render_template('confirm.html', booking=booking)

@app.route('/admin')
def admin():
    bookings = list(reversed(load_bookings()))
    return render_template('admin.html', bookings=bookings)

if __name__ == '__main__':
    app.run(debug=True)
