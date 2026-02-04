
import yfinance as yf

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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)