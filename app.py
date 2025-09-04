from flask import Flask, render_template, request, jsonify
import json, random, os

app = Flask(__name__)

# ---------- Station-wise slot inventory ----------
# Define the number of lockers (slots) available at each station.
# You can change counts as needed.
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


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/')
def home():
    return render_template('index.html')


# ---------- API to get available slots for a station ----------
@app.route('/get_slots', methods=['POST'])
def get_slots():
    req = request.get_json(silent=True) or {}
    station = req.get('station')

    # Booked slots lookup
    bookings = load_bookings()
    booked = set(b.get('slot') for b in bookings if b.get('station') == station)

    # If station not in inventory, default to 10 slots
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

    # Validate days and slot
    try:
        days = int(days_raw)
    except (TypeError, ValueError):
        days = 1

    try:
        slot = int(slot_raw)
    except (TypeError, ValueError):
        # Fallback: pick first available slot if not passed
        bookings = load_bookings()
        booked = set(b.get('slot') for b in bookings if b.get('station') == station)
        station_slots = slots_data.get(station, list(range(1, 11)))
        available = [s for s in station_slots if s not in booked]
        if not available:
            # No slots available, send simple error page
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
        "name": name,
        "mobile": mobile,
        "city": city,
        "station_type": station_type,
        "station": station,
        "day": day,
        "date": date,
        "days": days,
        "price": price,
        "pin": pin,
        "slot": slot
    }

    save_booking(booking)
    return render_template('confirm.html', booking=booking)


@app.route('/admin')
def admin():
    bookings = load_bookings()
    # Show latest first
    bookings = list(reversed(bookings))
    return render_template('admin.html', bookings=bookings)


if __name__ == '__main__':
    app.run(debug=True)
