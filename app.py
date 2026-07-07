import sqlite3, requests, smtplib, os
from flask import Flask, jsonify, request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from env import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return "Stock Tracker API is running!"

def init_db():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()

    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stocks(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    threshold REAL NOT NULL
                    )
                ''')
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS price_history(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    datetime DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
    conn.commit()
    conn.close()

def get_stocks(symbol):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
    response=requests.get(url)
    data=response.json()
    if "Global Quote" in data and "05. price" in data["Global Quote"]:
            price=float(data["Global Quote"]["05. price"])
            return price
    else:
        return None

@app.route('/price/<symbol>')
def check_price(symbol):
    price = get_stocks(symbol)
    if price is not None:
        return jsonify({"symbol": symbol, "price": price})
    return jsonify({"error": "price not found"}), 404

@app.route('/stocks', methods=['POST'])
def add_stock():
    data = request.get_json()
    if not data or 'symbol' not in data or 'threshold' not in data:
        return jsonify({"error": "Symbol and threshold required!"}), 400
    symbol=data['symbol'].upper()
    threshold  =float(data['threshold'])
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()    
    cursor.execute("INSERT INTO stocks (symbol, threshold) VALUES (?, ?)", (symbol, threshold))
    conn.commit()
    conn.close()
    return jsonify({"message": f"{symbol} added"}), 201

@app.route('/stocks', methods=['GET'])
def get_all_stocks():
    conn = sqlite3.connect('stocks.db')
    cursor  =conn.cursor()
    cursor.execute("SELECT id, symbol, threshold FROM stocks")
    rows=  cursor.fetchall()
    conn.close()
    stocks = []
    for row in rows:
        stocks.append({"id": row[0], "symbol": row[1], "threshold": row[2]})
    return jsonify(stocks), 200

@app.route('/stocks/<int:stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM stocks WHERE id = ?", (stock_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "stock not found"}), 404
    cursor.execute("DELETE FROM stocks WHERE id = ?", (stock_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Stock with id {stock_id} successfully deleted"}), 200

def send_alert(symbol, current_price, threshold):
    subject = f"Price ALert: {symbol} dropped below {threshold}!"
    body = f"Symbol: {symbol}\nPrice: ${current_price}\nThreshold: {threshold}"
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try: 
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False
    
@app.route('/check-alerts', methods=['GET'])
def check_alerts():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, symbol, threshold FROM stocks")
    stocks = cursor.fetchall()
    alerts_sent = []
    for stock in stocks:
        stock_id, symbol, threshold = stock
        current_price = get_stocks(symbol)
        if current_price is None: continue
        cursor.execute("INSERT INTO price_history (symbol, price) VALUES (?, ?)", (symbol, current_price))
        if current_price<threshold:
            if send_alert(symbol, current_price, threshold):
                alerts_sent.append(symbol)
    conn.commit()
    conn.close()
    return jsonify({"message": "Alert check complete", "alerts_sent": alerts_sent}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)