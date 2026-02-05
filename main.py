from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import time 
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Cache configuration
CACHE = {
    "data" : None,
    "last_updated" : None, 
    "cache_duration" : timedelta(minutes=15) 
}

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

def get_stock_details():
    """Fetch detailed stock information for all portfolio stocks"""

    # Check if cache is valid or not
    if CACHE["data"] and CACHE["last_updated"]:
        time_since_update = datetime.now()- CACHE["last_updated"]
        if time_since_update < CACHE["cache_duration"]:
            print("cached data")
            return CACHE["data"]
    
    results = []
    
    # Storing symbol sector and compnay name
    symbol_mapping = {}
    all_symbols = []

    for sector, stocks in PORTFOLIO_STOCKS.items():
        for symbol, company_name in stocks.items():
            symbol_mapping[symbol] = {
                "sector" : sector,
                "company_name" : company_name
            }
            all_symbols.append(symbol)
            print(all_symbols)

    tickers = yf.Tickers(" ".join(all_symbols))
    print(tickers)
    for symbol in all_symbols:
        try:
            ticker = tickers.tickers[symbol]
            info = ticker.info
            cashflow = ticker.cashflow
            
            # Get current market price
            hist = ticker.history(period="1d")
            cmp = round(hist['Close'].iloc[-1], 2) if not hist.empty else info.get('currentPrice')
            
            # Financial metrics
            market_cap = info.get('marketCap')
            pe_ratio = round(info.get('trailingPE'), 2) if info.get('trailingPE') else None
            revenue_ttm = info.get('totalRevenue')
            ebitda_ttm = info.get('ebitda')
            pat = info.get('netIncomeToCommon')
            
            # Calculate percentages
            ebitda_pct = round((ebitda_ttm / revenue_ttm * 100), 2) if ebitda_ttm and revenue_ttm else None
            pat_pct = round((pat / revenue_ttm * 100), 2) if pat and revenue_ttm else None
            
            # Cash flow data
            cfo_march_24 = None
            cfo_5_years = None
            free_cash_flow_5_years = None
            
            if not cashflow.empty:
                if 'Operating Cash Flow' in cashflow.index:
                    cfo_data = cashflow.loc['Operating Cash Flow']
                    if len(cfo_data) > 0:
                        cfo_march_24 = int(cfo_data.iloc[0])
                    if len(cfo_data) >= 5:
                        cfo_5_years = int(cfo_data.iloc[:5].sum())
                
                if 'Free Cash Flow' in cashflow.index:
                    fcf_data = cashflow.loc['Free Cash Flow']
                    if len(fcf_data) >= 5:
                        free_cash_flow_5_years = int(fcf_data.iloc[:5].sum())
            
            # Balance sheet data
            debt_to_equity = info.get('debtToEquity')
            book_value = round(info.get('bookValue'), 2) if info.get('bookValue') else None
            
            # Ratios
            price_to_sales = round(info.get('priceToSalesTrailing12Months'), 2) if info.get('priceToSalesTrailing12Months') else None
            cfo_to_ebitda = round((cfo_march_24 / ebitda_ttm), 2) if cfo_march_24 and ebitda_ttm else None
            cfo_to_pat = round((cfo_march_24 / pat), 2) if cfo_march_24 and pat else None
            price_to_book = round(info.get('priceToBook'), 2) if info.get('priceToBook') else None
            
            stock_data = {
                "sector": sector,
                "symbol": symbol,
                "company_name": company_name,
                "cmp": cmp,
                "market_cap": market_cap,
                "pe_ratio": pe_ratio,
                "latest_earnings": pat,
                "revenue_ttm": revenue_ttm,
                "ebitda_ttm": ebitda_ttm,
                "ebitda_percentage": ebitda_pct,
                "pat": pat,
                "pat_percentage": pat_pct,
                "cfo_march_24": cfo_march_24,
                "cfo_5_years": cfo_5_years,
                "free_cash_flow_5_years": free_cash_flow_5_years,
                "debt_to_equity": debt_to_equity,
                "book_value": book_value,
                "price_to_sales": price_to_sales,
                "cfo_to_ebitda": cfo_to_ebitda,
                "cfo_to_pat": cfo_to_pat,
                "price_to_book": price_to_book
            }
            
            results.append(stock_data)
            
        except Exception as e:
            results.append({
                "sector": sector,
                "symbol": symbol,
                "company_name": company_name,
                "error": str(e)
            })
    
    # Update the cache
    CACHE["data"] = results
    CACHE["last_updated"] = datetime.now()

    return results


@app.route('/api/stocks', methods=['GET'])
def get_all_stocks():
    """API endpoint to get all portfolio stocks data"""
    stocks_data = get_stock_details()
    return jsonify({
        "success": True,
        "total_stocks": len(stocks_data),
        "cached": CACHE["last_updated"] is not None,
        "cache_expires_in": int((CACHE["cache_duration"] - (datetime.now() - CACHE["last_updated"])).total_seconds()) if CACHE["last_updated"] else None,
        "last_updated": CACHE["last_updated"].isoformat() if CACHE["last_updated"] else None,
        "data": stocks_data
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Finance API is running",
        "cache_status": {
            "is_cached": CACHE["data"] is not None,
            "last_updated": CACHE["last_updated"].isoformat() if CACHE["last_updated"] else None
        }
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)