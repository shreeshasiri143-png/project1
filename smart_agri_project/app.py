from flask import Flask, render_template, request, redirect, session
import sqlite3
import joblib
import numpy as np
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ✅ FIX: Get correct folder path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🔥 LOAD ML MODEL + ENCODERS (FIXED PATH)
model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))
soil_enc = joblib.load(os.path.join(BASE_DIR, "soil_encoder.pkl"))
crop_enc = joblib.load(os.path.join(BASE_DIR, "crop_encoder.pkl"))
fert_enc = joblib.load(os.path.join(BASE_DIR, "fert_encoder.pkl"))

# 🛢 DATABASE INIT
def init_db():
    conn = sqlite3.connect(os.path.join(BASE_DIR, "database.db"))
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS soil_data(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temperature REAL,
        humidity REAL,
        moisture REAL,
        soil_type TEXT,
        crop_type TEXT,
        nitrogen INTEGER,
        potassium INTEGER,
        phosphorous INTEGER,
        fertilizer TEXT
    )
    ''')

    conn.commit()
    conn.close()

# 🤖 SAFE ML FUNCTION
def predict_fertilizer(temp, hum, moist, soil, crop, n, k, p):
    try:
        soil = soil.strip()
        crop = crop.strip()

        soil_val = soil_enc.transform([soil])[0]
        crop_val = crop_enc.transform([crop])[0]

        data = np.array([[temp, hum, moist, soil_val, crop_val, n, k, p]])

        pred = model.predict(data)
        result = fert_enc.inverse_transform(pred)

        return result[0]

    except Exception as e:
        print("Prediction Error:", e)
        return "⚠ Unknown soil/crop type"

# 🏠 HOME
@app.route('/')
def home():
    return redirect('/login')

# 📝 REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect(os.path.join(BASE_DIR, "database.db"))
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p))
            conn.commit()
        except:
            conn.close()
            return "⚠ Username already exists"

        conn.close()
        return redirect('/login')

    return render_template("register.html")

# 🔑 LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    error = None

    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect(os.path.join(BASE_DIR, "database.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = u
            return redirect('/dashboard')
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

# 📊 DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# 🔮 PREDICT
@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect('/login')

    try:
        temp = float(request.form['temperature'])
        hum = float(request.form['humidity'])
        moist = float(request.form['moisture'])

        soil = request.form['soil']
        crop = request.form['crop']

        n = int(request.form['nitrogen'])
        k = int(request.form['potassium'])
        p = int(request.form['phosphorous'])

    except ValueError:
        return "❌ Invalid input! Please enter correct values."

    fertilizer = predict_fertilizer(temp, hum, moist, soil, crop, n, k, p)

    conn = sqlite3.connect(os.path.join(BASE_DIR, "database.db"))
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO soil_data
    (temperature, humidity, moisture, soil_type, crop_type, nitrogen, potassium, phosphorous, fertilizer)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (temp, hum, moist, soil, crop, n, k, p, fertilizer))

    conn.commit()
    conn.close()

    return render_template('result.html', fertilizer=fertilizer)

# 📋 VIEW
@app.route('/view')
def view():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect(os.path.join(BASE_DIR, "database.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM soil_data")
    data = cursor.fetchall()
    conn.close()

    return render_template('view.html', records=data)

# ✏️ EDIT
@app.route('/edit/<int:id>')
def edit(id):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "database.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM soil_data WHERE id=?", (id,))
    record = cursor.fetchone()
    conn.close()

    return render_template('edit.html', record=record)

# 🔄 UPDATE
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    try:
        temp = float(request.form['temperature'])
        hum = float(request.form['humidity'])
        moist = float(request.form['moisture'])

        soil = request.form['soil']
        crop = request.form['crop']

        n = int(request.form['nitrogen'])
        k = int(request.form['potassium'])
        p = int(request.form['phosphorous'])

    except ValueError:
        return "❌ Invalid input"

    fertilizer = predict_fertilizer(temp, hum, moist, soil, crop, n, k, p)

    conn = sqlite3.connect(os.path.join(BASE_DIR, "database.db"))
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE soil_data
    SET temperature=?, humidity=?, moisture=?, soil_type=?, crop_type=?, nitrogen=?, potassium=?, phosphorous=?, fertilizer=?
    WHERE id=?
    ''', (temp, hum, moist, soil, crop, n, k, p, fertilizer, id))

    conn.commit()
    conn.close()

    return redirect('/view')

# 🗑 DELETE
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "database.db"))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM soil_data WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/view')

# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# 🚀 RUN
if __name__ == "__main__":
    init_db()
    app.run(debug=True)