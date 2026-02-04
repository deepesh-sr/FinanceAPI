from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

PORTFOLIO_STOCKS = {
    "Financial Sector": {
        "HDFCBANK.NS": "HDFC Bank",
        "BAJFINANCE.NS": "Bajaj Finance",
        "ICICIBANK.NS": "ICICI Bank",
        "BAJAJHFL.NS": "Bajaj Housing",
        "SAVAFINANCIAL.BO": "Savani Financials",
        "SBILIFE.NS": "SBI Life",
    },
    "Tech Sector": {
        "AFFLE.NS": "Affle India",
        "LTIM.NS": "LTI Mindtree",
        "KPITTECH.NS": "KPIT Tech",
        "TATATECH.NS": "Tata Tech",
        "BLSE.NS": "BLS E-Services",
        "TANLA.NS": "Tanla Platforms",
        "INFY.NS": "Infosys",
        "HAPPSTMNDS.NS": "Happiest Minds",
    },
    "Consumer Sector": {
        "DMART.NS": "DMart",
        "TATACONSUM.NS": "Tata Consumer",
        "PIDILITIND.NS": "Pidilite",
    },
    "Power Sector": {
        "TATAPOWER.NS": "Tata Power",
        "KPIGREEN.NS": "KPI Green",
        "SUZLON.NS": "Suzlon",
        "GENSOL.NS": "Gensol",
    },
    "Pipe Sector": {
        "HARIOMPIPE.NS": "Hariom Pipes",
        "ASTRAL.NS": "Astral",
        "POLYCAB.NS": "Polycab",
    },
    "Others": {
        "CLEAN.NS": "Clean Science",
        "DEEPAKNTR.NS": "Deepak Nitrite",
        "FINEORG.NS": "Fine Organic",
        "GRAVITA.NS": "Gravita",
        "EASEMYTRIP.NS": "Easemytrip",
    }
}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Finance API is running"
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)