# Stock Price Tracker & Alert System 📈🚀

A Flask-based REST API that monitors live stock prices via the Alpha Vantage API, stores tracking data in an SQLite database, and instantly sends automated email notifications using the SMTP protocol when a stock drops below a user-defined threshold price.

## 🛠️ Tech Stack
- **Backend Framework:** Python, Flask
- **Database:** SQLite3
- **APIs:** Alpha Vantage API (Financial Market Data)
- **Email Protocol:** SMTP (`smtplib`, `email.mime`)
- **Environment Management:** `python-dotenv`

## ✨ Features
- **Dynamic Watchlist (POST `/stocks`):** Add a stock symbol and its custom alert threshold.
- **View Watchlist (GET `/stocks`):** Retrieve all currently monitored stocks with their internal IDs.
- **Delete Stock (DELETE `/stocks`):** Dynamically remove any stock from the watchlist.
- **Automated Alerts (GET `/check-alerts`):** Triggers a system scan that fetches real-time prices, logs them into a persistent `price_history` table, and fires a secure email alert if any threshold is breached.

## 🚀 How to Run Locally

1. Open your terminal in the project folder and install the required packages:
pip install flask requests python-dotenv

2. Create a file named ".env" in the root directory (same folder where app.py is located).

3. Paste the following lines inside the ".env" file and replace with your actual values:
EMAIL=your_email
EMAIL_PASSWORD=your_16_digit_google_app_password
API_KEY=your_alpha_vantage_api_key

4. Run the Flask server:
python app.py

5. Open Postman or your browser and use these endpoints on http://127.0.0.1:5000/
- GET  /stocks          (To view your watchlist)
- POST /stocks          (To add a stock with JSON body: {"symbol": "TSLA", "threshold": 300.0})
- GET  /check-alerts    (To fetch live prices and trigger automated email alerts)
